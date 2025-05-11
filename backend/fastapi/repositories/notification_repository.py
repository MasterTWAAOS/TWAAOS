from sqlalchemy.orm import Session
from typing import List, Optional

from models.notification import Notification
from repositories.abstract.notification_repository_interface import INotificationRepository

class NotificationRepository(INotificationRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Notification]:
        return self.db.query(Notification).all()

    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def get_by_user_id(self, user_id: int) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.userId == user_id).all()
    
    def get_by_status(self, status: str) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.status == status).all()

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def update(self, notification: Notification) -> Notification:
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def delete(self, notification_id: int) -> bool:
        notification = self.get_by_id(notification_id)
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
