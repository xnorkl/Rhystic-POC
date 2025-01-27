from dataclasses import dataclass, field
from typing import Dict, Set
from aiohttp import web
import uuid

@dataclass
class Room:
    id: str
    peers: Set[web.WebSocketResponse] = field(default_factory=set)
    max_peers: int = 8  # Updated to support 8 peers
    
    def get_peer_ids(self) -> Set[int]:
        return {id(peer) for peer in self.peers}

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.max_peers = 8

    def create_room(self, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(id=room_id)
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
        return True
    
    def leave_room(self, room_id: str, peer: web.WebSocketResponse):
        if room_id in self.rooms:
            self.rooms[room_id].peers.remove(peer)
            if not self.rooms[room_id].peers:
                del self.rooms[room_id]
    
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