from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from models.schedule import Schedule
from repositories.abstract.schedule_repository_interface import IScheduleRepository

class ScheduleRepository(IScheduleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Schedule]:
        result = await self.db.execute(select(Schedule))
        return result.scalars().all()

    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.id == schedule_id))
        return result.scalar_one_or_none()
    
    async def get_by_assistant_id(self, assistant_id: int) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.assistantId == assistant_id))
        return result.scalars().all()
    
    async def get_by_room_id(self, room_id: int) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.roomId == room_id))
        return result.scalars().all()
    
    async def get_by_subject_id(self, subject_id: int) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.subjectId == subject_id))
        return result.scalars().all()
    
    async def get_by_date(self, schedule_date: date) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.date == schedule_date))
        return result.scalars().all()
    
    async def get_by_status(self, status: str) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.status == status))
        return result.scalars().all()

    async def create(self, schedule: Schedule) -> Schedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def update(self, schedule: Schedule) -> Schedule:
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def delete(self, schedule_id: int) -> bool:
        schedule = await self.get_by_id(schedule_id)
        if schedule:
            await self.db.delete(schedule)
            await self.db.commit()
            return True
        return False
