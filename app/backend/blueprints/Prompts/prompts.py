from quart import Blueprint, jsonify, request, current_app
from decorators import authenticated, group_access, error_response
from typing import Dict, Any
from config import CONFIG_AUTH_CLIENT, CONFIG_DB_CLIENT
from db.service.db_client import BaseClient as BaseDbClient
import time

prompts_bp = Blueprint("prompts", __name__)

@prompts_bp.route("/user/prompts/list", methods=["POST"])
@group_access(min_role='admin', group_required=True)
async def list_user_prompts(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    id = request_json.get('id', None)
    title = request_json.get('title', None)
    # if not id and not title:
    #     return jsonify({"error": "id or title is required"}), 400
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        prompts = await db_client.list_user_prompts(id, title)
        return jsonify({"prompts": prompts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompts_bp.route("/user/prompts/create", methods=["POST"])
@group_access(min_role='admin', group_required=True)
async def create_user_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    title = request_json.get('title', None)
    text = request_json.get('text', None)
    
    if not title or not text:
        return jsonify({"error": "title and text are required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        user_id = auth_claims.get('oid', None)
        prompt = await db_client.create_user_prompt(user_id, title, text)
        return jsonify({"prompt": prompt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompts_bp.route("/user/prompts/update", methods=["POST"])
@group_access(min_role='admin', group_required=True)
async def update_user_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    title = request_json.get('title', None)
    text = request_json.get('text', None)
    
    if not prompt_id or not title or not text:
        return jsonify({"error": "id, title and text are required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        prompt = await db_client.update_user_prompt(prompt_id, title, text)
        if not prompt:
            return jsonify({"error": "Prompt not found"}), 404
        return jsonify({"prompt": prompt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompts_bp.route("/user/prompts/delete", methods=["POST"])
@group_access(min_role='admin', group_required=True)
async def delete_user_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    
    if not prompt_id:
        return jsonify({"error": "id is required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        user_prompt = await db_client.list_user_prompts(id=prompt_id)
        if not user_prompt or len(user_prompt) == 0:
            return jsonify({"error": "Prompt not found"}), 404
        if user_prompt[0]['active']:
            return jsonify({"error": "Cannot delete an active prompt"}), 400
        success = await db_client.delete_user_prompt(prompt_id)
        if not success:
            return jsonify({"error": "Prompt not found"}), 404
        return jsonify({"message": "Prompt deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@prompts_bp.route('/user/prompts/set-default', methods=['POST'])
@group_access(min_role='admin', group_required=True)
async def set_default_user_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    active = request_json.get('active', True)
    
    if not prompt_id or active is None:
        return jsonify({"error": "id and status are required"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        user_prompt = await db_client.list_user_prompts(id=prompt_id)
        if user_prompt and len(user_prompt) > 0:
            user_prompt = user_prompt[0]
        if not user_prompt:
            return jsonify({"error": "Prompt not found"}), 404

        if active:
            await db_client.deactivate_all_user_prompts()
            await db_client.update_user_prompt_kwargs(prompt_id, active=True)
        elif not active:
            if user_prompt['active']:
                return jsonify({"error": "Cannot deactivate the an active prompt"}), 400
            else:
                db_client.update_user_prompt_kwargs(prompt_id, active=False)
        return jsonify({"message": "Prompt set as default successfully", "status": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

