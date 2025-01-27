import uuid
from aiohttp import web

async def handle_create_room(request):
    room_id = str(uuid.uuid4())[:8]
    request.app['room_manager'].create_room(room_id)
    return web.json_response({
        'room_id': room_id,
        'status': 'created'
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
    for room_id in room_manager.rooms:
        room = room_manager.get_room(room_id)
        rooms.append({
            'id': room_id,
            'peer_count': len(room.peers),
            'max_peers': room.max_peers,
            'is_full': len(room.peers) >= room.max_peers
        })
    return web.json_response({'rooms': rooms}) 