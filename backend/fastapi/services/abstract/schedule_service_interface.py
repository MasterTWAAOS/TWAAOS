from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import date
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from models.DTOs.user_dto import UserResponse

class IScheduleService(ABC):
    @abstractmethod
    async def get_all_schedules(self) -> List[ScheduleResponse]:
        pass

    @abstractmethod
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_group_id(self, group_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_teacher_id(self, teacher_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_room_id(self, room_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_subject_id(self, subject_id: int) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_date(self, schedule_date: date) -> List[ScheduleResponse]:
        pass
    
    @abstractmethod
    async def get_schedules_by_status(self, status: str) -> List[ScheduleResponse]:
        pass
        
    @abstractmethod
    async def validate_subject_id(self, subject_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    async def delete_all_schedules(self) -> int:
        """Delete all schedules from the database
        
        Returns:
            int: Number of deleted schedules
        """
        pass
        
    @abstractmethod
    async def populate_schedules_from_subjects(self) -> Dict[str, Any]:
        """Populate schedules table with preliminary entries based on subjects
        
        This creates initial schedule entries for each subject in the database,
        allowing users to modify dates and times later
        
        Returns:
            Dict[str, Any]: Statistics about the population process
        """
        pass
        
    @abstractmethod
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    async def validate_room_id(self, room_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    async def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    async def create_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        pass

    @abstractmethod
    async def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[ScheduleResponse]:
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: int) -> bool:
        pass
        
    @abstractmethod
    async def get_subject_assistants(self, subject_id: int) -> List[UserResponse]:
        """Get assistants (CD users) associated with a specific subject
        
        Args:
            subject_id (int): The ID of the subject
            
        Returns:
            List[UserResponse]: List of users who are assistants for this subject
        """
        pass
        
    @abstractmethod
    async def check_conflicts(self, schedule_id: int, date: date, start_time: str, end_time: str, room_ids: List[int], assistant_ids: List[int]) -> Dict[str, Any]:
        """Check for conflicts with existing schedules for rooms, assistants, and teacher
        
        Args:
            schedule_id (int): ID of the schedule to exclude from conflict check
            date (date): Date for the proposed schedule
            start_time (str): Start time of proposed schedule in format HH:MM
            end_time (str): End time of proposed schedule in format HH:MM
            room_ids (List[int]): List of room IDs to check for conflicts
            assistant_ids (List[int]): List of assistant IDs to check for conflicts
            
        Returns:
            Dict[str, Any]: Dictionary with conflict information
        """
        pass
