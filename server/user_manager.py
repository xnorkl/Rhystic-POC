from dataclasses import dataclass
from typing import Dict, Optional
import uuid

@dataclass
class User:
    id: str
    username: str
    display_name: str
    active: bool = True
    current_room: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'active': self.active,
            'current_room': self.current_room
        }

class UserManager:
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def create_user(self, username: str, display_name: str) -> User:
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            display_name=display_name
        )
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_all_users(self) -> Dict[str, User]:
        return {uid: user for uid, user in self.users.items() if user.active}
    
    def update_user_room(self, user_id: str, room_id: Optional[str]) -> bool:
        user = self.get_user(user_id)
        if user:
            user.current_room = room_id
            return True
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        user = self.get_user(user_id)
        if user:
            user.active = False
            user.current_room = None
            return True
        return False 