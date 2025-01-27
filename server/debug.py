"""Debug entrypoint for development with additional debugging tools."""
import os
import logging
import asyncio
import uvloop
import aiohttp_debugtoolbar
from aiohttp import web
from .api import init_app

async def init_debug_app():
    # Ensure debug environment
    os.environ['DEBUG'] = '1'
    
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('rhystic.debug')
    
    # Create application with debug tools
    app = await init_app()
    
    # Add debug toolbar
    aiohttp_debugtoolbar.setup(app, check_host=False)
    
    # Add development middleware
    app.middlewares.extend([
        # Log all requests
        @web.middleware
        async def request_logger(request, handler):
            logger.debug(f"{request.method} {request.path}")
            response = await handler(request)
            logger.debug(f"Response: {response.status}")
            return response,
        
        # Enable CORS for development
        async def cors_middleware(app, handler):
            async def middleware(request):
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            return middleware
    ])
    
    return app

def main():
    # Use uvloop for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    # Initialize and run debug app
    app = init_debug_app()
    web.run_app(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        access_log_format='%a "%r" %s %b "%{Referer}i" "%{User-Agent}i" %Tf'
    )

if __name__ == '__main__':
    main() 