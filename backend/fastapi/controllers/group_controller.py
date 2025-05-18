from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependency_injector.wiring import inject, Provide

from models.DTOs.group_dto import GroupCreate, GroupUpdate, GroupResponse
from services.abstract.group_service_interface import IGroupService
from config.containers import Container

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("", response_model=List[GroupResponse], summary="Get all groups", description="Retrieve a list of all groups in the system")
@inject
async def get_all_groups(
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Get all groups endpoint.
    
    Returns:
        List[GroupResponse]: A list of all groups
    """
    return await service.get_all_groups()

@router.get("/{group_id}", response_model=GroupResponse, summary="Get group by ID", description="Retrieve a specific group by its ID")
@inject
async def get_group(
    group_id: int, 
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Get a specific group by ID.
    
    Args:
        group_id (int): The ID of the group to retrieve
        
    Returns:
        GroupResponse: The group details
        
    Raises:
        HTTPException: If the group is not found
    """
    # First check if the group exists
    group = await service.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    return group

@router.get("/name/{name}", response_model=GroupResponse, summary="Get group by name", description="Retrieve a specific group by its name")
@inject
async def get_group_by_name(
    name: str, 
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Get a specific group by name.
    
    Args:
        name (str): The name of the group to retrieve
        
    Returns:
        GroupResponse: The group details
        
    Raises:
        HTTPException: If the group is not found
    """
    # First check if the group exists
    group = await service.get_group_by_name(name)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with name '{name}' not found"
        )
    return group

@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED, summary="Create new group", description="Create a new group in the system")
@inject
async def create_group(
    group_data: GroupCreate, 
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Create a new group.
    
    Args:
        group_data (GroupCreate): The group data for creation
        
    Returns:
        GroupResponse: The created group details
    """
    return await service.create_group(group_data)

@router.put("/{group_id}", response_model=GroupResponse, summary="Update group", description="Update an existing group's information")
@inject
async def update_group(
    group_id: int, 
    group_data: GroupUpdate, 
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Update an existing group.
    
    Args:
        group_id (int): The ID of the group to update
        group_data (GroupUpdate): The updated group data
        
    Returns:
        GroupResponse: The updated group details
        
    Raises:
        HTTPException: If the group is not found
    """
    updated_group = service.update_group(group_id, group_data)
    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    return updated_group

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete group", description="Delete a group from the system")
@inject
async def delete_group(
    group_id: int, 
    service: IGroupService = Depends(Provide[Container.group_service])
):
    """Delete a group.
    
    Args:
        group_id (int): The ID of the group to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the group is not found
    """
    success = service.delete_group(group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    return None
