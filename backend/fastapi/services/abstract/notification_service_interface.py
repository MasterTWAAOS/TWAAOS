from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.DTOs.notification_dto import NotificationCreate, NotificationUpdate, NotificationResponse

class INotificationService(ABC):
    @abstractmethod
    async def get_all_notifications(self) -> List[NotificationResponse]:
        pass

    @abstractmethod
    async def get_notification_by_id(self, notification_id: int) -> Optional[NotificationResponse]:
        pass
    
    @abstractmethod
    async def get_notifications_by_user_id(self, user_id: int) -> List[NotificationResponse]:
        pass
        
    @abstractmethod
    async def validate_user_id(self, user_id: int) -> Tuple[bool, Optional[str]]:
        pass
    
    @abstractmethod
    async def get_notifications_by_status(self, status: str) -> List[NotificationResponse]:
        pass

    @abstractmethod
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        pass

    @abstractmethod
    async def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> Optional[NotificationResponse]:
        pass

    @abstractmethod
    async def delete_notification(self, notification_id: int) -> bool:
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: int) -> Optional[NotificationResponse]:
        pass
