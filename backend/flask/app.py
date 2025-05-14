"""
Main Quart application module (async Flask alternative).
This module initializes the Quart application and registers all the blueprints.
"""
import os
import logging
import asyncio
from quart import Quart, render_template_string
# Remove Flasgger import which is causing context issues
# from flasgger import Swagger
from routes.api import api_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """Create and configure the Quart application"""
    # Create and configure the app
    app = Quart(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Simple HTML documentation instead of Swagger
    docs_html = """
    <html>
        <head>
            <title>Data Synchronization API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                h2 { color: #555; margin-top: 30px; }
                pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .endpoint { margin-bottom: 30px; }
                .method { font-weight: bold; color: #009688; }
            </style>
        </head>
        <body>
            <h1>Data Synchronization API</h1>
            <p>API for synchronizing data from USV to TWAAOS</p>
            
            <h2>Endpoints:</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>Health check endpoint to verify the API is running.</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /fetch-and-sync-data</h3>
                <p>Fetch and synchronize data from USV APIs to the TWAAOS database.</p>
                <p>This endpoint handles the following synchronization tasks:</p>
                <ul>
                    <li>Groups from FIESC faculty</li>
                    <li>Rooms</li>
                    <li>Faculty staff (users)</li>
                    <li>Subjects with teachers and assistants</li>
                </ul>
            </div>
        </body>
    </html>
    """
    
    @app.route('/docs/')
    async def api_docs():
        return docs_html, {"Content-Type": "text/html"}
        
    logger.info('Custom API documentation initialized at /docs/')
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Log that we're starting up
    logger.info('Quart app initialized')
    
    return app

# Create the Quart app
app = create_app()

if __name__ == '__main__':
    import hypercorn.asyncio
    from hypercorn.config import Config
    
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    config.use_reloader = True
    
    asyncio.run(hypercorn.asyncio.serve(app, config))
