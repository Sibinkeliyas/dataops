from quart import request, jsonify, current_app, Blueprint, Response
from typing import Dict, Any
from db.service.sql.sql_client import SqlClient
from db.service.sql.services.user_management_sql import UserManagement

usermanagement_bp = Blueprint('usermanagement', __name__)
user_management = UserManagement()

@usermanagement_bp.route("/user/usermanagement_bp/list-role", methods=["POST"])
# @group_access(min_role='admin', group_required=True)
async def list_user_roles():
    try:
        roles = user_management.get_roles()
        return jsonify({"success": True, "data": roles})
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500
    
@usermanagement_bp.route('/user/usermanagement_bp/create-role', methods=['POST'])
async def create_user_role():
    try:
        body = await request.get_json()
        role_name = body.get("name")
        await user_management.create_role(role_name)
        return {"success" : True, "role" :role_name}
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500
    
@usermanagement_bp.route('/user/usermanagement_bp/list-users', methods=['GET'])
async def get_users_list():
    try:
        users = user_management.get_users_list()
        return {"success" : True, "data" : users}
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500
    
@usermanagement_bp.route('/user/usermanagement_bp/create-user', methods=['POST'])
async def create_user():
    try:
        body = await request.get_json()
        name = body.get("name")
        email = body.get("email")
        role_id = body.get("role_id")
        if name is None or email is None or role_id is None :
             return jsonify({"error": "Fields are missing"}), 500
        is_user_exist = user_management.get_user(email)
        if(is_user_exist):
            return {"success" : True, "user" : is_user_exist}
        user = user_management.create_user(name, email, role_id)
        return {"success" : True, "user" : user}
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500
    

@usermanagement_bp.route('/user/usermanagement_bp/user', methods=['GET'])
async def find_user():
    try:
        email = request.args.get("email")
        print(email, "email from api")
        user = user_management.get_user(email)
        print(user, "fetched user")
        return {"success": True, "user": user}
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500
    
@usermanagement_bp.route('/user/usermanagement_bp/delete-user', methods=['delete'])
async def delete_user():
    try:
        id = request.args.get("id")
        print(id, "email from api")
        user = user_management.delete_user(id)
        print(user, "fetched user")
        return {"success": True, "user": user}
    except Exception as e:
        current_app.logger.error(f"Error checking group storage limits: {str(e)}")
        print(str(e))
        return jsonify({"error": str(e)}), 500


