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
    async def get_by_assistant_id(self, assistant_id: int) -> List[Subject]:
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
