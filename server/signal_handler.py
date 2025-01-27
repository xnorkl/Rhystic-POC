from aiohttp import web, WSMsgType
import json
from typing import Optional
from .room_manager import RoomManager

class SignalingHandler:
    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager
    
    async def _handle_ws_message(self, ws: web.WebSocketResponse, room_id: str, msg) -> None:
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                for peer in self.room_manager.get_peers(room_id):
                    if peer != ws:
                        await peer.send_json(data)
            except json.JSONDecodeError:
                pass
        elif msg.type == WSMsgType.ERROR:
            print(f'WebSocket error: {ws.exception()}')

    async def handle_connection(self, request: web.Request) -> web.WebSocketResponse:
        # Get parameters
        room_id = request.query.get('room')
        user_id = request.query.get('user_id')
        
        if not room_id or not user_id:
            raise web.HTTPBadRequest(text="room and user_id are required")

        # Create WebSocket
        ws = web.WebSocketResponse(
            autoping=True,
            heartbeat=30.0,
            protocols=['webrtc-signaling']
        )
        
        # Check if WebSocket upgrade is possible
        if not ws.can_prepare(request):
            raise web.HTTPBadRequest(text="WebSocket upgrade required")

        await ws.prepare(request)
        
        # Join room
        if not self.room_manager.join_room(room_id, ws):
            await ws.close(code=4001, message=b'Room full or not found')
            return ws

        try:
            # Handle messages
            async for msg in ws:
                await self._handle_ws_message(ws, room_id, msg)
        finally:
            # Clean up on disconnect
            self.room_manager.leave_room(room_id, ws)
        
        return ws