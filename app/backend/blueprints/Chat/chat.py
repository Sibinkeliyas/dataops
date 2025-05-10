from quart import Blueprint, jsonify, request, current_app, make_response, Response,stream_with_context
from typing import Dict, Any, AsyncGenerator, cast
from config import CONFIG_CHAT_APPROACH, CONFIG_CHAT_VISION_APPROACH, CONFIG_OPENAI_CLIENT, CONFIG_DB_CLIENT
from approaches.approach import Approach
from core.authentication import hash_uuid
from history.utils import generate_title
from db.service.db_client import BaseClient as BaseDbClient
import uuid
import os
import json
import dataclasses
from decorators import authenticated, group_access, error_response
from error import error_dict, error_response
import asyncio
import logging
import time

chat_bp = Blueprint('chat', __name__)


async def format_as_ndjson(r: AsyncGenerator[dict, None],current_app) -> AsyncGenerator[str, None]:
    try:
        async for event in r:
            yield json.dumps(event, ensure_ascii=False, cls=JSONEncoder) + "\n"
    except Exception as error:
        current_app.config['logging'].exception("Exception while generating response stream: %s", error)
        yield json.dumps(error_dict(error))


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)

async def handle_db_operations(user_id: str, group_id: str, request_json: Dict[str, Any], result: Dict[str, Any], app, datetime=None) -> str:
    hashed_userid = await hash_uuid(user_id)
    db_client: BaseDbClient = app.config[CONFIG_DB_CLIENT]

    if db_client:
        conversation_id = None
        if not request_json.get('conversation_id', None):
            title = await generate_title(
                model_client=app.config[CONFIG_OPENAI_CLIENT],
                model_name=os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
                conversation_messages=request_json["messages"],
            )
            conversation = await db_client.create_conversation(
                user_id=hashed_userid,
                title=title,
                group_id=group_id,
                datetime=datetime
            ) if db_client.async_mode else db_client.create_conversation(
                user_id=hashed_userid,
                title=title,
                datetime=datetime
            )
            conversation_id = conversation['id']
        
        conversation_id = conversation_id if conversation_id else request_json.get('conversation_id')

        message_list = request_json.get('messages', [])
        last_user_msg = None 
        if len(message_list) > 0:
            last_user_msg = message_list[-1]
            if last_user_msg.get('role') == 'assistant':
                last_user_msg = message_list[-2]
        assistant_message = result.get('message', '')
        if last_user_msg and assistant_message:
            _,assistant_message = await asyncio.gather(
                db_client.create_message(
                    conversation_id=conversation_id,
                    user_id=hashed_userid,
                    input_message=last_user_msg,
                    uuid=str(uuid.uuid4()),
                    datetime=datetime,
                ),
                db_client.create_message(
                    conversation_id=conversation_id,
                    user_id=hashed_userid,
                    input_message=assistant_message,
                    uuid=str(uuid.uuid4()),
                    datetime=datetime,
                    context=result.get('context', {})
                )
            )
            
        return conversation_id,assistant_message['id']
    return None

