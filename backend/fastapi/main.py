from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging

# Import all controllers
from controllers import user_controller
from controllers import group_controller
from controllers import subject_controller
from controllers import room_controller
from controllers import schedule_controller
from controllers import notification_controller
from controllers import excel_template_controller
from controllers import sync_controller
from controllers import auth_controller

from models.user import Base
from config.database import engine
from config.containers import Container
from dependency_injector.wiring import Provide, inject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comment out automatic table creation to use migrations instead
# Base.metadata.create_all(bind=engine)

# Create and configure the container
container = Container()

app = FastAPI(
    title="TWAAOS API",
    description="API for TWAAOS application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",  # Frontend running on local docker
        "http://127.0.0.1",  # Alternative localhost
        "http://localhost:80",  # With port specified
        "http://127.0.0.1:80",
        "http://localhost:8080",  # Vue.js development server
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_controller.router)
app.include_router(group_controller.router)
app.include_router(subject_controller.router)
app.include_router(room_controller.router)
app.include_router(schedule_controller.router)
app.include_router(notification_controller.router)
app.include_router(excel_template_controller.router)
app.include_router(sync_controller.router)
app.include_router(auth_controller.router)

# Root endpoint
@app.get("/", tags=["root"], summary="Root endpoint", description="Returns a welcome message for the API")
async def read_root():
    """Welcome endpoint for the API.
    
    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to TWAAOS API"}


# Custom OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# For local development
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)