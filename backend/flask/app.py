"""
Main Quart application module (async Flask alternative).
This module initializes the Quart application and registers all the blueprints.
"""
import os
import logging
import asyncio
from quart import Quart
from flasgger import Swagger
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
    
    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
        "title": "Data Synchronization API",
        "description": "API for synchronizing data from USV to TWAAOS",
        "version": "1.0.0",
    }
    try:
        # Try to initialize Swagger - if there are compatibility issues, we'll catch and log them
        swagger = Swagger(app, config=swagger_config)
        logger.info('Swagger documentation initialized')
    except Exception as e:
        logger.warning(f'Could not initialize Swagger documentation: {str(e)}')
        logger.warning('API will run without Swagger documentation')
        pass
    
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
