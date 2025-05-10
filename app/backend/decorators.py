import logging
from functools import wraps
from typing import Any, Callable, Dict
from quart import abort, current_app, request, jsonify, g
import asyncio
from config import CONFIG_AUTH_CLIENT, CONFIG_SEARCH_CLIENT, CONFIG_DB_CLIENT
from core.authentication import AuthError
from error import error_response
import time


def authenticated_path(route_fn: Callable[[str, Dict[str, Any]], Any]):
    """
    Decorator for routes that request a specific file that might require access control enforcement
    """

    @wraps(route_fn)
    async def auth_handler(path=""):
        auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
        search_client = current_app.config[CONFIG_SEARCH_CLIENT]
        db_client = current_app.config[CONFIG_DB_CLIENT]
        authorized = False

        try:
            # Get auth claims and group ID
            auth_claims = await auth_helper.get_auth_claims_if_enabled(request.headers)
            group_id = await get_group_id_from_request(request)
            g.group_id = group_id

            if group_id:
                # Group access logic
                db_groups = await db_client.get_groups()
                app_groups = {group['entraGroupId']: group for group in db_groups}
                user_groups = set(auth_claims.get('groups', []))

                # Check if user is admin
                is_admin = any(app_groups.get(gid, {}).get('groupType') == 'admin' 
                             for gid in user_groups)
                if is_admin:
                    authorized = True
                else:
                    # Check if user is member of the group
                    # is_member = bool(user_groups & set(app_groups.keys()))
                    is_member = group_id in user_groups
                    if is_member:
                        authorized = True
                    else:
                        # Check if user is owner of the group
                        owned_groups = await auth_helper.owned_groups(auth_claims['graph_token'])
                        if group_id in owned_groups:
                            authorized = True
            else:
                # Original path-based authorization logic
                authorized = await auth_helper.check_path_auth(path, auth_claims, search_client)

        except AuthError:
            abort(403)
        except Exception as error:
            logging.exception("Problem checking auth %s", error)
            return error_response(error, route="/content")

        if not authorized:
            abort(403)
        g.auth_claims = auth_claims
        return await route_fn(path, auth_claims)

    return auth_handler


def authenticated(route_fn: Callable[[Dict[str, Any]], Any]):
    """
    Decorator for routes that might require access control. Unpacks Authorization header information into an auth_claims dictionary
    """
    @wraps(route_fn)
    async def auth_handler(*args, **kwargs):
        auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
        try:
            # start_time = time.time()
            auth_claims = await auth_helper.get_auth_claims_if_enabled(request.headers)
            # end_time = time.time()
            # current_app.logger.info(f"authenticated decorator took {end_time - start_time:.2f} seconds")
            g.auth_claims = auth_claims
            return await route_fn(auth_claims, *args, **kwargs)
        except Exception as e:
            # print(str(str(e)))
            current_app.logger.error(f"Error in authenticated decorator: {e}")
            abort(403, description='You\'re not authorized to perform this action')
            
    
    return auth_handler



def group_access(min_role=None, group_required=False,path_required=False):
    """
    Decorator for routes that may require specific group access.
    :param min_role: Minimum role required (e.g., 'member', 'owner', 'admin')
    :param group_required: Whether a group_id is required for this route
    """
    def decorator(route_fn: Callable[[Dict[str, Any]], Any]):
        @wraps(route_fn)
        async def wrapper(*args, **kwargs):
            # start_time = time.time()
            if min_role and min_role not in {'admin', 'owner', 'member'}:
                raise TypeError("Invalid role specified for endpoint")
            
            auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
            db_client = current_app.config[CONFIG_DB_CLIENT]
            try:
                group_id = await get_group_id_from_request(request, kwargs)
                g.group_id = group_id
                if group_required and not group_id:
                    return AuthError(error="Group information is required for this operation", status_code=403).__json__()

                auth_claims, db_groups = await asyncio.gather(
                    auth_helper.get_auth_claims_if_enabled(request.headers),
                    db_client.get_groups()
                )

                if not group_required and not group_id:
                    g.auth_claims = auth_claims
                    return await route_fn(auth_claims, *args, **kwargs)
                
                app_groups = {group['entraGroupId']: group for group in db_groups}
                user_groups = set(auth_claims.get('groups', []))

                is_admin = any(app_groups.get(gid, {}).get('groupType') == 'admin' for gid in user_groups)
                
                if is_admin:
                    auth_claims['is_admin'] = True
                    g.auth_claims = auth_claims
                    return await route_fn(auth_claims, *args, **kwargs)

                if min_role == 'admin':
                    return AuthError(error="You're not authorized to perform this action", status_code=403).__json__()
                
                if min_role == 'owner':
                    owned_groups = await auth_helper.owned_groups(auth_claims['graph_token'])
                    if group_id in owned_groups:
                        auth_claims['is_owner'] = True
                        g.auth_claims = auth_claims
                        return await route_fn(auth_claims, *args, **kwargs)
                    return AuthError(error="You're not authorized to perform this action", status_code=403).__json__()
                
                if min_role == 'member':
                    # is_member = bool(user_groups & set(app_groups.keys()))
                    is_member = group_id in user_groups
                    if is_member:
                        auth_claims['is_member'] = True
                        g.auth_claims = auth_claims
                        return await route_fn(auth_claims, *args, **kwargs)
                    
                    owned_groups = await auth_helper.owned_groups(auth_claims['graph_token'])
                    if group_id in owned_groups:
                        auth_claims['is_owner'] = True
                        g.auth_claims = auth_claims
                        return await route_fn(auth_claims, *args, **kwargs)
                    
                    return AuthError(error="You're not authorized to perform this action", status_code=403).__json__()

                return AuthError(status_code=403, description="You're not authorized to perform this action").__json__()
            except Exception as e:
                current_app.logger.error(f"Error in group_access decorator: ")
                current_app.logger.error(e)
                return error_response(error="An unexpected error occurred", status_code=400).__json__()
            # finally:
                # end_time = time.time()
                # current_app.logger.info(f"group_access decorator took {end_time - start_time:.2f} seconds")
        return wrapper
    return decorator


