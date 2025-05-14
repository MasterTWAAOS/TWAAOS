from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
import logging
from config.containers import Container
from services.abstract.sync_service_interface import ISyncService
from services.abstract.group_service_interface import IGroupService
from services.abstract.room_service_interface import IRoomService
from services.abstract.user_service_interface import IUserService

router = APIRouter(
    prefix="/api/sync",
    tags=["Synchronization"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

class SyncResponse(BaseModel):
    success: bool
    message: str
    details: dict = None

class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int

@router.delete("/groups", response_model=DeleteResponse,
           summary="Delete all groups",
           description="Delete all groups from the database")
@inject
async def delete_all_groups(sync_service: ISyncService = Depends(Provide[Container.sync_service])):
    """
    Deletes all groups from the database.
    
    Args:
        sync_service: The sync service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        # Only delete groups, not the other entities
        deleted_counts = await sync_service.delete_all_data()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all groups",
            deleted_count=deleted_counts.get("groups", 0)
        )
    except Exception as e:
        logger.error(f"Error deleting all groups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all groups: {str(e)}"
        )

@router.delete("/rooms", response_model=DeleteResponse,
           summary="Delete all rooms",
           description="Delete all rooms from the database")
@inject
async def delete_all_rooms(room_service: IRoomService = Depends(Provide[Container.room_service])):
    """
    Deletes all rooms from the database.
    
    Args:
        room_service: The room service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = await room_service.delete_all_rooms()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all rooms",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting all rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all rooms: {str(e)}"
        )

@router.delete("/users", response_model=DeleteResponse,
           summary="Delete all users",
           description="Delete all users from the database")
@inject
async def delete_all_users(user_service: IUserService = Depends(Provide[Container.user_service])):
    """
    Deletes all users from the database.
    
    Args:
        user_service: The user service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = await user_service.delete_all_users()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all users",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all users: {str(e)}"
        )

@router.post("/data", response_model=SyncResponse, 
           summary="Sync data from USV API", 
           description="Triggers deletion of existing data and synchronization of groups, rooms, and users from USV API")
@inject
async def sync_data(
    sync_service: ISyncService = Depends(Provide[Container.sync_service])
):
    """
    Deletes all existing data and triggers the Flask service to fetch data from USV API and sync it to the database.
    
    Args:
        sync_service: The sync service that coordinates the entire synchronization process
        
    Returns:
        SyncResponse: The synchronization result
        
    Raises:
        HTTPException: If the synchronization fails
    """
    try:
        # Use the sync service to handle the entire synchronization process
        logger.info("Starting synchronization process using SyncService")
        result = await sync_service.sync_all_data()
        
        # Extract counts for the response message
        groups_count = result.get('synced', {}).get('groups', 0)
        rooms_count = result.get('synced', {}).get('rooms', 0)
        users_count = result.get('synced', {}).get('users', 0)
        test_users_count = result.get('test_users', {}).get('count', 0)
        
        # Create the success message
        message = f"Successfully synced {groups_count} groups, {rooms_count} rooms, and {users_count} users "
        if test_users_count > 0:
            message += f"(including {test_users_count} test users) "
        message += "from USV API"
        
        return SyncResponse(
            success=True,
            message=message,
            details=result
        )
    except Exception as e:
        logger.error(f"Error syncing data from USV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync data: {str(e)}"
        )

