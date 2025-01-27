from aiohttp import web
import pathlib

class StaticFileServer:
    def __init__(self, app: web.Application):
        self.app = app
        self.setup_routes()

    def setup_routes(self):
        # Get the project root directory
        project_root = pathlib.Path(__file__).parent.parent
        client_root = project_root / 'client'
        
        # Add routes for static files
        self.app.router.add_static('/js/', path=client_root / 'js')
        self.app.router.add_static('/css/', path=client_root / 'css')
        
        # Serve index.html at root
        self.app.router.add_get('/', self.serve_index)

    async def serve_index(self, request: web.Request) -> web.Response:
        project_root = pathlib.Path(__file__).parent.parent
        index_path = project_root / 'client' / 'index.html'
        
        if not index_path.exists():
            raise web.HTTPNotFound()
            
        with open(index_path) as f:
            return web.Response(
                text=f.read(),
                content_type='text/html'
            )