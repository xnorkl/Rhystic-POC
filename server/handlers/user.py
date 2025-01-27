import uuid
from aiohttp import web

async def handle_create_user(request):
    data = await request.json()
    user = {
        'user_id': str(uuid.uuid4()),
        'username': data['username'],
        'display_name': data['display_name']
    }
    return web.json_response(user) 