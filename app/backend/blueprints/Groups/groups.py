from quart import Blueprint, jsonify, request,current_app
from decorators import authenticated, group_access, error_response
from typing import Dict, Any
from config import CONFIG_AUTH_CLIENT, CONFIG_DB_CLIENT
from db.service.db_client import BaseClient as BaseDbClient
# import asyncio
import time

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups/list',methods=['POST','GET'])
@authenticated
async def list_groups(auth_claims: Dict[str, Any]):
    
    user_id = auth_claims.get('oid',None) if auth_claims else None
    if not user_id:
        return jsonify({"Error" : "user id required"})
    auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
    groups = auth_claims.get('groups',[])
    
    # start_time = time.time()
    owned_groups = await auth_helper.owned_groups(auth_claims['graph_token'])
    is_admin,group_roles = await auth_helper.get_combined_group_roles(groups,owned_groups)
    # end_time = time.time()
    # print(f"Time taken: {end_time - start_time} seconds")

    return jsonify({'is_admin' : is_admin,'groups' : group_roles})

@groups_bp.route('/groups/settings',methods=['POST'])
@group_access(min_role='owner',group_required=True)
async def update_group_settings(auth_claims: Dict[str, Any]):
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    
    
    data = await request.get_json()
    group_id = data.get('group_id', None)
    group_settings = data.get('settings', {})
    if not group_id:
        return jsonify({"error": "group_id is required"}), 400
    try:
        db_client: BaseDbClient = current_app.config[CONFIG_DB_CLIENT]

        group = await db_client.get_groups(group_id=group_id)
        if not group or len(group) == 0:
            return jsonify({"error": "workspace not found"}), 404
        group = group[0]

        group_args = {
            'group_id': group_id,
            'settings': group_settings
        }
        
        await db_client.update_group(**group_args)
        return jsonify({"status": True, "message": "Group settings updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500







