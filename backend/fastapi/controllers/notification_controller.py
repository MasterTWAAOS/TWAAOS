from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependency_injector.wiring import inject, Provide

from models.DTOs.notification_dto import NotificationCreate, NotificationUpdate, NotificationResponse
from services.abstract.notification_service_interface import INotificationService
from config.containers import Container

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse], summary="Get all notifications", description="Retrieve a list of all notifications in the system")
@inject
async def get_all_notifications(
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Get all notifications endpoint.
    
    Returns:
        List[NotificationResponse]: A list of all notifications
    """
    return await service.get_all_notifications()

@router.get("/{notification_id}", response_model=NotificationResponse, summary="Get notification by ID", description="Retrieve a specific notification by its ID")
@inject
async def get_notification(
    notification_id: int, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Get a specific notification by ID.
    
    Args:
        notification_id (int): The ID of the notification to retrieve
        
    Returns:
        NotificationResponse: The notification details
        
    Raises:
        HTTPException: If the notification is not found
    """
    # First check if the notification exists
    notification = await service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return notification

@router.get("/user/{user_id}", response_model=List[NotificationResponse], summary="Get notifications by user", description="Retrieve all notifications for a specific user")
@inject
async def get_notifications_by_user(
    user_id: int, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Get notifications for a specific user.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        List[NotificationResponse]: A list of notifications for the specified user
    """
    return await service.get_notifications_by_user_id(user_id)

@router.get("/status/{status}", response_model=List[NotificationResponse], summary="Get notifications by status", description="Retrieve all notifications with a specific status")
@inject
async def get_notifications_by_status(
    status: str, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Get notifications with a specific status.
    
    Args:
        status (str): The status to filter by (e.g., 'trimis', 'citit')
        
    Returns:
        List[NotificationResponse]: A list of notifications with the specified status
    """
    return await service.get_notifications_by_status(status)

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED, summary="Create notification", description="Create a new notification in the system")
@inject
async def create_notification(
    notification_data: NotificationCreate, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Create a new notification.
    
    Args:
        notification_data (NotificationCreate): The notification data for creation
        
    Returns:
        NotificationResponse: The created notification details
        
    Raises:
        HTTPException: If validation fails for userId
    """
    try:
        return await service.create_notification(notification_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{notification_id}", response_model=NotificationResponse, summary="Update notification", description="Update an existing notification's information")
@inject
async def update_notification(
    notification_id: int, 
    notification_data: NotificationUpdate, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Update an existing notification.
    
    Args:
        notification_id (int): The ID of the notification to update
        notification_data (NotificationUpdate): The updated notification data
        
    Returns:
        NotificationResponse: The updated notification details
        
    Raises:
        HTTPException: If the notification is not found or validation fails
    """
    # First check if the notification exists
    notification = await service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Update the notification
    updated_notification = await service.update_notification(notification_id, notification_data)
    return updated_notification

@router.put("/{notification_id}/read", response_model=NotificationResponse, summary="Mark notification as read", description="Mark a notification as having been read")
@inject
async def mark_notification_as_read(
    notification_id: int, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Mark a notification as read.
    
    Args:
        notification_id (int): The ID of the notification to mark as read
        
    Returns:
        NotificationResponse: The updated notification details
        
    Raises:
        HTTPException: If the notification is not found
    """
    updated_notification = await service.mark_as_read(notification_id)
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return updated_notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete notification", description="Delete a notification from the system")
@inject
async def delete_notification(
    notification_id: int, 
    service: INotificationService = Depends(Provide[Container.notification_service])
):
    """Delete a notification.
    
    Args:
        notification_id (int): The ID of the notification to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the notification is not found
    """
    success = await service.delete_notification(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return None
