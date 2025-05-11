from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.DTOs.notification_dto import NotificationCreate, NotificationUpdate, NotificationResponse

class INotificationService(ABC):
    @abstractmethod
    def get_all_notifications(self) -> List[NotificationResponse]:
        pass

    @abstractmethod
    def get_notification_by_id(self, notification_id: int) -> Optional[NotificationResponse]:
        pass
    
    @abstractmethod
    def get_notifications_by_user_id(self, user_id: int) -> List[NotificationResponse]:
        pass
        
    @abstractmethod
    def validate_user_id(self, user_id: int) -> Tuple[bool, Optional[str]]:
        pass
    
    @abstractmethod
    def get_notifications_by_status(self, status: str) -> List[NotificationResponse]:
        pass

    @abstractmethod
    def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        pass

    @abstractmethod
    def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> Optional[NotificationResponse]:
        pass

    @abstractmethod
    def delete_notification(self, notification_id: int) -> bool:
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: int) -> Optional[NotificationResponse]:
        pass
