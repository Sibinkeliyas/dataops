import dataclasses
import io
import json
import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Union, cast
import uuid
import base64
import re
from pydantic import BaseModel

from azure.cognitiveservices.speech import (
    ResultReason,
    SpeechConfig,
    SpeechSynthesisOutputFormat,
    SpeechSynthesisResult,
    SpeechSynthesizer,
)
from azure.storage.filedatalake.aio import DataLakeDirectoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from azure.identity import ClientSecretCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.storage.blob.aio import ContainerClient, BlobClient, BlobServiceClient
from azure.storage.blob.aio import StorageStreamDownloader as BlobDownloader
from azure.storage.filedatalake.aio import FileSystemClient
from azure.storage.filedatalake.aio import StorageStreamDownloader as DatalakeDownloader
from openai import AsyncAzureOpenAI, AsyncOpenAI
# from history.CosmosDbService import CosmosConversationClient
from db.service.cosmos.cosmos_client import CosmosConversationClient
from db.service.cosmos.cosmos_document_client import CosmosDocumentClient
from db.service.sql.sql_client import SqlClient
from db.service.db_client import BaseClient as BaseDbClient
from history.utils import generate_title
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
)

# from azure.identity import ClientSecretCredential
# from azure.graphrbac.graph_rbac_management_client import GroupsOperations
from msgraph.generated.models.group import Group 
from msgraph import GraphServiceClient
# from azure.identity import DeviceCodeCredential
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.reference_create import ReferenceCreate
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
import psutil
from decorators import get_group_id_from_request
from quart import (
    Blueprint,
    Quart,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
    send_file,
    send_from_directory,
    g,

)
from quart_cors import cors
from alembic.config import Config
from approaches.approach import Approach
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from approaches.chatreadretrievereadvision import ChatReadRetrieveReadVisionApproach
from approaches.retrievethenread import RetrieveThenReadApproach
from approaches.retrievethenreadvision import RetrieveThenReadVisionApproach
from config import (
    CONFIG_ASK_APPROACH,
    CONFIG_ASK_VISION_APPROACH,
    CONFIG_AUTH_CLIENT,
    CONFIG_BLOB_CONTAINER_CLIENT,
    CONFIG_CHAT_APPROACH,
    CONFIG_CHAT_VISION_APPROACH,
    CONFIG_CREDENTIAL,
    CONFIG_GPT4V_DEPLOYED,
    CONFIG_INGESTER,
    CONFIG_OPENAI_CLIENT,
    CONFIG_SEARCH_CLIENT,
    CONFIG_SEMANTIC_RANKER_DEPLOYED,
    CONFIG_SPEECH_INPUT_ENABLED,
    CONFIG_SPEECH_OUTPUT_AZURE_ENABLED,
    CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED,
    CONFIG_SPEECH_SERVICE_ID,
    CONFIG_SPEECH_SERVICE_LOCATION,
    CONFIG_SPEECH_SERVICE_TOKEN,
    CONFIG_SPEECH_SERVICE_VOICE,
    CONFIG_USER_BLOB_CONTAINER_CLIENT,
    CONFIG_USER_UPLOAD_ENABLED,
    CONFIG_VECTOR_SEARCH_ENABLED,
    CONFIG_DB_CLIENT,
    CONFIG_TASK_DB_CLIENT,
)
from prompts.utils import inject_variables
from core.authentication import AuthenticationHelper,hash_uuid
from decorators import authenticated, authenticated_path, group_access
from error import error_dict, error_response
from prepdocs import (
    clean_key_if_exists,
    setup_embeddings_service,
    setup_file_processors,
    setup_search_info,
)
from prepdocslib.filestrategy import UploadUserFileStrategy
from prepdocslib.listfilestrategy import File
from PIL import Image
from azure.storage.filedatalake import generate_file_sas, FileSystemSasPermissions
from datetime import datetime, timedelta
from io import BytesIO
from azure.storage.blob.aio import BlobServiceClient
from blueprints.Chat.chat import chat_bp
from blueprints.Groups.groups import groups_bp
from blueprints.Upload.upload import upload_bp
from blueprints.Prompts.prompts import prompts_bp
from blueprints.Groups.tasks import tasks_bp
from blueprints.UserManagement.usermanagement import usermanagement_bp

bp = Blueprint("routes", __name__, static_folder="static")
# Fix Windows registry issue with mimetypes
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")


@bp.route("/")
async def index():
    return await bp.send_static_file("index.html")


@bp.route("/document-management")
async def document_management():
    return await bp.send_static_file("index.html")

@bp.route("/ask-queries")
async def ask_queries():
    return await bp.send_static_file("index.html")


# Empty page is recommended for login redirect to work.
# See https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-browser/docs/initialization.md#redirecturi-considerations for more information
@bp.route("/redirect")
async def redirect():
    return ""


@bp.route("/favicon.ico")
async def favicon():
    return await bp.send_static_file("favicon.ico")


@bp.route("/assets/<path:path>")
async def assets(path):
    return await send_from_directory(Path(__file__).resolve().parent / "static" / "assets", path)


@bp.route("/content/<path>",methods=['POST','GET'])
@authenticated_path
async def content_file(path: str, auth_claims: Dict[str, Any]):
    """
    Serve content files from blob storage from within the app to keep the example self-contained.
    *** NOTE *** if you are using app services authentication, this route will return unauthorized to all users that are not logged in
    if AZURE_ENFORCE_ACCESS_CONTROL is not or false, logged in users can access all files regardless of access control
    if AZURE_ENFORCE_ACCESS_CONTROL is set to true, logged in users can only access files they have access to
    This is also slow and memory hungry.
    """
    # Remove page number from path, filename-1.txt -> filename.txt
    # This shouldn't typically be necessary as browsers don't send hash fragments to servers
    if path.find("#page=") > 0:
        path_parts = path.rsplit("#page=", 1)
        path = path_parts[0]
    json_data = await request.get_json()
    group_id = json_data.get('group_id', None)
    current_app.logger.info("Opening file %s", path)
    blob_container_client: ContainerClient = current_app.config[CONFIG_BLOB_CONTAINER_CLIENT]
    blob: Union[BlobDownloader, DatalakeDownloader]
    try:
        blob = await blob_container_client.get_blob_client(path).download_blob()
    except ResourceNotFoundError:
        current_app.logger.info("Path not found in general Blob container: %s", path)
        if current_app.config[CONFIG_USER_UPLOAD_ENABLED]:
            try:
                user_oid = auth_claims["oid"] if auth_claims and not group_id else group_id
                user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
                user_directory_client: FileSystemClient = user_blob_container_client.get_directory_client(user_oid)
                file_client = user_directory_client.get_file_client(path)
                blob = await file_client.download_file()
            except ResourceNotFoundError:
                current_app.logger.exception("Path not found in DataLake: %s", path)
                abort(404)
        else:
            abort(404)
    if not blob.properties or not blob.properties.has_key("content_settings"):
        abort(404)
    mime_type = blob.properties["content_settings"]["content_type"]
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    blob_file = io.BytesIO()
    await blob.readinto(blob_file)
    blob_file.seek(0)
    return await send_file(blob_file, mimetype=mime_type, as_attachment=False, attachment_filename=path)


