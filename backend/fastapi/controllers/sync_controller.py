from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
import requests
import logging
from config.containers import Container

router = APIRouter(
    prefix="/api/sync",
    tags=["Synchronization"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

class SyncResponse(BaseModel):
    success: bool
    message: str

@router.post("/data", response_model=SyncResponse, 
           summary="Sync data from USV API", 
           description="Trigger synchronization of groups and rooms data from USV API")
@inject
def sync_data():
    """
    Triggers the Flask service to fetch groups and rooms from USV API and sync them to the database.
    
    Returns:
        SyncResponse: The synchronization result
        
    Raises:
        HTTPException: If the synchronization fails
    """
    try:
        # Call the Flask service
        response = requests.post("http://flask:5000/fetch-and-sync-data")
        response.raise_for_status()
        
        result = response.json()
        
        # Extract summary counts from the response
        groups_count = result.get('groups', {}).get('count', 0)
        rooms_count = result.get('rooms', {}).get('count', 0)
        
        return SyncResponse(
            success=True,
            message=f"Successfully synced {groups_count} groups and {rooms_count} rooms from USV API"
        )
    except requests.RequestException as e:
        logger.error(f"Error syncing data from USV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync data: {str(e)}"
        )
