from dataclasses import dataclass, field
from typing import Dict, Set, Optional
from aiohttp import web
import uuid
import asyncio

@dataclass
class Room:
    id: str
    peers: Set[web.WebSocketResponse] = field(default_factory=set)
    max_peers: int = 8  # Updated to support 8 peers
    last_activity: Dict[web.WebSocketResponse, float] = field(default_factory=dict)
    
    def get_peer_ids(self) -> Set[int]:
        return {id(peer) for peer in self.peers}

    def get_peer_by_id(self, peer_id: int) -> Optional[web.WebSocketResponse]:
        return next((p for p in self.peers if id(p) == peer_id), None)

    def update_peer_activity(self, peer: web.WebSocketResponse):
        self.last_activity[peer] = asyncio.get_event_loop().time()

    def remove_inactive_peers(self, timeout: float = 30.0) -> Set[web.WebSocketResponse]:
        current_time = asyncio.get_event_loop().time()
        inactive_peers = {
            peer for peer in self.peers
            if current_time - self.last_activity.get(peer, 0) > timeout
        }
        for peer in inactive_peers:
            self.peers.remove(peer)
            del self.last_activity[peer]
        return inactive_peers

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.max_peers = 8
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        async def cleanup_loop():
            while True:
                await self._cleanup_inactive_peers()
                await asyncio.sleep(10)  # Check every 10 seconds

        asyncio.create_task(cleanup_loop())

    async def _cleanup_inactive_peers(self):
        for room_id, room in list(self.rooms.items()):
            inactive_peers = room.remove_inactive_peers()
            for peer in inactive_peers:
                if not peer.closed:
                    await peer.close()

            # Remove empty rooms
            if not room.peers:
                del self.rooms[room_id]

    def create_room(self, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(id=room_id)
            print(f"Created room {room_id}, total rooms: {len(self.rooms)}")
        return self.rooms[room_id]

    def get_room(self, room_id: str):
        return self.rooms.get(room_id)

    def join_room(self, room_id: str, peer: web.WebSocketResponse) -> bool:
        if room_id not in self.rooms:
            return False
            
        room = self.rooms[room_id]
        if len(room.peers) >= room.max_peers:
            return False
            
        room.peers.add(peer)
        room.update_peer_activity(peer)
        return True
    
    def leave_room(self, room_id: str, peer: web.WebSocketResponse):
        if room_id in self.rooms:
            try:
                self.rooms[room_id].peers.remove(peer)
                if peer in self.rooms[room_id].last_activity:
                    del self.rooms[room_id].last_activity[peer]
                if not self.rooms[room_id].peers:
                    del self.rooms[room_id]
            except KeyError:
                # Peer wasn't in room, that's okay
                pass
    
    def get_peers(self, room_id: str) -> Set[web.WebSocketResponse]:
        return self.rooms[room_id].peers if room_id in self.rooms else set()
    
    def get_room_info(self, room_id: str) -> dict:
        if room_id not in self.rooms:
            return {}
        room = self.rooms[room_id]
        return {
            'id': room.id,
            'peer_count': len(room.peers),
            'max_peers': room.max_peers,
            'peer_ids': [id(peer) for peer in room.peers]
        }

    def list_rooms(self) -> Dict[str, Room]:
        return self.rooms