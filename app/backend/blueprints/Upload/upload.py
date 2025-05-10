from quart import request, jsonify, current_app, Blueprint, Response
from typing import Any
from azure.storage.filedatalake import FileSystemClient
from azure.core.exceptions import ResourceNotFoundError
import io
from PIL import Image
from config import (CONFIG_USER_BLOB_CONTAINER_CLIENT, 
                    CONFIG_INGESTER, 
                    CONFIG_BLOB_CONTAINER_CLIENT,
                    CONFIG_CREDENTIAL,
                    CONFIG_TASK_DB_CLIENT)
from decorators import group_access
from prepdocslib.filestrategy import UploadUserFileStrategy
from prepdocslib.listfilestrategy import File
from db.service.db_client import BaseClient as BaseDbClient
from config import CONFIG_DB_CLIENT
import json
import asyncio
from quart.helpers import stream_with_context
# from typing import AsyncGenerator
from azure.storage.filedatalake import DataLakeDirectoryClient
from azure.storage.filedatalake import DataLakeFileClient
from azure.storage.blob.aio import BlobClient, BlobServiceClient
from azure.storage.blob import ContainerClient
import uuid
import asyncio
import logging
from urllib.parse import unquote


upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/groups/logo/upload', methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def upload_group_logo(auth_claims: dict[str, Any]):
    request_files = await request.files
    request_form = await request.form
    if "file" not in request_files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request_files.getlist("file")[0]
    group_id = request_form.get('group_id')
    file_size = int(request_form.get('file_size', 0))

    if not group_id:
        return jsonify({"error": "Group id is required"}), 400

    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_extension not in allowed_extensions:
        return jsonify({"error": "Invalid file type. Only PNG, JPG, and JPEG are allowed"}), 400

    # Verify file content
    try:
        img = Image.open(file.stream)
        img.verify()
        file.stream.seek(0)  # Reset file pointer
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    # Check group storage limits
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    try:
        group_info = await db_client.get_groups(group_id=group_id)
        if not group_info:
            return jsonify({"error": "Group not found"}), 404
        
        group_info = group_info[0]  # Assuming get_groups returns a list
        max_storage_size = group_info.get('maxStorageSize', 5) * 1024 * 1024  # Convert MB to bytes
        max_file_size = group_info.get('maxFileSize', 1) * 1024 * 1024  # Convert MB to bytes
        
        blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        group_directory_client = blob_container_client.get_directory_client(group_id)
        
        try:
            await group_directory_client.get_directory_properties()
            current_storage_size = await get_directory_size(blob_container_client, group_id)
        except ResourceNotFoundError:
            current_storage_size = 0

        if file_size > max_file_size:
            return jsonify({"error": f"File size exceeds the maximum allowed size of {max_file_size / (1024 * 1024):.2f} MB"}), 400

        if current_storage_size + file_size > max_storage_size:
            return jsonify({"error": f"Not enough storage space. Current usage: {current_storage_size / (1024 * 1024):.2f} MB, Max allowed: {max_storage_size / (1024 * 1024):.2f} MB"}), 400

    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        return jsonify({"error": "Failed to check group storage limits"}), 500

    # Proceed with file upload
    try:
        try:
            await group_directory_client.get_directory_properties()
        except ResourceNotFoundError:
            current_app.logger.info("Creating directory for group %s", group_id)
            await group_directory_client.create_directory()
        await group_directory_client.set_access_control(group=group_id)


        new_filename = f"group_picture.{file_extension}"
        file_client = group_directory_client.get_file_client(new_filename)

        file_contents = file.read()
        await file_client.upload_data(file_contents, overwrite=True,timeout=60)


        updated_group_uploads_size = await get_directory_size(blob_container_client, group_id)

        group_args = {
            'group_id': group_id,
            'groupLogoUrl': new_filename
        }
        await db_client.update_group(**group_args)

        # Fetch the updated group information
        updated_group = await db_client.get_groups(group_id=group_id)
        if not updated_group:
            return jsonify({"error": "Failed to fetch updated group information"}), 500

        return jsonify({
            "message": "Group logo uploaded successfully",
            "group_uploads_size_bytes": updated_group_uploads_size,
            "group_uploads_size_mb": round(updated_group_uploads_size / (1024 * 1024), 2),
            "group": updated_group[0]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error uploading group logo: {str(e)}")
        return jsonify({"error": f"Failed to upload group logo: {str(e)}"}), 500



@upload_bp.route('/groups/logo/delete', methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def delete_group_logo(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    group_id = request_json.get('group_id')
    if not group_id:
        return jsonify({"error": "Group id is required"}), 400
    
    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        group_info = await db_client.get_groups(group_id=group_id)
        if not group_info or len(group_info) == 0:
            return jsonify({"error": "Group not found"}), 404
        
        group_info = group_info[0]
        group_logo_url = group_info['groupLogoUrl']
        if not group_logo_url:
            return jsonify({"error": "Group logo not found"}), 404
        user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        user_directory_client = user_blob_container_client.get_directory_client(group_id)
        file_client = user_directory_client.get_file_client(group_logo_url)
        await file_client.delete_file()
        ingester = current_app.config[CONFIG_INGESTER]
        await ingester.remove_file(group_logo_url, group_id)
        # Calculate group uploads size after delete 
        group_uploads_size = await get_directory_size(user_blob_container_client, group_id)
        group_info['groupLogoUrl'] = None
        await db_client.update_group(**group_info)
        return jsonify({"message": f"Group logo deleted successfully", "group_uploads_size_bytes": group_uploads_size}), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 403
    

async def assign_tags_if_match(file_name : str, file_extension : str, directory : str, file_url : str, file_size : int, uploadedFrom : str):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    # current_app.logger.info(f'file_name : {file_name} file_extension : {file_extension} directory : {directory} file_url : {file_url} file_size : {file_size} uploadedFrom : {uploadedFrom}')
    tasks = await task_client.check_file_pattern(file_name=file_name, extensions=[file_extension])
    # current_app.logger.info(f'tasks : {tasks}')
    if len(tasks) > 0:
        current_app.logger.info(f'File {file_name} matches {len(tasks)} tasks')
        # current_app.logger.info('Assigning tags to the file')
        tags = []
        for task in tasks:
            tags.extend(task['tags'])
        tags = list(set(tags))
        current_app.logger.info(f'Assigning following tags to file : {tags}')
        # current_app.logger.info(f'file_name : {file_name} has tags : {tags} workspace_or_oid : {directory} file_url : {file_url} file_size : {file_size} uploadedFrom : {uploadedFrom}')
        await task_client.create_document(file_name=file_name,
                                          file_extension='.'+file_extension,
                                          workspace_or_oid=directory,
                                          file_url=file_url,
                                          file_size=file_size,
                                          uploadedFrom=uploadedFrom,
                                          tags=tags,
                                          file_metadata={})
        return True
    return False

    

@upload_bp.post("/upload")
@group_access(min_role='owner',group_required=False)
async def upload(auth_claims: dict[str, Any]):
    request_files = await request.files
    request_form = await request.form
    if "file" not in request_files:
        # If no files were included in the request, return an error response
        return jsonify({"message": "No file part in the request", "status": "failed"}), 400

    group_id = request_form.get('group_id',None)
    oid = auth_claims['oid']

    acls = {'groups' : [group_id]} if group_id else {'oids' : [oid]}
    
    
    file = request_files.getlist("file")[0]
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if group_id:
        group = await db_client.get_groups(group_id=group_id)
        group = group[0]
        max_size = group['maxStorageSize'] * 1024 * 1024
        max_file_size = group['maxFileSize'] * 1024 * 1024
    else:
        max_size = 50 * 1024 * 1024
        max_file_size = 50 * 1024 * 1024
    
    files_total_size = 0
    
    file.seek(0,2)
    file_size = file.tell()
    file.seek(0)
    if file_size > max_file_size:
        return jsonify({"error": f"File size exceeds the maximum allowed size of {max_file_size / (1024 * 1024)} MB", "status": "failed"}), 400
    files_total_size += file_size

    if files_total_size > max_size:
        return jsonify({"error": f"Total file size exceeds the maximum allowed size of {max_size / (1024 * 1024)} MB", "status": "failed"}), 400


    blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
   
    directory_client = blob_container_client.get_directory_client(group_id if group_id else oid)
    try:
        await directory_client.get_directory_properties()
    except ResourceNotFoundError:
        current_app.logger.info("Creating directory for group %s", group_id)
        await directory_client.create_directory()
        if group_id:
            await directory_client.set_access_control(group=group_id)
        else:
            await directory_client.set_access_control(owner=oid)
    try:
        file_client = directory_client.get_file_client(file.filename)
        file_io = file
        file_io.name = file.filename
        file_io = io.BufferedReader(file_io)
        await file_client.upload_data(file_io, overwrite=True, metadata={"UploadedBy": group_id if group_id else oid},timeout=60)
        file_io.seek(0)
        ingester: UploadUserFileStrategy = current_app.config[CONFIG_INGESTER]
        await ingester.add_file(File(content=file_io, acls=acls, url=file_client.url))
        task_client = current_app.config[CONFIG_TASK_DB_CLIENT]

        file_name_split = file.filename.split('.')
        file_name = file_name_split[0]
        file_extension = file_name_split[-1]

        await assign_tags_if_match(file_name=file.filename, 
                                   file_extension=file_extension, 
                                   directory=group_id if group_id else oid, 
                                   file_url=unquote(file_client.url.replace('%2F', '/')), 
                                   file_size=file_size, 
                                   uploadedFrom=group_id if group_id else oid)

    except Exception as e:
        return jsonify({"error": f"Error in ingesting file: {str(e)}", "status": "failed"}), 500
    
    # Calculate group uploads size after upload
    directory_size = await get_directory_size(blob_container_client, group_id if group_id else oid)
    
    return jsonify({
        "message": "File uploaded successfully",
        "directory_size": directory_size
    }), 200


@upload_bp.post("/delete_uploaded")
@group_access(min_role='owner',group_required=False)
async def delete_uploaded(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    filename = request_json.get("filename")
    user_oid = auth_claims["oid"]
    group_id = request_json.get('group_id',None)
    try:
        user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        user_directory_client = user_blob_container_client.get_directory_client(user_oid if not group_id else group_id)
        file_client = user_directory_client.get_file_client(filename)
        file_url = file_client.url
        await file_client.delete_file(recursive=True)
        ingester = current_app.config[CONFIG_INGESTER]
        await ingester.remove_file(filename, user_oid if not group_id else group_id)
        task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
        try:
            
            await task_client.delete_document(unquote(file_url.replace('%2F', '/')), user_oid if not group_id else group_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting document reference from db: {str(e)}")
        # Calculate group uploads size after delete 
        directory_size = await get_directory_size(user_blob_container_client, group_id if group_id else user_oid)
        return jsonify({"message": f"File {filename} deleted successfully", "directory_size": directory_size}), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 400


async def get_directory_size(directory_client: FileSystemClient, directory: str) -> int:
    total_size = 0
    async for path in directory_client.get_paths(path=directory):
        if not path.is_directory:
            total_size += path.content_length
    return total_size

@upload_bp.route('/stream-test', methods=['POST'])
@group_access(min_role='owner',group_required=False)
async def stream_test(auth_claims: dict[str, Any]):
    request_files = await request.files
    request_form = await request.form

    file = request_files.getlist("file")[0]
    file_io = file
    file_io.name = file.filename
    file_io = io.FileIO(file)
    # file_io = io.BytesIO(file.read())
    # file_io.name = file.filename
    @stream_with_context
    async def generate():
        try:
            # Get file and form data
            
            
            if "file" not in request_files:
                yield f"data: {json.dumps({'error': 'No file part in the request', 'progress': -1})}\n\n".encode('utf-8')
                return

            # Get user and group info
            group_id = request_form.get('group_id')
            
            if not group_id:
                yield f"data: {json.dumps({'error': 'No group_id provided', 'progress': -1})}\n\n".encode('utf-8')
                return

            # file = request_files.getlist("file")[0]

            yield f"data: {json.dumps({'message': 'Starting upload process...', 'progress': 10})}\n\n".encode('utf-8')

            # Get blob container client
            blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
            
            # Get/create group directory
            group_directory_client = blob_container_client.get_directory_client(group_id)
            
            yield f"data: {json.dumps({'message': 'Checking directory...', 'progress': 15})}\n\n".encode('utf-8')

            try:
                await group_directory_client.get_directory_properties()
            except ResourceNotFoundError:
                current_app.logger.info("Creating directory for group %s", group_id)
                await group_directory_client.create_directory()
                await group_directory_client.set_access_control(group=group_id)
            
            # yield f"data: {json.dumps({'message': 'Setting up file client...', 'progress': 20})}\n\n".encode('utf-8')

            file_client = group_directory_client.get_file_client(file.filename)
            
            # Read file content
            # file_client = group_directory_client.get_file_client(file.filename)
            # file_io = file
            # file_io.name = file.filename
            # file_io = io.BufferedReader(file.stream)
            # file_io.seek(0)
            yield f"data: {json.dumps({'message': 'Uploading file...', 'progress': 40})}\n\n".encode('utf-8')
            await file_client.upload_data(file_io, overwrite=True, metadata={"UploadedBy": group_id},timeout=60)
            yield f"data: {json.dumps({'message': 'Upload completed', 'progress': 60})}\n\n".encode('utf-8')
            file_io.seek(0)
            ingester: UploadUserFileStrategy = current_app.config[CONFIG_INGESTER]
            yield f"data: {json.dumps({'message': 'Updating index ...', 'progress': 70})}\n\n".encode('utf-8')
            await ingester.add_file(File(content=file_io, acls={'groups' : [group_id]}, url=file_client.url))
            yield f"data: {json.dumps({'message': 'Calculating final size...', 'progress': 90})}\n\n".encode('utf-8')

            # Calculate group uploads size
            group_uploads_size = await get_directory_size(blob_container_client, group_id)
            
            final_response = {
                "message": "File uploaded successfully",
                "filename": file.filename,
                "group_uploads_size_bytes": group_uploads_size,
                "group_uploads_size_mb": round(group_uploads_size / (1024 * 1024), 2),
                "progress": 100
            }
            
            yield f"data: {json.dumps(final_response)}\n\n".encode('utf-8')

        except Exception as e:
            # print(e)
            current_app.logger.error(f"Error in stream test: {str(e)}")
            yield f"data: {json.dumps({'error': f'Upload failed: {str(e)}', 'progress': -1})}\n\n".encode('utf-8')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )


async def batch_processing(directory : str,  acls : dict,batch_id : str,type : str,uploadedFrom : str):
    batch_directory = f'{directory}/batch-{batch_id}'
    blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
    azure_credential = current_app.config[CONFIG_CREDENTIAL]

    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    
    batch = await db_client.list_batch_processing(batch_id=batch_id)
    if not batch or len(batch) == 0:
        current_app.logger.error(f"Batch not found with id {batch_id}")
        return
    batch = batch[0]
    documents = batch['documents']
    ingester: UploadUserFileStrategy = current_app.config[CONFIG_INGESTER]

    # Get list of files from the directory
    for document in documents:
    # async for path in blob_container_client.get_paths(path=batch_directory):
        # print(path.name)
        document['status'] = 'processing'
        document['message'] = 'Processing file'
        if type == 'oid':
            await db_client.update_batch_processing(batch_id=batch_id,userId=directory,documents=documents)
        else:
            await db_client.update_batch_processing(batch_id=batch_id,documents=documents)
            

        file_path = f'{batch_directory}/{document["name"]}'
        file_extension = document['name'].split('.')[-1]
        file_name = document['name']
        file_size = 0
        
        try:
            file_client : DataLakeFileClient = blob_container_client.get_file_client(file_path)


            downloaded_file = await file_client.download_file()
            file_bytes = await downloaded_file.readall()
            file_name = document['name']
            # file_size = file.seek(0,2)
            file_io = io.BytesIO(file_bytes)
            file_io.seek(0,2)
            file_size = file_io.tell()
            file_io.seek(0)
            file_io.name = file_name
            file_object = File(content=file_io, acls=acls, url=file_client.url)
            current_app.logger.info(f"file : {file_name} has extension : {file_object.file_extension()}")
            await ingester.add_file(file_object)

        except Exception as e:
            batch['status'] = 'failed'
            document['status'] = 'failed'
            document['message'] = str(e)
            await db_client.update_batch_processing(batch_id=batch_id, documents=documents, status='failed')
            current_app.logger.error(f"Error in batch processing: {str(e)}")
            continue

        try:

            blob_url = f'https://{blob_container_client.account_name}.blob.core.windows.net/{blob_container_client.file_system_name}'
            # print(blob_url)
            bc : BlobClient = BlobClient(
                account_url=blob_url,
                container_name=batch_directory,
                blob_name=file_name,
                credential=azure_credential
            )

            client : BlobServiceClient = BlobServiceClient(
                account_url=blob_url,
                credential=azure_credential
            )
            blob_client : BlobClient = client.get_blob_client(directory, file_name)
            # print(f'{bc.url}')
            # await blob_client.start_copy_from_url(source_url=f'{bc.url}')
            await blob_client.start_copy_from_url(source_url=f'{bc.url}')
            task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
            file_extension = file_name.split('.')[-1]

            try:
                await assign_tags_if_match(file_name=file_name, 
                                           file_extension=file_extension, 
                                           directory=directory,
                                           file_url=unquote(file_client.url.replace('%2F', '/').replace(f'/batch-{batch_id}/','/')), 
                                           file_size=file_size, 
                                           uploadedFrom=uploadedFrom)
            except Exception as e:
                current_app.logger.error(f"Error in assigning tags to the file: {str(e)}")


            document['status'] = 'completed'
            document['message'] = 'File indexed successfully'
            if type == 'oid':
                await db_client.update_batch_processing(batch_id=batch_id,userId=directory,documents=documents)
            else:
                await db_client.update_batch_processing(batch_id=batch_id,documents=documents)
            await file_client.delete_file()
        except Exception as e:
            batch['status'] = 'failed'
            document['status'] = 'failed'
            document['message'] = str(e)
            if type=='oid':
                await db_client.update_batch_processing(batch_id=batch_id, userId=directory,documents=documents, status='failed')
            else:
                await db_client.update_batch_processing(batch_id=batch_id, documents=documents, status='failed')

            current_app.logger.error(f"Error in batch processing: {str(e)}")
            continue
        finally:
            asyncio.gather(client.close(), bc.close(), blob_client.close())
            
    
    updated_batch = await db_client.list_batch_processing(batch_id=batch_id)
    updated_batch = updated_batch[0]

    for document in updated_batch['documents']:
        if document['status'] == 'failed':
            updated_batch['status'] = 'failed'
            if type =='oid':
                await db_client.update_batch_processing(batch_id=batch_id, userId=directory,status='failed')
            else:
                await db_client.update_batch_processing(batch_id=batch_id,status='failed')

            break
    
    if updated_batch['status'] != 'failed':
        file_client : DataLakeDirectoryClient = blob_container_client.get_directory_client(batch_directory)
        await file_client.delete_directory()
        if type=='oid':
            await db_client.update_batch_processing(batch_id=batch_id, userId=directory,status='completed')
        else:
            await db_client.update_batch_processing(batch_id=batch_id, status='completed')

    


@upload_bp.route('/upload/batch', methods=['POST'])
@group_access(min_role='owner',group_required=False)
async def batch_upload(auth_claims: dict[str, Any]):
    request_files = await request.files
    request_form = await request.form
    if "files" not in request_files:
        return jsonify({"message": "No file part in the request", "status": "failed"}), 400

    group_id = request_form.get('group_id',None)
    oid = auth_claims.get('oid',None)
    blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]

    group_directory_client = blob_container_client.get_directory_client(group_id if group_id else oid)

    try:
        await group_directory_client.get_directory_properties()
    except ResourceNotFoundError:
        current_app.logger.info("Creating directory for group %s", group_id)
        await group_directory_client.create_directory()
        if group_id:
            await group_directory_client.set_access_control(group=group_id)
        else:
            await group_directory_client.set_access_control(owner=oid)

    
    
    files = request_files.getlist("files")

    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]

    if group_id:
        batch = await db_client.create_batch_processing(group_id=group_id)
    else:
        batch = await db_client.create_batch_processing(userId=oid)
    


    if group_id:
        group = await db_client.get_groups(group_id=group_id)
        group = group[0]
        max_size = group['maxStorageSize'] * 1024 * 1024
        max_file_size = group['maxFileSize'] * 1024 * 1024
    else:
        max_size = 50 * 1024 * 1024
        max_file_size = 50 * 1024 * 1024
    
    files_total_size = 0
    for file in files:
        file.seek(0,2)
        file_size = file.tell()
        file.seek(0)
        if file_size > max_file_size:
            return jsonify({"error": f"File size exceeds the maximum allowed size of {max_file_size / (1024 * 1024)} MB", "status": "failed"}), 400
        files_total_size += file_size
    
    if files_total_size > max_size:
        return jsonify({"error": f"Total file size exceeds the maximum allowed size of {max_size / (1024 * 1024)} MB", "status": "failed"}), 400
    


    current_app.logger.info(f"Batch processing created with id: {batch['id']}")

    batch_directory_client : DataLakeDirectoryClient = blob_container_client.get_directory_client(f'{group_id if group_id else oid}/batch-{batch["id"]}')
    
    try:
        await batch_directory_client.get_directory_properties()
    except ResourceNotFoundError:
        current_app.logger.info("Creating directory for batch processing %s", batch['id'])
        await batch_directory_client.create_directory()
        if group_id:
            await batch_directory_client.set_access_control(group=group_id)
        else:
            await batch_directory_client.set_access_control(owner=oid)
    
    documents = []

    try:

        for file in files:
            current_app.logger.info(f"Uploading file {file.filename}")
            file_client = batch_directory_client.get_file_client(file.filename)
            file_io = file
            file_io.name = file.filename
            file_io = io.BufferedReader(file_io)
            await file_client.upload_data(file_io, overwrite=True, metadata={"UploadedBy": group_id if group_id else oid},timeout=60)
            current_app.logger.info(f"File {file.filename} uploaded")
            documents.append({'id' : str(uuid.uuid4()), 
                            'name' : file.filename,
                            'status' : 'pending',
                            'message' : 'In queue for indexing',
                            'progress' : {
                                'batches' : 0, 
                                'progress' : 0
                            }})
        if group_id:
            await db_client.update_batch_processing(batch_id=batch['id'], documents=documents)
        else:
            await db_client.update_batch_processing(batch_id=batch['id'], userId=oid,documents=documents)
        current_app.logger.info(f"Batch processing updated with id: {batch['id']}")
        acls = {'groups' : [group_id]} if group_id else {'oids' : [oid]}
        current_app.logger.info(f"starting batch processing")
        current_app.add_background_task(batch_processing,group_id if group_id else oid,acls,batch['id'],'group' if group_id else 'oid','workspace' if group_id else 'user')
    except Exception as e:
        current_app.logger.error(f"Error in batch upload: {str(e)}")
        return jsonify({"error": "Error in batch upload", "status": "failed"}), 500
    
    updated_batch = await db_client.list_batch_processing(batch_id=batch['id'])
    updated_batch = updated_batch[0]
    return jsonify({
        "message": "Files uploaded successfully",
        "status": "success",
        "batch": updated_batch
    }), 200
    
@upload_bp.route('/batch/delete', methods=['POST'])
@group_access(min_role='owner',group_required=False)
async def delete_batch_processing(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    batch_id = request_json.get('batch_id',None)
    group_id = request_json.get('group_id',None)
    oid = auth_claims.get('oid',None)
    if not batch_id:
        return jsonify({"error": "No batch_id provided", "status": "failed"}), 400
    
    db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
    if group_id:
        batch = await db_client.list_batch_processing(batch_id=batch_id)
    else:
        batch = await db_client.list_batch_processing(batch_id=batch_id,userId=oid)

    if not batch or len(batch) == 0:
        return jsonify({"error": "Batch not found", "status": "failed"}), 404
    batch = batch[0]
    if batch['status'] not in ['completed','failed']:
        return jsonify({"error" : "Cannot delete a batch that is running"}),400
    else:
        directory_size = 0
        user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        try:
            user_directory_client = user_blob_container_client.get_directory_client(group_id if group_id else oid)
            file_client = user_directory_client.get_file_client(f'batch-{batch["id"]}')
            await file_client.delete_file(recursive=True)
            current_app.logger.info(f"Batch {batch['id']} deleted")
        except ResourceNotFoundError as e:
            current_app.logger.exception("Error deleting batch processing", e)
        except Exception as e:
            current_app.logger.exception("Error deleting batch processing", e)
        finally:
            if group_id:
                await db_client.delete_batch_processing(batch_id=batch_id)
            else:
                await db_client.delete_batch_processing(batch_id=batch_id,userId=oid)
        
        directory_size = await get_directory_size(user_blob_container_client,group_id if group_id else oid)
        return jsonify({"error": "Batch process deleted successfully", "status": "success","directory_size" : directory_size}), 200    


@upload_bp.route('/list/uploaded',methods=['POST'])
@group_access(min_role='member',group_required=False)
async def list_uploads(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    group_id = request_json.get('group_id',None)
    oid = auth_claims['oid']

    try:

        directory = group_id if group_id else oid
        user_blob_container_client: FileSystemClient = current_app.config[CONFIG_USER_BLOB_CONTAINER_CLIENT]
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        files = []
        recursive = request_json.get('recursive',False)
        try:
            all_paths = user_blob_container_client.get_paths(path=directory,recursive=False) # Force non-recursive
            async for path in all_paths:
                if not path.is_directory:
                    files.append({'name' : path.name.split("/", 1)[1], 'type' : 'file','size' : path.content_length})
            if group_id:
                batches = await db_client.list_batch_processing(group_id=group_id)
            else:
                batches = await db_client.list_batch_processing(userId=oid)
            batch_list = []
            for batch in batches:
                batch_list.append({'id' : batch['id'], 'type' : 'batch', 'documents' : batch['documents'],'status' : batch['status']})
            total_size = await get_directory_size(user_blob_container_client,directory)
            return jsonify({"files":files,"batches" : batch_list,"directory_size" : total_size}), 200

        except ResourceNotFoundError as error:
            if error.status_code != 404:
                current_app.logger.exception("Error listing uploaded files", error)
            return jsonify({"files" : [], "batches" : [], "directory_size" : 0}), 200
        except Exception as e:
                current_app.logger.exception("Error listing uploaded files", e)
                return jsonify({'error' : f'Error listing uploaded files : {e}'}),400
    except Exception as e:
        current_app.logger.exception("Error listing uploaded files", e)
        return jsonify({'error' : f'Error listing uploaded files : {e}'}),400


    

@upload_bp.route('/batch/fetch', methods=['POST'])
@group_access(min_role='owner',group_required=False)
async def fetch_batch(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    batch_id = request_json.get('batch_id',None)
    group_id = request_json.get('group_id',None)
    oid = auth_claims.get('oid',None)
    if not batch_id:
        return jsonify({"error": "No batch_id provided", "status": "failed"}), 400
    try:

        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]
        if group_id:
            batch = await db_client.list_batch_processing(batch_id=batch_id)
        else:
            batch = await db_client.list_batch_processing(batch_id=batch_id,userId=oid)
        if not batch or len(batch) == 0:
            return jsonify({"message": "Batch not found"}), 404
        batch = batch[0]
        return jsonify({"batch" : batch}), 200
    except Exception as e:
        current_app.logger.exception('Error fetching batch information',e)
        return jsonify({"error" : "Error fetching batch information. Try again"}),400
    

@upload_bp.route('/file/search', methods=['POST'])
@group_access(min_role='member',group_required=False)
async def file_search(auth_claims: dict[str, Any]):
    request_json = await request.get_json()
    match_all_tags = request_json.get('match_all_tags',None)
    match_any_tags = request_json.get('match_any_tags',None)
    oid = auth_claims['oid']
    group_id = request_json.get('group_id',None)
    if match_all_tags and match_any_tags:
        return jsonify({"error" : "Cannot provide both match_all_tags and match_any_tags", "status" : "failed"}), 400
    
    if not match_all_tags and not match_any_tags:
        return jsonify({"error" : "No tags provided", "status" : "failed"}), 400
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    if match_all_tags:
        documents = await task_client.file_search(oid=oid, group_id=group_id, match_all_tags=match_all_tags)
    elif match_any_tags:
        documents = await task_client.file_search(oid=oid, group_id=group_id, match_any_tags=match_any_tags)
    
    return jsonify({"files" : documents}), 200
    
    
    


    
    


