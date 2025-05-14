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
    async def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:  
        pass
        
    @abstractmethod
    async def validate_assistant_id(self, assistant_id: int) -> Tuple[bool, Optional[str]]:  
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
