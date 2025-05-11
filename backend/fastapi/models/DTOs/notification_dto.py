from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    userId: int
    message: str
    status: str  # ex: 'trimis', 'citit'

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    userId: Optional[int] = None
    message: Optional[str] = None
    status: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: int
    dateSent: datetime

    class Config:
        from_attributes = True
