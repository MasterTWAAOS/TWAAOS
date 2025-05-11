from abc import ABC, abstractmethod
from typing import List, Optional
from models.group import Group

class IGroupRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Group]:
        pass

    @abstractmethod
    def get_by_id(self, group_id: int) -> Optional[Group]:
        pass
        
    @abstractmethod
    def exists_by_id(self, group_id: int) -> bool:
        pass

    @abstractmethod
    def create(self, group: Group) -> Group:
        pass

    @abstractmethod
    def update(self, group: Group) -> Group:
        pass

    @abstractmethod
    def delete(self, group_id: int) -> bool:
        pass
