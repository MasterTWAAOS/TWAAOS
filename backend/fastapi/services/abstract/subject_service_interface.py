from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse

class ISubjectService(ABC):
    @abstractmethod
    async def get_all_subjects(self) -> List[SubjectResponse]:
        pass

    @abstractmethod
    async def get_subject_by_id(self, subject_id: int) -> Optional[SubjectResponse]:
        pass
    
    @abstractmethod
    async def get_subjects_by_group_id(self, group_id: int) -> List[SubjectResponse]:
        pass
    
    @abstractmethod
    async def get_subjects_by_teacher_id(self, teacher_id: int) -> List[SubjectResponse]:
        pass
        
    @abstractmethod
    async def get_subjects_by_assistant_id(self, assistant_id: int) -> List[SubjectResponse]:
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
    async def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:  
        pass
        
    @abstractmethod
    async def validate_assistant_id(self, assistant_id: int) -> Tuple[bool, Optional[str]]:  
        pass
    
    @abstractmethod
    async def get_subject_with_teacher(self, subject_id: int):
        """Get a subject with its teacher relationship loaded.
        
        Args:
            subject_id (int): The ID of the subject to fetch
            
        Returns:
            Subject: The subject with teacher relationship populated
        """
        pass

    @abstractmethod
    async def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        pass

    @abstractmethod
    async def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[SubjectResponse]:
        pass

    @abstractmethod
    async def delete_subject(self, subject_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all_subjects(self) -> int:
        """Delete all subjects from the database
        
        Returns:
            int: Number of subjects deleted
        """
        pass
        
    @abstractmethod
    async def get_subject_with_teacher(self, subject_id: int):
        """Get a subject with its teacher relationship fully loaded.
        
        Args:
            subject_id: ID of the subject to retrieve
            
        Returns:
            The subject model with teacher relationship loaded, or None if not found
        """
        pass
        
    @abstractmethod
    async def get_group_by_id(self, group_id: int):
        """Get a group by its ID.
        
        Args:
            group_id: ID of the group to retrieve
            
        Returns:
            The group model or None if not found
        """
        pass