@bp.route("/ask", methods=["POST"])
@authenticated
async def ask(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims
    try:
        use_gpt4v = context.get("overrides", {}).get("use_gpt4v", False)
        approach: Approach
        if use_gpt4v and CONFIG_ASK_VISION_APPROACH in current_app.config:
            approach = cast(Approach, current_app.config[CONFIG_ASK_VISION_APPROACH])
        else:
            approach = cast(Approach, current_app.config[CONFIG_ASK_APPROACH])
        r = await approach.run(
            request_json["messages"], context=context, session_state=request_json.get("session_state")
        )
        return jsonify(r)
    except Exception as error:
        return error_response(error, "/ask")


@bp.route('/groups/remove',methods=["POST"])
@group_access(min_role='owner',group_required=True)
async def delete_group(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    user_id = auth_claims["oid"]

    group_id = request_json.get('group_id',None)

    if not group_id:
        return jsonify({'error' : 'Invalid/Missing group id'}),400

    # group_role = auth_claims.get('')

    try:
        # credentials = DeviceCodeCredential(client_id=os.getenv('AZURE_SERVER_APP_ID'),tenant_id=os.getenv('AZURE_TENANT_ID'))

        credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))

        # graph_client = GraphServiceClient(credentials=credentials,scopes=['Group.ReadWrite.All'
        #                                                                                 'Group.Read.All',
        #                                                                                 'Group.Create'])

        scopes = [
            'https://graph.microsoft.com/.default'
        ]

        graph_client = GraphServiceClient(credentials=credentials)

        response = await graph_client.groups.by_group_id(group_id=group_id).delete()

        db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            await db_client.delete_group(group_id=group_id,user_id=user_id)
        else:
            return jsonify({"error" : "Could not establish connection with database"}), 400
        

        return jsonify({"status" : True}),200
    except ODataError as error:
        return jsonify({'error' : error.error.message}),400

    except Exception as e:
        return jsonify({'error' : str(e )}),400
        

@bp.route('/groups/create', methods=['POST'])
# @authenticated
@group_access(min_role='admin',group_required=False)
async def create_group(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    # print('hi')  
    request_json = await request.get_json()
    user_id = auth_claims['oid']
    display_name = request_json.get('display_name',None)
    description = request_json.get('group_description',None)
    group_type = request_json.get('group_type','default')
    max_storage_size = request_json.get('max_storage_size',5120)
    max_file_size = request_json.get('max_file_size',50)

    if max_file_size > max_storage_size:
        return jsonify({"error" : "Max file size cannot be greater than max storage size"}),400
    

        
    try:
        # credentials = DeviceCodeCredential(client_id=os.getenv('AZURE_SERVER_APP_ID'),tenant_id=os.getenv('AZURE_TENANT_ID'))

        credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))

        # graph_client = GraphServiceClient(credentials=credentials,scopes=['Group.ReadWrite.All'
        #                                                                                 'Group.Read.All',
        #                                                                                 'Group.Create'])

        scopes = [
            'https://graph.microsoft.com/.default'
        ]

        graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)
        
        group_request = Group(
            description=description,
            display_name=display_name,
            mail_enabled=False,
            security_enabled=True,
            mail_nickname='NotSet',
            group_types=[]

        )
        # result = await graph_client.groups.post(group_request)
        result = await graph_client.directory.administrative_units.by_administrative_unit_id(os.getenv('AZURE_ADMINISTRATIVE_UNIT','')).members.post(group_request);

        try:
            if result:
                db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]

                if db_client:
                    db_response = await db_client.create_group(group_id=result.id,
                                        group_display_name=display_name,
                                        group_description=description,
                                        group_type=group_type,
                                        user_id=user_id,
                                        max_storage_size=max_storage_size,
                                        max_file_size=max_file_size
                                        )
                    try:
                        prompts = await db_client.get_prompts(id='default')
                        if not prompts or len(prompts) > 0:
                            variables = {'group_name': display_name, 'additional_instructions': 'ensure that the above instructions are followed strictly'}
                            await db_client.create_workspace_prompt(base_prompt_id='default',
                                                                    variables={'group_name': display_name, 'additional_instructions': 'ensure that the above instructions are followed strictly'},
                                                                text=f'''Assistant helps the {variables['group_name']} employees with their queries and questions. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. But then ask if the user if they are interested in searching for the AI model's general knowledge database or that they can upload documents to the chat by using the menu located on the top right corner of the screen. 
Annotate/reference these answers as coming from "LLM Model Knowledge" source document for content generated from the LLM Model's knowledge.
If asking a clarifying question to the user would help, ask the question.
User might also ask questions related to the conversation. You'll be provided the chat history from which you can refer and answer the question.
For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf]. If there are no sources, mention it's coming from your LLM Model Knowledge as the source.

Additional instructions:
-----------------------------------
{variables['additional_instructions']}
-----------------------------------
#''',
                                                                group_id=result.id,
                                                                active=True)
                    except Exception as e:
                        current_app.logger.error(f"Error creating workspace prompt: {str(e)}")
                    
        except Exception as db_error:
            return jsonify({
                'Error' : str(db_error)
            })
        return jsonify({"group" : db_response})
    except Exception as e:
        return jsonify({"error" : str(e)}),400


