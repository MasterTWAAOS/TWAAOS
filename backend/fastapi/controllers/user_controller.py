from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependency_injector.wiring import inject, Provide

from models.DTOs.user_dto import UserCreate, UserUpdate, UserResponse
from services.abstract.user_service_interface import IUserService
from config.containers import Container

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse], summary="Get all users", description="Retrieve a list of all users in the system")
@inject
def get_all_users(
    service: IUserService = Depends(Provide[Container.user_service])
):
    """Get all users endpoint.
    
    Returns:
        List[UserResponse]: A list of all users
    """
    return service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID", description="Retrieve a specific user by their ID")
@inject
def get_user(
    user_id: int, 
    service: IUserService = Depends(Provide[Container.user_service])
):
    """Get a specific user by ID.
    
    Args:
        user_id (int): The ID of the user to retrieve
        
    Returns:
        UserResponse: The user details
        
    Raises:
        HTTPException: If the user is not found
    """
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create new user", description="Create a new user in the system")
@inject
def create_user(
    user_data: UserCreate, 
    service: IUserService = Depends(Provide[Container.user_service])
):
    """Create a new user.
    
    Args:
        user_data (UserCreate): The user data for creation
        
    Returns:
        UserResponse: The created user details
        
    Raises:
        HTTPException: If a user with the same email already exists
    """
    # Check if user with this email already exists
    existing_user = service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user_data.email} already exists"
        )
    return service.create_user(user_data)

@router.put("/{user_id}", response_model=UserResponse, summary="Update user", description="Update an existing user's information")
@inject
def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    service: IUserService = Depends(Provide[Container.user_service])
):
    """Update an existing user.
    
    Args:
        user_id (int): The ID of the user to update
        user_data (UserUpdate): The updated user data
        
    Returns:
        UserResponse: The updated user details
        
    Raises:
        HTTPException: If the user is not found
    """
    updated_user = service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user", description="Delete a user from the system")
@inject
def delete_user(
    user_id: int, 
    service: IUserService = Depends(Provide[Container.user_service])
):
    """Delete a user.
    
    Args:
        user_id (int): The ID of the user to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the user is not found
    """
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None