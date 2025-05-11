from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from models.schedule import Schedule

class IScheduleRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Schedule]:
        pass

    @abstractmethod
    def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        pass
    
    @abstractmethod
    def get_by_group_id(self, group_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    def get_by_teacher_id(self, teacher_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    def get_by_room_id(self, room_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    def get_by_subject_id(self, subject_id: int) -> List[Schedule]:
        pass
    
    @abstractmethod
    def get_by_date(self, date: date) -> List[Schedule]:
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[Schedule]:
        pass

    @abstractmethod
    def create(self, schedule: Schedule) -> Schedule:
        pass

    @abstractmethod
    def update(self, schedule: Schedule) -> Schedule:
        pass

    @abstractmethod
    def delete(self, schedule_id: int) -> bool:
        pass
