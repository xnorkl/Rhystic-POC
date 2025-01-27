from aiohttp import web
import uvloop
import asyncio
from .room_manager import RoomManager
from .signal_handler import SignalingHandler
from .turn import TURNManager, TURNConfig
from .static_server import StaticFileServer
from .handlers import handle_create_user, handle_create_room, handle_get_room, handle_list_rooms
import os

async def init_app():
    # Initialize event loop with uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    # Create application
    app = web.Application()  # Initialize without debug parameter
    
    # Configure debug settings through middleware if needed
    if os.getenv('DEBUG', '0') == '1':
        app['debug'] = True
        # Add development middleware here if needed
    
    # Initialize components
    room_manager = RoomManager()
    
    # Development TURN config for localhost
    if app['debug']:
        turn_config = TURNConfig(
            server_url="localhost",
            realm="localhost",
            auth_secret="development_secret_key",
            tcp_port=3478,
            udp_port=3478,
            tls_port=5349
        )
    else:
        turn_config = TURNConfig(
            server_url="turn1.rhystic.io",
            realm="rhystic.io",
            auth_secret="your_secret_key_here"
        )
    
    turn_manager = TURNManager(turn_config)
    
    # Setup handlers
    signaling_handler = SignalingHandler(room_manager)
    static_server = StaticFileServer(app)
    
    # Store references
    app['room_manager'] = room_manager
    app['turn_manager'] = turn_manager
    
    # Setup routes
    app.router.add_get('/ws', signaling_handler.handle_connection)
    app.router.add_get('/turn', turn_manager.get_credentials)
    
    # REST API routes
    app.router.add_post('/api/users', handle_create_user)
    app.router.add_get('/api/rooms', handle_list_rooms)
    app.router.add_post('/api/rooms', handle_create_room)
    app.router.add_get('/api/rooms/{room_id}', handle_get_room)
    
    return app

def main():
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()