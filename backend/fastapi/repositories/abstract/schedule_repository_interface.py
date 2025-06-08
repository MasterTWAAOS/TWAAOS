from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
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
        
    @abstractmethod
    async def delete_all_schedules(self) -> int:
        """Delete all schedule records
        
        Returns:
            int: Number of deleted records
        """
        pass
    
    @abstractmethod
    async def populate_from_subjects(self) -> Dict[str, Any]:
        """Populate schedules table with preliminary entries based on subjects
        
        This creates initial schedule entries for each subject in the database,
        allowing users to modify dates and times later
        
        Returns:
            Dict[str, Any]: Statistics about the population process
        """
        pass
