from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from models.notification import Notification
from repositories.abstract.notification_repository_interface import INotificationRepository

class NotificationRepository(INotificationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Notification]:
        result = await self.db.execute(select(Notification))
        return result.scalars().all()

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        result = await self.db.execute(select(Notification).filter(Notification.id == notification_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[Notification]:
        result = await self.db.execute(select(Notification).filter(Notification.userId == user_id))
        return result.scalars().all()
    
    async def get_by_status(self, status: str) -> List[Notification]:
        result = await self.db.execute(select(Notification).filter(Notification.status == status))
        return result.scalars().all()

    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def update(self, notification: Notification) -> Notification:
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete(self, notification_id: int) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification:
            await self.db.delete(notification)
            await self.db.commit()
            return True
        return False
        
    async def delete_all(self) -> int:
        """Delete all notifications from the database
        
        Returns:
            int: Number of notifications deleted
        """
        # Use the SQLAlchemy delete statement to delete all notifications at once
        from sqlalchemy import delete
        result = await self.db.execute(delete(Notification))
        deleted_count = result.rowcount
        await self.db.commit()
        
        print(f"Deleted {deleted_count} notifications")
        return deleted_count