@chat_bp.route("/chat", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def chat(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims

    user_id = auth_claims.get('oid', None) if auth_claims else None
    datetime = request_json.get('datetime', None)
    # group_id = context.get('overrides', {}).get('current_group', False)
    group_id = request_json.get('group_id', None)
    if group_id:
        context['overrides']['current_group'] = group_id
        context['overrides']['prioritize_filter'] = {'group_ids': [group_id]}
    try:
        use_gpt4v = False
        approach: Approach
        if use_gpt4v and CONFIG_CHAT_VISION_APPROACH in current_app.config:
            approach = current_app.config[CONFIG_CHAT_VISION_APPROACH]
        else:
            approach = current_app.config[CONFIG_CHAT_APPROACH]

        result = await approach.run(
            request_json["messages"],
            context=context,
            session_state=request_json.get("session_state"),
        )
        # print('after chat')
        if user_id:
            conversation_id,assistant_message_id = await handle_db_operations(user_id, group_id, request_json, result, current_app, datetime)
            if conversation_id:
                result['conversation_id'] = conversation_id
                result['message_id'] = assistant_message_id

        return jsonify(result)
    except Exception as error:
        current_app.logger.exception("Exception in /chat: %s", error)
        return jsonify(error_dict(error)), 400
    
@chat_bp.route("/feedback", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def feedback(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    message_id = request_json.get('message_id', None)
    feedback = request_json.get('feedback', None)
    if not isinstance(feedback,bool) and feedback is not None:
        return jsonify({"error": "feedback must be a boolean or null"}), 400
    try:

        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            oid = auth_claims.get('oid', None)
            hashed_userid = await hash_uuid(oid)
            await db_client.update_message_feedback(message_id = message_id, feedback = feedback, user_id = hashed_userid)
            return jsonify({"status": True, "message": "Feedback updated successfully"}), 200
        else:
            return jsonify({"error": "Unable to connect to DB"}), 500
    except Exception as error:
        current_app.logger.exception("Exception in /feedback: %s", error)
        return jsonify(error_dict(error)), 400


@chat_bp.route("/conversation/fetch", methods=['POST'])
@group_access(min_role='member', group_required=False)
async def conversation_history(auth_claims: Dict[str, Any]):
    # start_time = time.time()
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims

    user_id = auth_claims.get('oid', None) if auth_claims else None
    group_id = request_json.get('group_id', None)
    continuation_token = request_json.get('continuation_token',None)


    conversation_id = request_json.get('conversation_id', None)
    # end_time = time.time()
    # current_app.logger.info(f"conversation/fetch before db call took {end_time - start_time:.2f} seconds")
    try:
        # start_time = time.time()
        if conversation_id or user_id:
            db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
            if db_client:
                if conversation_id and user_id:
                    hashed_userid = await hash_uuid(user_id)
                    results = await db_client.get_conversation(
                        user_id=hashed_userid,
                        conversation_id=conversation_id
                    ) if db_client.async_mode else db_client.get_conversation(
                        user_id=hashed_userid,
                        conversation_id=conversation_id
                    )
                    # end_time = time.time()
                    # current_app.logger.info(f"conversation/fetch after db call took {end_time - start_time:.2f} seconds")
                    return jsonify(results)
                elif user_id and not conversation_id:
                    hashed_userid = await hash_uuid(user_id)
                    limit = request_json.get("limit", 100)
                    results,continuation_token = await db_client.get_conversations(
                        user_id=hashed_userid,
                        group_id=group_id,
                        limit=limit,
                        continuation_token=continuation_token
                    ) if db_client.async_mode else db_client.get_conversations(
                        user_id=hashed_userid,
                        limit=limit,
                        continuation_token=continuation_token
                    )
                    # end_time = time.time()
                    # current_app.logger.info(f"conversation/fetch after db call took {end_time - start_time:.2f} seconds")
                    # return jsonify(results)
                    # results['continuation_token'] = continuation_token
                    # current_app.logger.info(f"continuation_token: {continuation_token}")
                    return jsonify({"result" : results, "continuation_token" : continuation_token})
                else:
                    return jsonify({'error': 'Missing/Invalid user_id or conversation_id'})
            else:
                return jsonify({'error': 'Unable to connect to DB'})
        else:        
            return jsonify({'error': 'Missing/Invalid user_id or conversation_id'})
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@chat_bp.route("/messages/fetch", methods=['POST'])
@group_access(min_role='member', group_required=False)
async def message_history(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims

    user_id = auth_claims.get('oid', None) if auth_claims else None
    conversation_id = request_json.get('conversation_id', None)

    try:
        if conversation_id and user_id:
            hashed_userid = await hash_uuid(user_id)
            db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
            if db_client:
                results = await db_client.get_messages(
                    user_id=hashed_userid,
                    conversation_id=conversation_id
                ) if db_client.async_mode else db_client.get_messages(
                    user_id=hashed_userid,
                    conversation_id=conversation_id
                )
                return jsonify(results)
            else:
                return jsonify({'error': 'Unable to connect to DB'})
        else:
            return jsonify({'error': 'Missing/Invalid user_id or conversation_id'})
    except Exception as error:
        return jsonify({"error": str(error)}), 500



@chat_bp.route("/chat/stream", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def chat_stream(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims
    user_id = auth_claims.get('oid', None) if auth_claims else None
    # group_id = context.get('overrides', {}).get('current_group', False)
    group_id = request_json.get('group_id', None)
    if group_id:
        context['overrides']['current_group'] = group_id
        context['overrides']['prioritize_filter'] = {'group_ids': [group_id]}
    datetime = request_json.get('datetime', None)
   
    try:
        use_gpt4v = context.get("overrides", {}).get("use_gpt4v", False)
        approach: Approach
        if use_gpt4v and CONFIG_CHAT_VISION_APPROACH in current_app.config:
            approach = cast(Approach, current_app.config[CONFIG_CHAT_VISION_APPROACH])
        else:
            approach = cast(Approach, current_app.config[CONFIG_CHAT_APPROACH])

        session_state = request_json.get("session_state")
        app = current_app._get_current_object()

        result = await approach.run_stream(
            request_json["messages"],
            context=context,
            session_state=session_state,
        )

        async def format_and_store():
            content_list = []
            context = None
            conversation_id = None
            try:
                # Start processing the stream
                async for event in result:
                    if 'delta' in event and 'content' in event['delta']:
                        content = event['delta']['content']
                        content_list.append(content if isinstance(content, str) else '')
                    if 'delta' in event and 'context' in event['delta']:
                        # context.append(event['delta']['context'])
                        context = event['delta']['context']
                    if 'context' in event:
                        context = event['context']
                        # context.append(event['delta']['context'])
                    yield json.dumps(event, ensure_ascii=False, cls=JSONEncoder) + "\n"
            
            # After streaming is complete, handle DB operations
                if user_id:
                    accumulated_response = ''.join(content_list)
                    conversation_id,assistant_message_id = await handle_db_operations(
                        user_id,
                        group_id,
                        request_json,
                        {'message': {'role': 'assistant', 'content': accumulated_response}, 'context': context},
                        app,
                        datetime
                    )
                    
                    # Yield the conversation_id early if it was successfully created
                    if conversation_id:
                        yield json.dumps({"conversation_id": conversation_id, "message_id": assistant_message_id}, ensure_ascii=False) + "\n"
                        
            except Exception as error:
                # print(error)
                # current_app.logger.exception("Exception while generating response stream: %s", error)
                yield json.dumps(error_dict(error))
                
        response = await make_response(format_and_store())
        response.timeout = None  # type: ignore
        response.mimetype = "application/json-lines"
        return response
    except Exception as error:
        # print(error)
        current_app.logger.exception("Exception in /chat/stream: %s", error)
        return error_response(error, "/chat/stream")
        # return jsonify(error_dict(error)), 400

        # return make_response(error_dict(error)), 400
        # return jsonify({'message' : {'role' : "assistant", 'content' : error.args[0]}}), 400


@chat_bp.route("/conversation/delete", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def delete_conversation(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    conversation_id = request_json.get('conversation_id', None)
    if not conversation_id:
        return jsonify({"error": "conversation_id is required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        try:
            hashed_userid = await hash_uuid(auth_claims.get('oid', None))
            await db_client.delete_conversation(hashed_userid, conversation_id)
            await db_client.delete_messages(conversation_id, hashed_userid)
            return jsonify({"status": True, "message": "Conversation deleted successfully"}), 200
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Unable to connect to DB"}), 500
    

@chat_bp.route("/conversation/delete/all", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def delete_all_conversations(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    group_id = request_json.get('group_id', None)

    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        try:
            hashed_userid = await hash_uuid(auth_claims.get('oid', None))
            await db_client.delete_conversations(hashed_userid, group_id)
            return jsonify({"status": True, "message": "All conversations deleted successfully"}), 200
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Unable to connect to DB"}), 500


@chat_bp.route("/conversation/update", methods=["POST"])
@group_access(min_role='member', group_required=False)
async def update_conversation(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    conversation_id = request_json.get('conversation_id', None)
    title = request_json.get('title', None)
    if not conversation_id or not title:
        return jsonify({"error": "conversation id and title are required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        try:
            hashed_userid = await hash_uuid(auth_claims.get('oid', None))
            await db_client.update_conversation(conversation_id, hashed_userid, title)
            return jsonify({"status": True, "message": "Conversation updated successfully"}), 200
        except Exception as error:
            return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Unable to connect to DB"}), 500


