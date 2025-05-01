from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging

from controllers import user_controller
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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_controller.router)

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