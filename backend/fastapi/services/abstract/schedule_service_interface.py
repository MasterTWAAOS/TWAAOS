from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from datetime import date
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse

class IScheduleService(ABC):
    @abstractmethod
    def get_all_schedules(self) -> List[ScheduleResponse]:
        pass

    @abstractmethod
    def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_group_id(self, group_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_teacher_id(self, teacher_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_room_id(self, room_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_subject_id(self, subject_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_date(self, schedule_date: date) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    def get_schedules_by_status(self, status: str) -> List[ScheduleResponse]:
        pass
        
    @abstractmethod
    def validate_subject_id(self, subject_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    def validate_room_id(self, room_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    def create_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        pass

    @abstractmethod
    def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[ScheduleResponse]:
        pass

    @abstractmethod
    def delete_schedule(self, schedule_id: int) -> bool:
        pass
