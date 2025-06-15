from abc import ABC, abstractmethod
from typing import List, Optional
from models.subject import Subject

class ISubjectRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Subject]:
        pass

    @abstractmethod
    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        pass
    
    @abstractmethod
    async def get_by_group_id(self, group_id: int) -> List[Subject]:
        pass
    
    @abstractmethod
    async def get_by_teacher_id(self, teacher_id: int) -> List[Subject]:
        pass
        
    @abstractmethod
    async def get_subject_with_teacher(self, subject_id: int) -> Optional[Subject]:
        """Get a subject by ID with its teacher relationship loaded.
        
        Args:
            subject_id (int): The subject ID
            
        Returns:
            Optional[Subject]: The subject with teacher relationship or None
        """
        pass
        
    @abstractmethod
    async def get_by_assistant_id(self, assistant_id: int) -> List[Subject]:
        pass
        
    @abstractmethod
    async def update_teacher_for_group_subjects(self, group_id: int, teacher_id: int) -> int:
        """Update the teacherId for all subjects assigned to a specific group.
        
        Args:
            group_id (int): The ID of the group whose subjects will be updated
            teacher_id (int): The new teacher ID to set for these subjects
            
        Returns:
            int: The number of subjects updated
        """
        pass

    @abstractmethod
    async def create(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    async def update(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    async def delete(self, subject_id: int) -> bool:
        pass
    
    @abstractmethod
    async def delete_all(self) -> int:
        pass
