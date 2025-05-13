from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from models.schedule import Schedule

class IScheduleRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Schedule]:
        pass

    @abstractmethod
    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        pass
    
    @abstractmethod
    async def get_by_assistant_id(self, assistant_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    async def get_by_room_id(self, room_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    async def get_by_subject_id(self, subject_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    async def get_by_date(self, date: date) -> List[Schedule]:
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str) -> List[Schedule]:
        pass

    @abstractmethod
    async def create(self, schedule: Schedule) -> Schedule:
        pass

    @abstractmethod
    async def update(self, schedule: Schedule) -> Schedule:
        pass

    @abstractmethod
    async def delete(self, schedule_id: int) -> bool:
        pass
