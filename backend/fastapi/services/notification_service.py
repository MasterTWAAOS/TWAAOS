from typing import List, Optional
from datetime import datetime

from models.notification import Notification
from models.DTOs.notification_dto import NotificationCreate, NotificationUpdate, NotificationResponse
from repositories.abstract.notification_repository_interface import INotificationRepository
from services.abstract.notification_service_interface import INotificationService

class NotificationService(INotificationService):
    def __init__(self, notification_repository: INotificationRepository):
        self.notification_repository = notification_repository

    def get_all_notifications(self) -> List[NotificationResponse]:
        notifications = self.notification_repository.get_all()
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    def get_notification_by_id(self, notification_id: int) -> Optional[NotificationResponse]:
        notification = self.notification_repository.get_by_id(notification_id)
        if notification:
            return NotificationResponse.model_validate(notification)
        return None
    
    def get_notifications_by_user_id(self, user_id: int) -> List[NotificationResponse]:
        notifications = self.notification_repository.get_by_user_id(user_id)
        return [NotificationResponse.model_validate(notification) for notification in notifications]
    
    def get_notifications_by_status(self, status: str) -> List[NotificationResponse]:
        notifications = self.notification_repository.get_by_status(status)
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        # Create new notification object
        notification = Notification(
            userId=notification_data.userId,
            message=notification_data.message,
            status=notification_data.status,
            dateSent=datetime.now()
        )
        
        # Save to database
        created_notification = self.notification_repository.create(notification)
        return NotificationResponse.model_validate(created_notification)

    def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> Optional[NotificationResponse]:
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification:
            return None
            
        # Update notification fields if provided
        if notification_data.userId is not None:
            notification.userId = notification_data.userId
        if notification_data.message is not None:
            notification.message = notification_data.message
        if notification_data.status is not None:
            notification.status = notification_data.status
            
        # Save changes
        updated_notification = self.notification_repository.update(notification)
        return NotificationResponse.model_validate(updated_notification)

    def delete_notification(self, notification_id: int) -> bool:
        return self.notification_repository.delete(notification_id)
    
    def mark_as_read(self, notification_id: int) -> Optional[NotificationResponse]:
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification:
            return None
        
        notification.status = "citit"
        updated_notification = self.notification_repository.update(notification)
        return NotificationResponse.model_validate(updated_notification)
