import json
from aiohttp import web
from urllib.parse import urlparse
import uuid

async def handle_create_user(request):
    try:
        data = await request.json()

        # Validate required fields
        if not data or 'username' not in data or 'display_name' not in data:
            raise web.HTTPBadRequest(text="username and display_name are required")

        # Check if accessing via HTTPS/443
        forwarded_proto = request.headers.get('X-Forwarded-Proto', '')
        host = request.headers.get('Host', '')
        is_production = forwarded_proto == 'https' or ':443' in host

        # Create user via manager
        user = request.app['user_manager'].create_user(
            username=data['username'],
            display_name=data['display_name']
        )

        # Only auto-create room in development
        room_id = None
        if not is_production:
            room_id = str(uuid.uuid4())[:8]
            request.app['room_manager'].create_room(room_id)

        response = user.to_dict()
        if room_id:
            response['auto_created_room'] = room_id
        return web.json_response(response)
    except json.JSONDecodeError as err:
        raise web.HTTPBadRequest(text="Invalid JSON data") from err

async def handle_get_user(request):
    user_id = request.match_info['user_id']
    user = request.app['user_manager'].get_user(user_id)
    if not user:
        raise web.HTTPNotFound()
    return web.json_response(user)

async def handle_list_users(request):
    users = request.app['user_manager'].get_all_users()
    return web.json_response(list(users))