from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class ScheduleBase(BaseModel):
    subjectId: int
    teacherId: int
    roomId: int
    groupId: int
    date: date
    startTime: time
    endTime: time
    status: str  # ex: 'propus', 'acceptat', 'respins'

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    subjectId: Optional[int] = None
    teacherId: Optional[int] = None
    roomId: Optional[int] = None
    groupId: Optional[int] = None
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: int

    class Config:
        from_attributes = True
