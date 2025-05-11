from abc import ABC, abstractmethod
from typing import List, Optional
from models.subject import Subject

class ISubjectRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Subject]:
        pass

    @abstractmethod
    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        pass
    
    @abstractmethod
    def get_by_group_id(self, group_id: int) -> List[Subject]:
        pass
    
    @abstractmethod
    def get_by_teacher_id(self, teacher_id: int) -> List[Subject]:
        pass

    @abstractmethod
    def create(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    def update(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    def delete(self, subject_id: int) -> bool:
        pass
