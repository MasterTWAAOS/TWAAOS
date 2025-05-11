from abc import ABC, abstractmethod
from typing import List, Optional
from models.notification import Notification

class INotificationRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Notification]:
        pass

    @abstractmethod
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Notification]:
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[Notification]:
        pass

    @abstractmethod
    def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def update(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        pass
