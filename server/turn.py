from dataclasses import dataclass
from typing import Dict, Optional
import hmac
import time
import base64
import hashlib
from aiohttp import web

@dataclass
class TURNConfig:
    server_url: str
    realm: str
    auth_secret: str
    tcp_port: int = 3478
    udp_port: int = 3478
    tls_port: int = 5349
    lifetime: int = 3600

class TURNManager:
    def __init__(self, config: TURNConfig):
        self.config = config
    
    def _generate_credentials(self, username: str) -> Dict:
        timestamp = int(time.time()) + self.config.lifetime
        username_with_timestamp = f"{timestamp}:{username}"
        
        hmac_obj = hmac.new(
            self.config.auth_secret.encode(),
            username_with_timestamp.encode(),
            hashlib.sha1
        )
        password = base64.b64encode(hmac_obj.digest()).decode()
        
        return {
            'username': username_with_timestamp,
            'password': password,
            'ttl': self.config.lifetime,
            'uris': [
                f"turn:{self.config.server_url}:{self.config.udp_port}?transport=udp"
            ]
        }
    
    async def get_credentials(self, request: web.Request) -> web.Response:
        user_id = request.query.get('user_id')
        if not user_id:
            raise web.HTTPBadRequest(text="user_id is required")
            
        credentials = self._generate_credentials(user_id)
        return web.json_response({
            'iceServers': [
                {
                    'urls': credentials['uris'],
                    'username': credentials['username'],
                    'credential': credentials['password'],
                    'credentialType': 'password'
                },
                {'urls': 'stun:stun.l.google.com:19302'},
                {'urls': 'stun:stun1.l.google.com:19302'}
            ],
            'iceTransportPolicy': 'all'
        })