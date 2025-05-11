from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
import requests
import logging
from config.containers import Container
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

class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int

@router.delete("/groups", response_model=DeleteResponse,
           summary="Delete all groups",
           description="Delete all groups from the database")
@inject
def delete_all_groups(group_service: IGroupService = Depends(Provide[Container.group_service])):
    """
    Deletes all groups from the database.
    
    Args:
        group_service: The group service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = group_service.delete_all_groups()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all groups",
            deleted_count=deleted_count
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
def delete_all_rooms(room_service: IRoomService = Depends(Provide[Container.room_service])):
    """
    Deletes all rooms from the database.
    
    Args:
        room_service: The room service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = room_service.delete_all_rooms()
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
def delete_all_users(user_service: IUserService = Depends(Provide[Container.user_service])):
    """
    Deletes all users from the database.
    
    Args:
        user_service: The user service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = user_service.delete_all_users()
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
def sync_data(
    group_service: IGroupService = Depends(Provide[Container.group_service]),
    room_service: IRoomService = Depends(Provide[Container.room_service]),
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Deletes all existing data and triggers the Flask service to fetch data from USV API and sync it to the database.
    
    Args:
        group_service: The group service
        room_service: The room service
        user_service: The user service
        
    Returns:
        SyncResponse: The synchronization result
        
    Raises:
        HTTPException: If the synchronization fails
    """
    try:
        # First, delete all existing data
        deleted_groups = group_service.delete_all_groups()
        deleted_rooms = room_service.delete_all_rooms()
        deleted_users = user_service.delete_all_users()
        
        logger.info(f"Deleted {deleted_groups} groups, {deleted_rooms} rooms, and {deleted_users} users before synchronization")
        
        # Call the Flask service to fetch and sync new data
        response = requests.post("http://flask:5000/fetch-and-sync-data")
        response.raise_for_status()
        
        result = response.json()
        
        # Extract summary counts from the response
        groups_count = result.get('groups', {}).get('count', 0)
        rooms_count = result.get('rooms', {}).get('count', 0)
        users_count = result.get('users', {}).get('count', 0)
        
        return SyncResponse(
            success=True,
            message=f"Successfully synced {groups_count} groups, {rooms_count} rooms, and {users_count} users from USV API"
        )
    except requests.RequestException as e:
        logger.error(f"Error syncing data from USV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync data: {str(e)}"
        )
