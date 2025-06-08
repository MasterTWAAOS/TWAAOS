from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from models.DTOs.room_dto import RoomCreate, RoomUpdate, RoomResponse
from services.abstract.room_service_interface import IRoomService
from config.containers import Container

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("", response_model=List[RoomResponse], summary="Get all rooms", description="Retrieve a list of all rooms in the system")
@inject
async def get_all_rooms(
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Get all rooms endpoint.
    
    Returns:
        List[RoomResponse]: A list of all rooms
    """
    return await service.get_all_rooms()

@router.get("/{room_id}", response_model=RoomResponse, summary="Get room by ID", description="Retrieve a specific room by its ID")
@inject
async def get_room(
    room_id: int, 
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Get a specific room by ID.
    
    Args:
        room_id (int): The ID of the room to retrieve
        
    Returns:
        RoomResponse: The room details
        
    Raises:
        HTTPException: If the room is not found
    """
    room = await service.get_room_by_id(room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    return room

@router.get("/building/{building_name}", response_model=List[RoomResponse], summary="Get rooms by building", description="Retrieve a list of all rooms in a specific building")
@inject
async def get_rooms_by_building(
    building_name: str, 
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Get rooms in a specific building.
    
    Args:
        building_name (str): The name of the building
        
    Returns:
        List[RoomResponse]: A list of rooms in the specified building
    """
    return await service.get_rooms_by_building(building_name)

@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, summary="Create room", description="Create a new room record")
@inject
async def create_room(
    room_data: RoomCreate, 
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Create a new room.
    
    Args:
        room_data (RoomCreate): The room data for creation
        
    Returns:
        RoomResponse: The created room details
    """
    return await service.create_room(room_data)

@router.put("/{room_id}", response_model=RoomResponse, summary="Update room", description="Update an existing room's details")
@inject
async def update_room(
    room_id: int, 
    room_data: RoomUpdate, 
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Update an existing room.
    
    Args:
        room_id (int): The ID of the room to update
        room_data (RoomUpdate): The updated room data
        
    Returns:
        RoomResponse: The updated room details
        
    Raises:
        HTTPException: If the room is not found
    """
    updated_room = await service.update_room(room_id, room_data)
    if not updated_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    return updated_room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete room", description="Delete a room permanently")
@inject
async def delete_room(
    room_id: int, 
    service: IRoomService = Depends(Provide[Container.room_service])
):
    """Delete a room.
    
    Args:
        room_id (int): The ID of the room to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the room is not found
    """
    success = service.delete_room(room_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    return None
