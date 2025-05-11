from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    role: Literal['SG', 'CD', 'SEC', 'ADM']
    groupId: Optional[int] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    googleId: Optional[str] = None
    isActive: bool = True

class UserCreate(UserBase):
    passwordHash: Optional[str] = None

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal['SG', 'CD', 'SEC', 'ADM']] = None
    groupId: Optional[int] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    passwordHash: Optional[str] = None
    googleId: Optional[str] = None
    isActive: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True