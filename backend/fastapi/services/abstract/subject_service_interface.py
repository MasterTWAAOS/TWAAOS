from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse

class ISubjectService(ABC):
    @abstractmethod
    def get_all_subjects(self) -> List[SubjectResponse]:
        pass

    @abstractmethod
    def get_subject_by_id(self, subject_id: int) -> Optional[SubjectResponse]:
        pass
    
    @abstractmethod
    def get_subjects_by_group_id(self, group_id: int) -> List[SubjectResponse]:
        pass
    
    @abstractmethod
    def get_subjects_by_teacher_id(self, teacher_id: int) -> List[SubjectResponse]:
        pass
        
    @abstractmethod
    def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        pass
        
    @abstractmethod
    def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:  
        pass

    @abstractmethod
    def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        pass

    @abstractmethod
    def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[SubjectResponse]:
        pass

    @abstractmethod
    def delete_subject(self, subject_id: int) -> bool:
        pass