def inject_group_info(group_required=False):
    """
    Decorator for routes that may require group access information.
    This decorator should be used after @authenticated.
    :param group_required: Whether a group_id is required for this route
    """
    def decorator(route_fn: Callable[[Dict[str, Any]], Any]):
        @wraps(route_fn)
        async def wrapper(auth_claims, *args, **kwargs):
            auth_helper = current_app.config[CONFIG_AUTH_CLIENT]
            db_client = current_app.config[CONFIG_DB_CLIENT]
            try:
                # Get group_id from various possible sources
                group_id = await get_group_id_from_request(request, kwargs)
                g.group_id = group_id
    
                if group_required and not group_id:
                    return AuthError(error="Group information is required for this operation", status_code=403).__json__()

                # Fetch application-specific groups from the database
                db_groups = await db_client.get_groups() if db_client.async_mode else db_client.get_groups()
                app_groups = {group['entraGroupId']: group for group in db_groups}

                # Determine user's role for each group
                user_groups_info = {}
                is_admin = False
                for group_id in auth_claims.get('groups', []):
                    if group_id in app_groups:
                        group_info = app_groups[group_id]
                        user_groups_info[group_id] = {
                            'role': 'member',
                            'name': group_info.get('groupName'),
                            'type': group_info.get('groupType')
                        }
                        if group_info.get('groupType') == 'admin':
                            is_admin = True

                auth_claims['user_groups_info'] = user_groups_info
                auth_claims['is_admin'] = is_admin

                return await route_fn(auth_claims, *args, **kwargs)
            
            except Exception as e:
                current_app.logger.error(f"Error in inject_group_info decorator: ")
                current_app.logger.error(e)
                abort(403, description='You\'re not authorized to perform this action')
        
        return wrapper
    return decorator

async def get_group_id_from_request(request, kwargs=None):
    if request.is_json:
        json_data = await request.get_json()
        group_id = json_data.get('group_id')
    else:
        group_id = None
    
    if not group_id:
        form = await request.form
        group_id = form.get('group_id')
    if not group_id:
        group_id = request.args.get('group_id')
    if not group_id and kwargs:
        group_id = kwargs.get('group_id')
    
    return group_id

def check_admin_status(auth_claims, app_groups):
    for group_id in auth_claims['groups']:
        if group_id in app_groups and app_groups[group_id]['groupType'] == 'admin':
            return True
    return False

def check_member_status(auth_claims, app_groups):
    for group_id in auth_claims['groups']:
        if group_id in app_groups:
            return True
    return False

def get_user_role_in_group(auth_claims, group_id):
    if group_id in auth_claims.get('owned_groups', {}):
        return 'owner'
    elif group_id in auth_claims.get('groups', []):
        return 'member'
    return None

def check_minimum_role(user_role, min_role):
    role_hierarchy = {'admin': 3, 'owner': 2, 'member': 1}
    required_role_value = role_hierarchy.get(min_role, 0)
    user_role_value = role_hierarchy.get(user_role, 0)

    if user_role_value < required_role_value:
        abort(403, description=f"Minimum role '{min_role}' not met for this group")

