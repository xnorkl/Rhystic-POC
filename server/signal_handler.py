from aiohttp import web, WSMsgType
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
from .room_manager import RoomManager

@dataclass
class SignalMessage:
    type: str
    from_id: str
    target: Optional[str] = None
    sdp: Optional[Dict[str, Any]] = None
    candidate: Optional[Dict[str, Any]] = None

class SignalingHandler:
    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager
    
    async def _notify_peers(self, room_id: str, ws: web.WebSocketResponse, message: dict):
        """Send message to all peers in room except sender"""
        for peer in self.room_manager.get_peers(room_id):
            if peer != ws:
                await peer.send_json(message)

    async def _handle_signal_message(self, room_id: str, ws: web.WebSocketResponse, data: dict):
        """Handle WebRTC signaling messages"""
        if data['type'] in ['offer', 'answer', 'ice']:
            target_peer = next(
                (p for p in self.room_manager.get_peers(room_id)
                 if id(p) == int(data['target'])),
                None
            )
            if target_peer:
                await target_peer.send_json({**data, 'from': id(ws)})

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

        await self._notify_peers(room_id, ws, {
            'type': 'peer-joined',
            'peer_id': id(ws)
        })

        try:
            async for msg in ws:
                if msg.type != WSMsgType.TEXT and msg.type == WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    continue

                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    continue

                # Update peer activity timestamp
                room = self.room_manager.get_room(room_id)
                if not room:
                    continue

                room.update_peer_activity(ws)
                await self._handle_signal_message(room_id, ws, data)
        finally:
            # Notify peers about departure
            await self._notify_peers(room_id, ws, {
                'type': 'peer-left',
                'peer_id': id(ws)
            })
            self.room_manager.leave_room(room_id, ws)
        
        return ws