import uuid
from aiohttp import web

async def handle_create_room(request):
    room_id = str(uuid.uuid4())[:8]
    request.app['room_manager'].create_room(room_id)
    return web.json_response({
        'room_id': room_id,
        'status': 'created'
    })

async def handle_join_room(request):
    room_id = request.match_info['room_id']
    user_id = request.query.get('user_id')

    if not user_id:
        raise web.HTTPBadRequest(text="user_id is required")

    room = request.app['room_manager'].get_room(room_id)
    if not room:
        raise web.HTTPNotFound()

    # For REST API, we don't actually join the WebSocket connection
    # Just check if room is available
    if len(room.peers) >= room.max_peers:
        raise web.HTTPForbidden(text="Could not join room (full or not found)")

    # Update user's current room
    request.app['user_manager'].update_user_room(user_id, room_id)

    return web.json_response({
        'id': room_id,
        'joined': True,
        'peer_count': len(room.peers),
        'max_peers': room.max_peers
    })

async def handle_get_room(request):
    room_id = request.match_info['room_id']
    room = request.app['room_manager'].get_room(room_id)
    if not room:
        raise web.HTTPNotFound()
    return web.json_response({
        'id': room_id,
        'peer_count': len(room.peers),
        'max_peers': room.max_peers
    })

async def handle_list_rooms(request):
    room_manager = request.app['room_manager']
    rooms = []
    for room_id, room in room_manager.rooms.items():
        room = room_manager.get_room(room_id)
        rooms.append({
            'id': room_id,
            'peer_count': len(room.peers),
            'max_peers': room.max_peers,
            'is_full': len(room.peers) >= room.max_peers
        })
    return web.json_response({'rooms': rooms})

async def handle_leave_room(request):
    room_id = request.match_info['room_id']
    user_id = request.query.get('user_id')

    if not user_id:
        raise web.HTTPBadRequest(text="user_id is required")

    room = request.app['room_manager'].get_room(room_id)
    if not room:
        raise web.HTTPNotFound()

    # For REST API, we don't remove WebSocket peers
    # Just update user state

    # Update user state
    request.app['user_manager'].update_user_room(user_id, None)

    return web.json_response({
        'status': 'success',
        'message': 'Left room successfully'
    })