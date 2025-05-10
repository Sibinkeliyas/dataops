from quart import Blueprint, jsonify, request,current_app
from decorators import authenticated, group_access, error_response
from typing import Dict, Any
from config import CONFIG_AUTH_CLIENT, CONFIG_DB_CLIENT, CONFIG_TASK_DB_CLIENT
from db.service.db_client import BaseClient as BaseDbClient
import time
import logging
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks/create',methods=['POST','GET'])
@authenticated
async def create_task(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error" : "Invalid request"}),400
    data = await request.get_json()

    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]

    startsWith = data.get('startsWith')
    endsWith = data.get('endsWith')
    contains = data.get('contains')
    extensions = data.get('extensions',[])
    tags = data.get('tags',[])
    # task_name = data.get('taskName')

    # if starts, ends, contains , extensions. if any of these are not present, set to throw an error
    if not startsWith and not endsWith and not contains and not extensions:
        return jsonify({"error" : "At least one of startsWith, endsWith, contains, or extensions must be present"}),400
    
    task_args = {}
    for key, value in data.items():
        if value:
            task_args[key] = value
    
    try:
        task = await task_client.create_task(**task_args)
        return jsonify({"task" : task}),200
    except Exception as e:
        return jsonify({"error" : str(e)}),500
    

@tasks_bp.route('/tasks/list',methods=['POST','GET'])
@authenticated
async def list_tasks(auth_claims: Dict[str, Any]):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]

    if request.method == 'GET':
        try:
            tasks = await task_client.list_tasks()
            return jsonify({"tasks" : tasks}),200
        except Exception as e:
            print(e)
            return jsonify({"error" : str(e)}),500

    if not request.is_json:
        return jsonify({"error" : "Invalid request"}),400
    data = await request.get_json() 


    try:

        filters = {}
        for key, value in data.items():
            if value:
                filters[key] = value
            tasks = await task_client.list_tasks(**filters)
            return jsonify({"tasks" : tasks}),200
    except Exception as e:
        print(e)
        return jsonify({"error" : str(e)}),500
    

@tasks_bp.route('/tags/list',methods=['POST','GET'])
@authenticated
async def list_tags(auth_claims: Dict[str, Any]):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    if request.method == 'GET':
        try:
            tags = await task_client.get_tags()
            return jsonify({"tags" : tags}),200
        except Exception as e:
            print(e)
            return jsonify({"error" : str(e)}),500
    
    if not request.is_json:
        return jsonify({"error" : "Invalid request"}),400
    data = await request.get_json()
    tag_name = data.get('tagName')
    tag_id = data.get('tagId')
    if not tag_name and not tag_id:
        return jsonify({"error" : "Either Tag name or id  must be provided"}),400
    
    filters = {}
    if tag_name:
        filters['tagName'] = tag_name
    if tag_id:
        filters['tagId'] = tag_id
    try:
        tags = await task_client.list_tags(**filters)
        return jsonify({"tags" : tags}),200
    except Exception as e:
        print(e)
        return jsonify({"error" : str(e)}),500
    

@tasks_bp.route('/tags/create',methods=['POST'])
@authenticated
async def create_tag(auth_claims: Dict[str, Any]):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    data = await request.get_json()
    tag_name = data.get('tagName')
    if not tag_name:
        return jsonify({"error" : "Tag name is required"}),400
    try:
        tag = await task_client.get_tags(name=tag_name)
        if tag:
            return jsonify({"error" : "Tag already exists"}),400
        tag = await task_client.create_tag(tag_name)
        return jsonify({"tag" : tag}),200
    except Exception as e:
        print(e)
        return jsonify({"error" : str(e)}),500
    
@tasks_bp.route('/tags/search',methods=['GET'])
@authenticated
async def search_tag(auth_claims: Dict[str, Any]):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    tag_name = request.args.get('tagName')
    if not tag_name:
        return jsonify({"error": "tagName parameter is required"}), 400
    try:
        tags = await task_client.tag_search(tag_name)
        return jsonify({"tags" : tags}),200
    except Exception as e:
        print(e)
        return jsonify({"error" : str(e)}),500
    
@tasks_bp.route('/tasks/update',methods=['POST'])
@authenticated
async def update_task(auth_claims: Dict[str, Any]):
    task_client = current_app.config[CONFIG_TASK_DB_CLIENT]
    data = await request.get_json()
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({"error" : "task_id is required"}),400
    arguments = {}
    for key, value in data.items():
        if value and key != 'task_id':
            arguments[key] = value
    try:
        task = await task_client.update_task(task_id, **arguments)
        return jsonify({"task" : task}),200
    except Exception as e:
        print(e)
        logging.error(f"Error updating task: {e}")
        return jsonify({"error" : str(e)}),500
    