@bp.route('/groups/update', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def update_group(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    group_id = request_json.get('group_id', None)
    max_storage_size = request_json.get('max_storage_size', None)
    max_file_size = request_json.get('max_file_size', None)
    group_name = request_json.get('name', None)
    group_description = request_json.get('description', None)

    if not group_id:
        return jsonify({"error": "Missing/Invalid group id"}), 400
    
    if max_file_size is not None and max_storage_size is not None and max_file_size > max_storage_size:
        return jsonify({"error": "Max file size cannot be greater than max storage size"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            # Only keep the keys if any values are there
            group_args = {k: v for k, v in {
                'group_id': group_id,
                'maxStorageSize': max_storage_size,
                'maxFileSize': max_file_size,
                'groupName': group_name,
                'groupDescription': group_description
            }.items() if v is not None}
            
            # Update Azure group if name or description is provided
            await update_azure_group(group_id, group_name, group_description)
            
            # Update the group in the database
            await db_client.update_group(**group_args)
            
            # Fetch the updated group information
            updated_group = await db_client.get_groups(group_id=group_id)
            if updated_group:
                return jsonify({"group": updated_group[0]}), 200
            else:
                return jsonify({"error": "Failed to fetch updated group information"}), 500
        else:
            return jsonify({"error": "Unable to connect to DB"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

async def update_azure_group(group_id: str, group_name: str = None, group_description: str = None):
    try:
        credentials = ClientSecretCredential(
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_SERVER_APP_ID'),
            client_secret=os.getenv('AZURE_SERVER_APP_SECRET')
        )
        
        graph_client = GraphServiceClient(credentials=credentials)
        
        update_body = Group()
        update_needed = False

        if group_name is not None:
            update_body.display_name = group_name
            update_needed = True

        if group_description is not None:
            update_body.description = group_description
            update_needed = True
        
        if update_needed:
            await graph_client.groups.by_group_id(group_id).patch(update_body)
    
    except Exception as e:
        current_app.logger.error(f"Error updating Azure group: {str(e)}")
        raise

@bp.route('/groups/fetch', methods=['POST'])
@group_access(min_role='member', group_required=True)
async def fetch_group(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()

    context = request_json.get("context", {})
    context["auth_claims"] = auth_claims

    try:
        group_id = request_json.get('group_id', None)
        if not group_id:
            return jsonify({"error": "Missing/Invalid group id"}), 400
        
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.get_groups(group_id=group_id)
            if response:
                group_info = response[0]
                
                # group_info['groupLogoUrl'] = None
            return jsonify({'group': group_info})
        else:
            return jsonify({'error': 'Unable to connect to DB'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# @bp.route('/groups/upload', methods=['POST'])
# @group_access(min_role='owner',group_required=True)
# async def upload_group_logo(auth_claims: dict[str, Any]):
#     request_files = await request.files
#     request_form = await request.form
#     if "file" not in request_files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request_files.getlist("file")[0]
#     group_id = request_form.get('group_id')
#     file_size = int(request_form.get('file_size', 0))

#     if not group_id:
#         return jsonify({"error": "Group id is required"}), 400

#     # Check file type
#     allowed_extensions = {'png', 'jpg', 'jpeg'}
#     file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
#     if file_extension not in allowed_extensions:
#         return jsonify({"error": "Invalid file type. Only PNG, JPG, and JPEG are allowed"}), 400

#     # Verify file content
#     try:
#         img = Image.open(file.stream)
#         img.verify()
#         file.stream.seek(0)  # Reset file pointer
#     except Exception:
#         return jsonify({"error": "Invalid image file"}), 400

#     # Check group storage limits
#     db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
#     try:
#         group_info = await db_client.get_groups(group_id=group_id)
#         if not group_info:
#             return jsonify({"error": "Group not found"}), 404
        
#         group_info = group_info[0]  # Assuming get_groups returns a list
#         max_storage_size = group_info.get('maxStorageSize', 5) * 1024 * 1024  # Convert MB to bytes
#         max_file_size = group_info.get('maxFileSize', 1) * 1024 * 1024  # Convert MB to bytes
        
#         blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
#         group_directory_client = blob_container_client.get_directory_client(group_id)
        
#         try:
#             await group_directory_client.get_directory_properties()
#             current_storage_size = await get_group_uploads_size(blob_container_client, group_id)
#         except ResourceNotFoundError:
#             current_storage_size = 0

#         if file_size > max_file_size:
#             return jsonify({"error": f"File size exceeds the maximum allowed size of {max_file_size / (1024 * 1024):.2f} MB"}), 400

#         if current_storage_size + file_size > max_storage_size:
#             return jsonify({"error": f"Not enough storage space. Current usage: {current_storage_size / (1024 * 1024):.2f} MB, Max allowed: {max_storage_size / (1024 * 1024):.2f} MB"}), 400

#     except Exception as e:
#         current_app.logger.error(f"Error checking group storage limits: {str(e)}")
#         return jsonify({"error": "Failed to check group storage limits"}), 500

#     # Proceed with file upload
#     try:
#         try:
#             await group_directory_client.get_directory_properties()
#         except ResourceNotFoundError:
#             current_app.logger.info("Creating directory for group %s", group_id)
#             await group_directory_client.create_directory()
#         await group_directory_client.set_access_control(group=group_id)

#         # Ensure the filename is always group_picture with the original extension
#         new_filename = f"group_picture.{file_extension}"
#         file_client = group_directory_client.get_file_client(new_filename)

#         file_contents = file.read()
#         await file_client.upload_data(file_contents, overwrite=True)

#         # Calculate updated group uploads size
#         updated_group_uploads_size = await get_group_uploads_size(blob_container_client, group_id)

#         # Update the group information with the new logo filename
#         group_args = {
#             'group_id': group_id,
#             'groupLogoUrl': new_filename
#         }
#         await db_client.update_group(**group_args)

#         # Fetch the updated group information
#         updated_group = await db_client.get_groups(group_id=group_id)
#         if not updated_group:
#             return jsonify({"error": "Failed to fetch updated group information"}), 500

#         return jsonify({
#             "message": "Group logo uploaded successfully",
#             "group_uploads_size_bytes": updated_group_uploads_size,
#             "group_uploads_size_mb": round(updated_group_uploads_size / (1024 * 1024), 2),
#             "group": updated_group[0]
#         }), 200

#     except Exception as e:
#         current_app.logger.error(f"Error uploading group logo: {str(e)}")
#         return jsonify({"error": f"Failed to upload group logo: {str(e)}"}), 500


async def validate_prompt_text(prompt_text: str):
    # TODO: Implement prompt text validation
    # fetch all the policies 
    # check if the prompt text violates any of the policies
    # use openai to validate the prompt text and make it return a reason for rejection if it violates any policy


    class PolicyViolation(BaseModel):
        violations: list[str]
        status : bool 
    
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    model_client : AsyncOpenAI = current_app.config[CONFIG_OPENAI_CLIENT]
    model_name = os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"]
    if db_client and model_client:
        try:
            policies = await db_client.list_policies()
            # title_prompt = '''You are a policy validator. You are given a prompt text and a list of policies. You need to check if the prompt text violates any of the policies.
            # in the violations, you need to mention the violations that they broke. Example : x is not allowed, you can't do this.. etc.

            # If it does, return the policy it violated (only violated policy). If it does not violate any policies and false, return empty array and status true. If no policies are provided, you can return empty array and status true.
            # response should be a perfect json object with the following structure : 
            # {
            #     violations: [string],
            #     status: boolean
            # }
            # '''

            title_prompt = '''
                You are a policy validator. You will receive a prompt text and a list of policies. Your task is to determine whether the prompt text violates any of the provided policies.

                If the prompt text violates one or more policies, you need to identify the violations and specify which policies are broken (e.g., 'X is not allowed, you can't do this').
                If the prompt text does not violate any policies, return an empty array under the violations field and set the status field to true.
                If no policies are provided, simply return an empty array and set the status field to true.
                Ensure that your response strictly follows the structure below.
                Response format:

                {
                "violations": string[...],
                "status": boolean
                }
                Where:

                violations: An array containing a list of policy violations, if any.
                Make sure to return the violations in the same language as the prompt text and in the same tense as the prompt text.
                status: A boolean value indicating whether the prompt text is compliant (true) or violates policies (false)."
            '''

            policy_list = [policy['text'] for policy in policies]
            policy_list_str = '\n'.join(policy_list)
            messages = [
                {"role": "system", "content": title_prompt},
                {"role": "user", "content": f"Policies: \n{policy_list_str}"},
                {"role": "user", "content":  f"Prompt: \n{prompt_text}"}

            ]
            response = await model_client.chat.completions.create(
                model=model_name, messages=messages, temperature=0, max_tokens=1000,
                # response_format=PolicyViolation,
                # response_format={ "type": "json_object" }
                )
            event = response.choices[0].message.content
            try:
                policy_violation = PolicyViolation.model_validate_json(event)
                return policy_violation
                # event = json.loads(event)
            except:
                policy_violation = PolicyViolation(violations=['The model was unable to validate the prompt text. Try again.'], status=False)
                return policy_violation
        except Exception as e:
            current_app.logger.error(f"Error validating prompt text: {str(e)}")
            return PolicyViolation(violations=[str(e)], status=False)

        


@bp.route('/prompts/request/create', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def create_request_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_text = request_json.get('text', None)
    group_id = request_json.get('group_id', None)

    if not prompt_text:
        return jsonify({"error": "Missing prompt text"}), 400
    if not group_id:
        return jsonify({"error": "Missing group id"}), 400

    try:
        validation_result = await validate_prompt_text(prompt_text)
        if not validation_result.status:
            return jsonify({"error": "Prompt text violates policy", "violations": validation_result.violations}), 400
        
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.create_request_prompt(
                user_id='temp_user_id',
                prompt_text=prompt_text,
                group_id=group_id
            )
            return jsonify({"status": True, "prompt": response}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating request prompt: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/prompts/request/update', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def update_request_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    prompt_text = request_json.get('text', None)

    if not prompt_id or not prompt_text:
        return jsonify({"error": "Missing required fields (id/text)"}), 400

    try:
        if prompt_text:
            validation_result = await validate_prompt_text(prompt_text)
            if not validation_result.status:
                return jsonify({"error": "Prompt text violates policy", "violations": validation_result.violations}), 400

        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.update_request_prompt(
                prompt_id=prompt_id,
                prompt_text=prompt_text,
            )
            if response:
                return jsonify({"status": True, "prompt": response}), 200
            else:
                return jsonify({"error": "Prompt not found"}), 404
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating request prompt: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/prompts/request/delete', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def delete_request_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)

    if not prompt_id:
        return jsonify({"error": "Missing prompt id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            success = await db_client.delete_request_prompt(prompt_id=prompt_id)
            if success:
                return jsonify({"status": True, "message": "Prompt request deleted successfully"}), 200
            else:
                return jsonify({"error": "Prompt request not found"}), 404
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting request prompt: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/prompts/request/list', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def list_request_prompts(auth_claims: Dict[str, Any]):
    try:
        request_json = {}
        if request.is_json:
            request_json = await request.get_json()
        
        status = request_json.get('status', 'pending')
        group_id = request_json.get('group_id', None)
        
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            prompts = await db_client.list_request_prompts(status=status, group_id=group_id)
            return jsonify({"status": True, "prompts": prompts}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error listing request prompts: {str(e)}")
        return jsonify({"error": str(e)}), 400
    

@bp.route('/prompts/request/list-all', methods=['POST'])
@group_access(min_role='admin', group_required=True)
async def list_all_request_prompts(auth_claims: Dict[str, Any]):
    try:
        request_json = {}
        if request.is_json:
            request_json = await request.get_json()
        
        status = request_json.get('status', 'pending')
        group_id = request_json.get('group_id', None)
        
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            # prompts = await db_client.list_request_prompts(status=status, group_id=group_id)
            prompts = await db_client.list_request_prompts(status=status)
            return jsonify({"status": True, "prompts": prompts}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error listing request prompts: {str(e)}")
        return jsonify({"error": str(e)}), 400



@bp.route('/prompts/create', methods=['POST'])
@group_access(min_role='admin', group_required=True)
async def create_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_text = request_json.get('text', None)

    if not prompt_text:
        return jsonify({"error": "Missing prompt text"}), 400

    user_id = auth_claims.get('oid', None)
    if not user_id:
        return jsonify({"error": "User id not found"}), 400

    try:
        hashed_userid = await hash_uuid(user_id)
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        
        if db_client:
            response = await db_client.create_prompt(
                user_id=hashed_userid,
                prompt_text=prompt_text
            ) if db_client.async_mode else db_client.create_prompt(
                user_id=hashed_userid,
                prompt_text=prompt_text
            )
            return jsonify({"status": True, "prompt": response}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/prompts/delete', methods=['POST'])
@authenticated
async def delete_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)

    if not prompt_id:
        return jsonify({"error": "Missing prompt id"}), 400

    user_id = auth_claims.get('oid', None)
    if not user_id:
        return jsonify({"error": "User id not found"}), 400

    try:
        hashed_userid = await hash_uuid(user_id)
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        
        if db_client:
            prompt = await db_client.get_prompts(id=prompt_id)
            if prompt and len(prompt) > 0 and prompt[0]['id'] == 'default':
                return jsonify({"error": "Global default prompt cannot be deleted or modified"}), 400

            response = await db_client.delete_prompt(
                prompt_id=prompt_id,
                user_id=hashed_userid
            ) if db_client.async_mode else db_client.delete_prompt(
                prompt_id=prompt_id,
                user_id=hashed_userid
            )
            return jsonify({"status": True, "result": response}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/prompts/list', methods=['GET', 'POST'])
@authenticated
async def list_prompts(auth_claims: Dict[str, Any]):
    user_id = auth_claims.get('oid', None)
    # if not user_id:
    #     return jsonify({"error": "User id not found"}), 400

    try:
        hashed_userid = await hash_uuid(user_id)
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        
        if db_client:
            prompt_id = None
            if request.method == 'POST':
                if not request.is_json:
                    return jsonify({"error": "request must be json"}), 415
                request_json = await request.get_json()
                prompt_id = request_json.get('prompt_id',None)
                status = request_json.get('status',None)
                prompts = await db_client.get_prompts(id=prompt_id,status=status)
            else:
                prompts = await db_client.get_prompts()

            return jsonify({"status": True, "prompts": prompts}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error listing prompts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/prompts/update', methods=['POST'])
@authenticated
async def update_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    prompt_text = request_json.get('text', None)

    if not prompt_id or not prompt_text:
        return jsonify({"error": "Missing prompt id or text"}), 400

    user_id = auth_claims.get('oid', None)
    if not user_id:
        return jsonify({"error": "User id not found"}), 400

    try:
        hashed_userid = await hash_uuid(user_id)
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        
        if db_client:
            prompt = await db_client.get_prompts(id=prompt_id)
            if prompt and len(prompt) > 0 and prompt[0]['id'] == 'default':
                return jsonify({"error": "Global default prompt cannot be deleted or modified"}), 400

            response = await db_client.update_prompt(
                prompt_id=prompt_id,
                # user_id=hashed_userid,
                prompt_text=prompt_text
            ) if db_client.async_mode else db_client.update_prompt(
                prompt_id=prompt_id,
                # user_id=hashed_userid,
                prompt_text=prompt_text
            )
            return jsonify({"status": True, "prompt": response}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500



@bp.route('/groups/prompts/create', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def create_group_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    group_id = request_json.get('group_id')
    base_prompt_id = request_json.get('base_prompt_id')
    variables = request_json.get('variables', {})

    if not group_id or not base_prompt_id:
        return jsonify({"error": "Missing group_id or base_prompt_id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if not db_client:
            return jsonify({"error": "Failed to establish connection with DB"}), 400

        # Fetch the base prompt
        base_prompts = await db_client.get_prompts(id=base_prompt_id)
        if not base_prompts or len(base_prompts) == 0:
            return jsonify({"error": "Base prompt not found"}), 404
        
        base_prompt = base_prompts[0]  # Get the first (and should be only) prompt

        # Identify variables in the base prompt
        base_variables = re.findall(r'<(\w+)>', base_prompt['text'])


        # Check if all required variables are provided and valid
        for var in base_variables:
            if var not in variables:
                return jsonify({"error": f"Missing required variable: {var}"}), 400
            if not variables[var] or variables[var].isspace():
                return jsonify({"error": f"Variable {var} cannot be empty or contain only whitespace"}), 400

        # Create the new text by replacing variables in the base prompt
        new_text = base_prompt['text']
        for var, value in variables.items():
            new_text = new_text.replace(f'<{var}>', value)

        # Create the workspace prompt
        response = await db_client.create_workspace_prompt(
            base_prompt_id=base_prompt_id,
            text=new_text,
            variables=variables,
            group_id=group_id
        )
        return jsonify({"status": True, "prompt": response}), 200
    except Exception as e:
        current_app.logger.error(f"Error creating group prompt: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/groups/prompts/update', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def update_group_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    group_id = request_json.get('group_id')
    workspace_prompt_id = request_json.get('workspace_prompt_id')
    variables = request_json.get('variables', {})

    if not group_id or not workspace_prompt_id:
        return jsonify({"error": "Missing group_id or workspace_prompt_id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if not db_client:
            return jsonify({"error": "Failed to establish connection with DB"}), 400

        # Fetch the current workspace prompt
        workspace_prompt = await db_client.get_workspace_prompt(workspace_prompt_id)
        if not workspace_prompt:
            return jsonify({"error": "Workspace prompt not found"}), 404

        # Fetch the base prompt
        base_prompts = await db_client.get_prompts(id=workspace_prompt['basePromptId'])
        if not base_prompts or len(base_prompts) == 0:
            return jsonify({"error": "Base prompt not found"}), 404
        
        base_prompt = base_prompts[0]

        # Identify variables in the base prompt
        base_variables = re.findall(r'<(\w+)>', base_prompt['text'])

        # Check if all required variables are provided and valid
        all_variables_accounted = True
        for var in base_variables:
            if var not in variables:
                all_variables_accounted = False
                return jsonify({"error": f"Missing required variable: {var}"}), 400
            if not variables[var] or variables[var].isspace():
                all_variables_accounted = False
                return jsonify({"error": f"Variable {var} cannot be empty or contain only whitespace"}), 400

        # Create the new text by replacing variables in the base prompt
        new_text = base_prompt['text']
        for var, value in variables.items():
            new_text = new_text.replace(f'<{var}>', value)

        # Update the workspace prompt
        update_data = {
            'text': new_text,
        }
        if all_variables_accounted:
            update_data['variables'] = json.dumps(variables)

        updated_prompt = await db_client.update_workspace_prompt(
            workspace_prompt_id=workspace_prompt_id,
            **update_data
        )
        return jsonify({"status": True, "prompt": updated_prompt}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating group prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/groups/prompts/delete', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def delete_group_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    group_id = request_json.get('group_id')
    workspace_prompt_id = request_json.get('workspace_prompt_id')

    if not group_id or not workspace_prompt_id:
        return jsonify({"error": "Missing group_id or workspace_prompt_id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            # Check if the prompt is active
            prompt = await db_client.get_workspace_prompt(workspace_prompt_id)
            if not prompt:
                return jsonify({"error": "Workspace prompt not found"}), 404
            
            if prompt.get('active', False):
                return jsonify({"error": "Cannot delete an active prompt"}), 400

            # Delete the prompt
            success = await db_client.delete_workspace_prompt(
                workspace_prompt_id=workspace_prompt_id
            )
            if success:
                return jsonify({"status": True, "message": "Prompt deleted successfully"}), 200
            else:
                return jsonify({"error": "Failed to delete prompt"}), 400
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting group prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/groups/prompts/list', methods=['POST'])
@group_access(min_role='member', group_required=True)
async def list_group_prompts(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    group_id = request_json.get('group_id',None)
    prompt_id = request_json.get('prompt_id',None)

    prompt_args = {k: v for k, v in {
        'groupId': group_id,
        'id': prompt_id,
    }.items() if v is not None}

    if not group_id:
        return jsonify({"error": "Missing group_id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            prompts = await db_client.list_workspace_prompts(**prompt_args)
            return jsonify({"status": True, "prompts": prompts}), 200
        else:
            return jsonify({"error": "Failed to establish connection with DB"}), 400
    except Exception as e:
        current_app.logger.error(f"Error listing group prompts: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/groups/prompts/set-default', methods=['POST'])
@group_access(min_role='owner', group_required=True)
async def set_default_group_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    group_id = request_json.get('group_id')
    prompt_id = request_json.get('prompt_id')
    active = request_json.get('active', True)
    if not group_id or not prompt_id:
        return jsonify({"error": "Missing group_id or prompt_id"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if not db_client:
            return jsonify({"error": "Failed to establish connection with DB"}), 400

        # Fetch the prompt to be set as default
        prompt = await db_client.get_workspace_prompt(prompt_id)
        if not prompt:
            return jsonify({"error": "Workspace prompt not found"}), 400

        if active:    
            await db_client.deactivate_all_workspace_prompts(group_id)
        if not active:
            active_prompts = await db_client.get_active_workspace_prompts(group_id=group_id)
            if len(active_prompts) == 1 and active_prompts[0]['id'] == prompt_id:
                return jsonify({"error": "Cannot deactivate the only active prompt"}), 400

        success = await db_client.update_workspace_prompt(
            workspace_prompt_id=prompt_id,
            active=active
        )

        if success:
            return jsonify({"status": True, "message": "Default prompt set successfully"}), 200
        else:
            return jsonify({"error": "Failed to set default prompt"}), 400

    except Exception as e:
        current_app.logger.error(f"Error setting default group prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500




@bp.route('/groups/contents', methods=['GET'])
@group_access(min_role='member', group_required=True)
async def get_group_content(auth_claims: Dict[str, Any]):
    group_id = request.args.get('group_id')
    file_name = request.args.get('file_name')

    if not group_id or not file_name:
        return jsonify({"error": "Missing group_id or file_name"}), 400

    try:
        blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        group_directory_client = blob_container_client.get_directory_client(group_id)
        file_client = group_directory_client.get_file_client(file_name)


        file_data = await file_client.download_file()
        

        file_stream = BytesIO()
        await file_data.readinto(file_stream)
        file_stream.seek(0)
        
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'

        return await send_file(file_stream, mimetype=mime_type, as_attachment=False, attachment_filename=file_name)

    except ResourceNotFoundError:
        return jsonify({"error": "File not found"}), 400
    except Exception as e:
        current_app.logger.error(f"Error fetching group content: {str(e)}")
        return jsonify({"error": "Failed to fetch group content"}), 500
    

    


@bp.route('/groups/members/remove',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def remove_members(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    group_id = request_json.get('group_id',None)
    member = request_json.get('member',None)
    owner = request_json.get('owner',None)

    if not group_id:
        return jsonify({"Error" : "Invalid/Missing group id"}),400
    if not owner and not member:
        return jsonify({"error" : "Missing/invalid member/owner"}),400
    else:
        try:
            credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))
        
            scopes = [
                'https://graph.microsoft.com/.default'
            ]

            graph_client = GraphServiceClient(credentials=credentials 
                                            #   ,scopes=scopes
                                          )
            if member:
                member_result = await graph_client.groups.by_group_id(group_id=group_id).members.by_directory_object_id(member).ref.delete()
            
            if owner:
                owner_result = await graph_client.groups.by_group_id(group_id=group_id).owners.by_directory_object_id(owner).ref.delete()
            return jsonify({"status" : True})
        except ODataError as error:
            return jsonify({'error' : error.error.message}),400
        except Exception as e:
            return jsonify({"status" : False,"error" : str(e)}),400


@bp.route('/groups/members/add',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def add_members(auth_claims):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    group_id = request_json.get('group_id',None)
    members = request_json.get('members',[])
    owner = request_json.get('owner',None)

    if not group_id:
        return jsonify({"error" : "Invalid/Missing group id"}),400
    if not owner and not members:
        return jsonify({"error" : "Missing/invalid member/owner"}),400
    else:
        try:
            credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))
        
            scopes = [
                'https://graph.microsoft.com/.default'
            ]

            graph_client = GraphServiceClient(credentials=credentials 
                                            #   ,scopes=scopes
                                          )
            if len(members) > 0:
                request_body_multiple = Group(
                    additional_data = {
                        "members@odata.bind": [
                            f"https://graph.microsoft.com/v1.0/directoryObjects/{id}"
                            for id in members
                        ]
                    }
                )
        
                # Adding multiple users to group
                group_result_multiple = await graph_client.groups.by_group_id(group_id).patch(request_body_multiple)
            
            if owner:
                request_body = ReferenceCreate(
                    odata_id = f"https://graph.microsoft.com/v1.0/users/{owner}",
                )

                owner_result = await graph_client.groups.by_group_id(group_id=group_id).owners.ref.post(request_body)
            return jsonify({"status" : True})
        except ODataError as error:
            return jsonify({'error' : error.error.message}),400

        except Exception as e:
            return jsonify({"status" : False,"error" : str(e)}),400

@bp.route('/groups/users/list', methods=['POST'])
@group_access(min_role='member', group_required=True)
async def list_group_users(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()

    group_id = request_json.get('group_id', None)
    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    # user_type should be a list containing 'owners', 'members', or both
    user_type = request_json.get('user_type', [])
    if not isinstance(user_type, list):
        return jsonify({"error": "user_type must be a list"}), 400

    owners = 'owners' in user_type
    members = 'members' in user_type

    if not owners and not members:
        return jsonify({"error": "user type must contain 'owners', 'members', or both"}), 400

    if any(user not in ['owners', 'members'] for user in user_type):
        return jsonify({"error": "Invalid user type. Only 'owners' and 'members' are allowed"}), 400

    try:
        # start_time = time.time()
        credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))
        
        graph_client = GraphServiceClient(credentials=credentials)

        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            count=True,
            orderby=["displayName"],
            select=["displayName", "id", "mail"],
        )

        request_configuration = RequestConfiguration(
            query_parameters=query_params,
        )
        request_configuration.headers.add("ConsistencyLevel", "eventual")
        members_list = []
        owners_list = []

        if members:
            members = await graph_client.groups.by_group_id(group_id=group_id).members.graph_user.get(request_configuration=request_configuration)
            for member in members.value:
                members_list.append({
                    'id': member.id,
                    'name': member.display_name,
                    'mail': member.mail
                })
        
        if owners:
            owners = await graph_client.groups.by_group_id(group_id=group_id).owners.graph_user.get(request_configuration=request_configuration)
            for owner in owners.value:
                owners_list.append({
                    'id': owner.id,
                    'name': owner.display_name,
                    'mail': owner.mail
                })
            
        # end_time = time.time()

        return jsonify({"members": members_list, "owners": owners_list}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in list_group_users: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/groups/questions/create',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def create_question(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    question = request_json.get('question',None)
    group_id = request_json.get('group_id',None)
    if not question or not group_id:
        return jsonify({"error" : "Invalid/Missing question or group id"}),400
    db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        response = await db_client.create_question(auth_claims['oid'],group_id,question)
        return jsonify({"status" : True}),200
    else:
        return jsonify({"error" : "Failed to establish connection with DB"}),400

@bp.route('/groups/questions/list',methods=['POST'])
@group_access(min_role='member',group_required=True)
async def list_questions(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    group_id = request_json.get('group_id',None)
    if not group_id:
        return jsonify({"error" : "Invalid/Missing group id"}),400
    db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        response = await db_client.get_questions(group_id)
        return jsonify({"questions" : response}),200
    else:
        return jsonify({"error" : "Failed to establish connection with DB"}),400

@bp.route('/groups/questions/update',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def update_question(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    question_id = request_json.get('question_id',None)
    question = request_json.get('question',None)    
    group_id = request_json.get('group_id',None)
    if not question_id or not question or not group_id:
        return jsonify({"error" : "Invalid/Missing question id or question"}),400
    db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        response = await db_client.update_question(question_id,auth_claims['oid'],group_id,question)
        return jsonify({"status" : True}),200
    else:
        return jsonify({"error" : "Failed to establish connection with DB"}),400

@bp.route('/groups/questions/delete',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def delete_question(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    question_id = request_json.get('question_id',None)
    if not question_id:
        return jsonify({"error" : "Invalid/Missing question id"}),400   
    db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if db_client:
        response = await db_client.delete_question(question_id,auth_claims['oid'])
        return jsonify({"status" : True}),200
    else:
        return jsonify({"error" : "Failed to establish connection with DB"}),400



# Policy Section

@bp.route('/groups/policies/create',methods=['POST'])
@group_access(min_role='admin',group_required=False)
async def create_policy(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    policy_text = request_json.get('policy_text',None)
    if not policy_text:
        return jsonify({"error" : "Invalid/Missing policy text"}),400
    try:

        db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.create_policy(policy_text)
            return jsonify({"status" : True,"policy" : response}),200
        else:
            return jsonify({"error" : "Failed to establish connection with DB"}),400
    except Exception as e:
        current_app.logger.error(f"Error in create_policy: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/groups/policies/list',methods=['GET'])
@group_access(min_role='admin',group_required=False)
async def list_policies(auth_claims: Dict[str, Any]):
    try:

        db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.list_policies()
            return jsonify({"policies" : response}),200
        else:
            return jsonify({"error" : "Failed to establish connection with DB"}),400
    except Exception as e:
        current_app.logger.error(f"Error in list_policies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/groups/policies/update',methods=['POST'])
@group_access(min_role='admin',group_required=False)
async def update_policy(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    policy_id = request_json.get('policy_id',None)
    policy_text = request_json.get('policy_text',None)
    if not policy_id or not policy_text:
        return jsonify({"error" : "Invalid/Missing policy id or policy text"}),400
    try:
        db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.update_policy(policy_id,policy_text)
            return jsonify({"status" : True,"policy" : response}),200
        else:
            return jsonify({"error" : "Failed to establish connection with DB"}),400
    except Exception as e:
        current_app.logger.error(f"Error in update_policy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/groups/policies/delete',methods=['POST'])
@group_access(min_role='admin',group_required=False)
async def delete_policy(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = await request.get_json()
    policy_id = request_json.get('policy_id',None)
    if not policy_id:
        return jsonify({"error" : "Invalid/Missing policy id"}),400
    try:
        db_client : BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if db_client:
            response = await db_client.delete_policy(policy_id)
            return jsonify({"status" : True}),200
        else:
            return jsonify({"error" : "Failed to establish connection with DB"}),400
    except Exception as e:
        current_app.logger.error(f"Error in delete_policy: {str(e)}")
        return jsonify({'error': str(e)}), 500
# End of Policy Section
    




@bp.route('/users/search/<search_query>', methods=['GET'])
@authenticated
async def search_users(auth_claims,search_query):

    try:
        credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                             client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                             client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))
        
        graph_client = GraphServiceClient(credentials=credentials)
        
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            count=True,
            search=f"\"displayName:{search_query}\"",
            orderby=["displayName"],
            select=["displayName", "id", "mail"],
        )

        request_configuration = RequestConfiguration(
            query_parameters=query_params,
        )
        request_configuration.headers.add("ConsistencyLevel", "eventual")

        users = await graph_client.users.get(request_configuration=request_configuration)
        
        users_list = []
        for user in users.value:
            users_list.append({
                'id': user.id,
                'name': user.display_name,
                'mail': user.mail
            })
        
        return jsonify({"users": users_list}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in search_users: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Send MSAL.js settings to the client UI
@bp.route("/auth_setup", methods=["GET"])
def auth_setup():
    auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
    return jsonify(auth_helper.get_auth_setup_for_client())


@bp.route("/config", methods=["GET"])
def config():
    return jsonify(
        {
            "showGPT4VOptions": current_app.config[CONFIG_GPT4V_DEPLOYED],
            "showSemanticRankerOption": current_app.config[CONFIG_SEMANTIC_RANKER_DEPLOYED],
            "showVectorOption": current_app.config[CONFIG_VECTOR_SEARCH_ENABLED],
            "showUserUpload": current_app.config[CONFIG_USER_UPLOAD_ENABLED],
            "showSpeechInput": current_app.config[CONFIG_SPEECH_INPUT_ENABLED],
            "showSpeechOutputBrowser": current_app.config[CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED],
            "showSpeechOutputAzure": current_app.config[CONFIG_SPEECH_OUTPUT_AZURE_ENABLED],
        }
    )


@bp.route("/speech", methods=["POST"])
async def speech():
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415

    speech_token = current_app.config.get(CONFIG_SPEECH_SERVICE_TOKEN)
    if speech_token is None or speech_token.expires_on < time.time() + 60:
        speech_token = await current_app.config[CONFIG_CREDENTIAL].get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        current_app.config[CONFIG_SPEECH_SERVICE_TOKEN] = speech_token

    request_json = await request.get_json()
    text = request_json["text"]
    try:
        # Construct a token as described in documentation:
        # https://learn.microsoft.com/azure/ai-services/speech-service/how-to-configure-azure-ad-auth?pivots=programming-language-python
        auth_token = (
            "aad#"
            + current_app.config[CONFIG_SPEECH_SERVICE_ID]
            + "#"
            + current_app.config[CONFIG_SPEECH_SERVICE_TOKEN].token
        )
        speech_config = SpeechConfig(auth_token=auth_token, region=current_app.config[CONFIG_SPEECH_SERVICE_LOCATION])
        speech_config.speech_synthesis_voice_name = current_app.config[CONFIG_SPEECH_SERVICE_VOICE]
        speech_config.speech_synthesis_output_format = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result: SpeechSynthesisResult = synthesizer.speak_text_async(text).get()
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            return result.audio_data, 200, {"Content-Type": "audio/mp3"}
        elif result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            current_app.logger.error(
                "Speech synthesis canceled: %s %s", cancellation_details.reason, cancellation_details.error_details
            )
            raise Exception("Speech synthesis canceled. Check logs for details.")
        else:
            current_app.logger.error("Unexpected result reason: %s", result.reason)
            raise Exception("Speech synthesis failed. Check logs for details.")
    except Exception as e:
        current_app.logger.exception("Exception in /speech")
        return jsonify({"error": str(e)}), 500



# @bp.post("/upload")
# @group_access(min_role='owner',group_required=False)
# async def upload(auth_claims: dict[str, Any]):
#     request_files = await request.files
#     request_form = await request.form
#     if "file" not in request_files:
#         # If no files were included in the request, return an error response
#         return jsonify({"message": "No file part in the request", "status": "failed"}), 400

#     user_oid = auth_claims["oid"]
#     group_id = request_form.get('group_id',None)

#     file = request_files.getlist("file")[0]
#     # print(request_form)
#     # return jsonify({"message": "File uploaded successfully"}), 200
#     blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
#     if not group_id:

#         user_directory_client = blob_container_client.get_directory_client(user_oid)
#         try:
#             await user_directory_client.get_directory_properties()
#         except ResourceNotFoundError:
#             current_app.logger.info("Creating directory for user %s", user_oid)
#             await user_directory_client.create_directory()
#         await user_directory_client.set_access_control(owner=user_oid,)
#         file_client = user_directory_client.get_file_client(file.filename)
#         file_io = file
#         file_io.name = file.filename
#         file_io = io.BufferedReader(file_io)
#         await file_client.upload_data(file_io, overwrite=True, metadata={"UploadedBy": user_oid})
#         file_io.seek(0)
#         ingester: UploadUserFileStrategy = current_app.config[CONFIG_INGESTER]
#         await ingester.add_file(File(content=file_io, acls={"oids": [user_oid],'groups' : ['59ee26ae-530b-4f8f-81b5-2a14d5ed03fa']}, url=file_client.url))
#         return jsonify({"message": "File uploaded successfully"}), 200
#     else:
#         is_admin = auth_claims.get('is_admin',True)
#         authorized = False
#         if not is_admin:
#             groups = auth_claims.get('groups_info',[])
#             for group in groups:
#                 if group['id'] == group_id and (group['highestRole'] == 'owner' or group['highestRole'] == 'admin'):
#                     authorized = True 
#                     break
#         else:
#             authorized = True


#         if authorized:
#             group_directory_client = blob_container_client.get_directory_client(group_id)
#             try:
#                 await group_directory_client.get_directory_properties()
#             except ResourceNotFoundError:
#                 current_app.logger.info("Creating directory for group %s", group_id)
#                 await group_directory_client.create_directory()
#                 await group_directory_client.set_access_control(group=group_id)
#             file_client = group_directory_client.get_file_client(file.filename)
#             file_io = file
#             file_io.name = file.filename
#             file_io = io.BufferedReader(file_io)
#             await file_client.upload_data(file_io, overwrite=True, metadata={"UploadedBy": group_id})
#             file_io.seek(0)
#             ingester: UploadUserFileStrategy = current_app.config[CONFIG_INGESTER]
#             await ingester.add_file(File(content=file_io, acls={'groups' : [group_id]}, url=file_client.url))
            
#             # Calculate group uploads size after upload
#             group_uploads_size = await get_group_uploads_size(blob_container_client, group_id)
            
#             return jsonify({
#                 "message": "File uploaded successfully",
#                 "group_uploads_size_bytes": group_uploads_size,
#                 "group_uploads_size_mb": round(group_uploads_size / (1024 * 1024), 2)
#             }), 200
#         else:
#             return jsonify({'error' : "You are not authorized to perform this action."}), 403

async def get_group_uploads_size(directory_client: FileSystemClient, group_id: str) -> int:
    total_size = 0
    async for path in directory_client.get_paths(path=group_id):
        if not path.is_directory:
            total_size += path.content_length
    return total_size







@bp.route("/list_uploaded",methods=['GET','POST'])
@group_access(min_role='member',group_required=False)
async def list_uploaded(auth_claims: dict[str, Any]):
    if request.method == 'GET':

        user_oid = auth_claims["oid"]
        user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        files = []
        try:
            total_size = 0
            all_paths = user_blob_container_client.get_paths(path=user_oid)
            async for path in all_paths:
                files.append(path.name.split("/", 1)[1])
                total_size += path.content_length
        except ResourceNotFoundError as error:
            if error.status_code != 404:
                current_app.logger.exception("Error listing uploaded files", error)
        return jsonify({"files":files,"group_uploads_size_bytes" : total_size}), 200
    elif request.method == 'POST':
        request_json = await request.get_json()
        if not request.is_json:
            return jsonify({"error": "request must be json"}), 415
        group_id = request_json.get('group_id',None)
        if not group_id:
            return jsonify({"error" : "group id required"}),400
        else:
            user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
            files = []
            try:
                all_paths = user_blob_container_client.get_paths(path=group_id)
                total_size = 0
                async for path in all_paths:
                    files.append(path.name.split("/", 1)[1])
                    total_size += path.content_length
            except ResourceNotFoundError as error:
                if error.status_code != 404:
                    current_app.logger.exception("Error listing uploaded files", error)
                # return jsonify({'error' : f'Error listing uploaded files : {error}'})
            except Exception as e:
                    current_app.logger.exception("Error listing uploaded files", e)
            return jsonify({"files":files,"group_uploads_size_bytes" : total_size}), 200

        


@bp.before_app_serving
async def setup_clients():
    # Replace these with your own values, either in environment variables or directly here
    # Use the current user identity to authenticate with Azure OpenAI, AI Search and Blob Storage (no secrets needed,
    # just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the
    # keys for each service
    # If you encounter a blocking error during a DefaultAzureCredential resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
    azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    # current_app.logger.info(azure_credential)
    # current_app.logger.info(type(azure_credential))

    # AZURE_STORAGE_ACCOUNT = os.environ["AZURE_STORAGE_ACCOUNT"]
    # AZURE_STORAGE_CONTAINER = os.environ["AZURE_STORAGE_CONTAINER"]
    # AZURE_USERSTORAGE_ACCOUNT = os.environ.get("AZURE_USERSTORAGE_ACCOUNT")
    # AZURE_USERSTORAGE_CONTAINER = os.environ.get("AZURE_USERSTORAGE_CONTAINER")
    # AZURE_SEARCH_SERVICE = os.environ["AZURE_SEARCH_SERVICE"]
    # AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]

    # #Cosmos DB setup
    # COSMOS_ENDPOINT = os.environ['AZURE_COSMOSDB_ENDPOINT']
    # COSMOS_KEY = os.getenv('AZURE_COSMOSDB_KEY',None)
    # DATABASE_NAME = os.environ['AZURE_COSMOSDB_DATABASE']
    # CONTAINER_NAME = os.environ['AZURE_COSMOSDB_CONVERSATIONS_CONTAINER']
    
    # DB Setup
    # db_type = os.getenv('DB_TYPE','COSMOS')

    # DB_CONNECTION = {
    #     'container_name' : os.environ['AZURE_COSMOSDB_CONVERSATIONS_CONTAINER'],
    #     'database_name' : os.environ['AZURE_COSMOSDB_DATABASE'],
    #     'credential' : os.getenv('AZURE_COSMOSDB_KEY') if os.getenv('AZURE_COSMOSDB_KEY',None) else azure_credential,
    #     'cosmosdb_endpoint' : os.environ['AZURE_COSMOSDB_ENDPOINT']
    # }
    # db_client : BaseDbClient = CosmosConversationClient(**DB_CONNECTION)
    # DB_CONNECTION = {
    #     'database_name' : os.environ['AZURE_COSMOSDB_DATABASE'],
    #     'credential' : os.getenv('AZURE_COSMOSDB_KEY') if os.getenv('AZURE_COSMOSDB_KEY',None) else azure_credential,
    #     'cosmosdb_endpoint' : os.environ['AZURE_COSMOSDB_ENDPOINT']
    # }
    # task_db_client : BaseDbClient = CosmosDocumentClient(**DB_CONNECTION)
    SQL_DB_CONNECTION = {
        'db_name': "sqldbdashboard",
        'password': None,  # Password not needed for "Active Directory Default"
        'user_name': None,  # Username is also handled via AAD
        'server_name': "sqldataharbor.database.windows.net",
        'authentication': "ActiveDirectoryDefault",
        'encrypt': True,
        'trust_server_certificate': False,
        'port': 1433,
        'alembic_config': Config('alembic.ini')
    }
    sql_db_client : BaseDbClient = SqlClient(**SQL_DB_CONNECTION)
    sql_db_client.run_migrations()



    # Shared by all OpenAI deployments
    


@bp.after_app_serving
async def close_clients():
    # await current_app.config[CONFIG_SEARCH_CLIENT].close()
    # await current_app.config[CONFIG_BLOB_CONTAINER_CLIENT].close()
    # if current_app.config.get(CONFIG_USER_BLOB_CONTAINER_CLIENT):
    #     await current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT].close()
    # if current_app.config.get(CONFIG_DB_CLIENT):
    #     await current_app.config[CONFIG_DB_CLIENT].close() if current_app.config[CONFIG_DB_CLIENT].async_mode else current_app.config[CONFIG_DB_CLIENT].close()
    # if current_app.config.get(CONFIG_TASK_DB_CLIENT):
    #     await current_app.config[CONFIG_TASK_DB_CLIENT].close() if current_app.config[CONFIG_TASK_DB_CLIENT].async_mode else current_app.config[CONFIG_TASK_DB_CLIENT].close()
    pass

def create_app():
    app = Quart(__name__)
    app.register_blueprint(bp)
    app.register_blueprint(usermanagement_bp)

    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 # 1GB

    


    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):

        app.logger.info("APPLICATIONINSIGHTS_CONNECTION_STRING is set, enabling Azure Monitor")
        configure_azure_monitor()
        # This tracks HTTP requests made by aiohttp:
        AioHttpClientInstrumentor().instrument()
        # This tracks HTTP requests made by httpx:
        HTTPXClientInstrumentor().instrument()
        # This tracks OpenAI SDK requests:
        OpenAIInstrumentor().instrument()
        # This middleware tracks app route requests:
        app.asgi_app = OpenTelemetryMiddleware(app.asgi_app)  # type: ignore[assignment]

    # Log levels should be one of https://docs.python.org/3/library/logging.html#logging-levels
    # Set root level to WARNING to avoid seeing overly verbose logs from SDKS
    logging.basicConfig(level=logging.WARNING)
    # Set the app logger level to INFO by default
    default_level = "INFO"
    app.logger.setLevel(os.getenv("APP_LOG_LEVEL", default_level))

    if allowed_origin := os.getenv("ALLOWED_ORIGIN"):
        app.logger.info("ALLOWED_ORIGIN is set, enabling CORS for %s", allowed_origin)
        cors(app, allow_origin=allowed_origin, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"])

    @app.before_request
    async def before_request():
        g.start = time.time()
        g.memory_before = psutil.Process().memory_info().rss

    @app.after_request
    async def after_request(response):
        auth_claims = g.get('auth_claims', None)
        user_details = {}
        # app.logger.info(auth_claims)
        if auth_claims:
            user_details['user_id'] = auth_claims.get('oid', None)
            if auth_claims.get('graph_token', None):
                if auth_claims.get('graph_token', None).get('id_token_claims', None):
                    user_details['name'] = auth_claims.get('graph_token', None).get('id_token_claims', None).get('name', None)
                    user_details['preferred_username'] = auth_claims.get('graph_token', None).get('id_token_claims', None).get('preferred_username', None)
        try:    
            user_details['workspace_id'] = g.get('group_id', None)
        except Exception as e:
            user_details['workspace_id'] = 'workspace id not found'
        memory_after = psutil.Process().memory_info().rss
        memory_diff = memory_after - g.memory_before
        app.logger.info(f"User details: {user_details} - Memory Usage: {memory_diff} bytes - Path: {request.path}")
        return response
    
    return app



@bp.route('/prompts/request/review', methods=['POST'])
@group_access(min_role='admin', group_required=False)
async def review_request_prompt(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    request_json = await request.get_json()
    prompt_id = request_json.get('id', None)
    action = request_json.get('action', None)  # 'approve' or 'reject'

    if not prompt_id or not action:
        return jsonify({"error": "Missing required fields (id/action)"}), 400
    
    if action not in ['approve', 'reject']:
        return jsonify({"error": "Invalid action. Must be 'approve' or 'reject'"}), 400

    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if not db_client:
            return jsonify({"error": "Failed to establish connection with DB"}), 400

        # Get the prompt request
        prompts = await db_client.list_request_prompts(prompt_id=prompt_id)
        if not prompts or len(prompts) == 0:
            return jsonify({"error": "Prompt request not found"}), 404
        
        prompt_request = prompts[0]

        if action == 'approve':
            # Create a new prompt with the text from the request
            user_id = auth_claims.get('oid', None)
            if not user_id:
                return jsonify({"error": "User id not found"}), 400

            hashed_userid = await hash_uuid(user_id)
            
            # Create the new prompt
            new_prompt = await db_client.create_prompt(
                user_id=hashed_userid,
                prompt_text=prompt_request['text']
            )

            # Delete the prompt request
            await db_client.delete_request_prompt(prompt_id=prompt_id)

            return jsonify({
                "status": True, 
                "message": "Prompt request approved and new prompt created",
                "prompt": new_prompt
            }), 200
        else:  # reject
            # Simply delete the prompt request
            await db_client.delete_request_prompt(prompt_id=prompt_id)
            return jsonify({
                "status": True, 
                "message": "Prompt request rejected and deleted"
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error reviewing prompt request: {str(e)}")
        return jsonify({"error": str(e)}), 400
