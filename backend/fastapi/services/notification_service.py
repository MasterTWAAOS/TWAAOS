from typing import List, Optional, Tuple
from datetime import datetime

from models.notification import Notification
from models.DTOs.notification_dto import NotificationCreate, NotificationUpdate, NotificationResponse
from repositories.abstract.notification_repository_interface import INotificationRepository
from repositories.abstract.user_repository_interface import IUserRepository
from services.abstract.notification_service_interface import INotificationService

class NotificationService(INotificationService):
    def __init__(self, notification_repository: INotificationRepository,
                 user_repository: IUserRepository):
        self.notification_repository = notification_repository
        self.user_repository = user_repository

    async def get_all_notifications(self) -> List[NotificationResponse]:
        notifications = await self.notification_repository.get_all()
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    async def get_notification_by_id(self, notification_id: int) -> Optional[NotificationResponse]:
        notification = await self.notification_repository.get_by_id(notification_id)
        if notification:
            return NotificationResponse.model_validate(notification)
        return None
    
    async def get_notifications_by_user_id(self, user_id: int) -> List[NotificationResponse]:
        notifications = await self.notification_repository.get_by_user_id(user_id)
        return [NotificationResponse.model_validate(notification) for notification in notifications]
        
    async def validate_user_id(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the user_id exists.
        
        Args:
            user_id: The user ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False, f"User with ID {user_id} does not exist"
        
        # All checks passed
        return True, None
    
    async def get_notifications_by_status(self, status: str) -> List[NotificationResponse]:
        notifications = await self.notification_repository.get_by_status(status)
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        # Validate user_id
        is_valid, error_message = await self.validate_user_id(notification_data.userId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Create new notification object
        notification = Notification(
            userId=notification_data.userId,
            message=notification_data.message,
            status=notification_data.status,
            dateSent=datetime.now()
        )
        
        # Save to database
        created_notification = await self.notification_repository.create(notification)
        return NotificationResponse.model_validate(created_notification)

    async def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> Optional[NotificationResponse]:
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification:
            return None
            
        # Validate user_id if provided
        if notification_data.userId is not None:
            is_valid, error_message = await self.validate_user_id(notification_data.userId)
            if not is_valid:
                raise ValueError(error_message)
            
        # Update notification fields if provided
        if notification_data.userId is not None:
            notification.userId = notification_data.userId
        if notification_data.message is not None:
            notification.message = notification_data.message
        if notification_data.status is not None:
            notification.status = notification_data.status
            
        # Save changes
        updated_notification = await self.notification_repository.update(notification)
        return NotificationResponse.model_validate(updated_notification)

    async def delete_notification(self, notification_id: int) -> bool:
        return await self.notification_repository.delete(notification_id)
    
    async def mark_as_read(self, notification_id: int) -> Optional[NotificationResponse]:
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification:
            return None
        
        notification.status = "citit"
        updated_notification = await self.notification_repository.update(notification)
        return NotificationResponse.model_validate(updated_notification)
