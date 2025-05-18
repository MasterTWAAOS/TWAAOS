from abc import ABC, abstractmethod
from typing import List, Optional
from models.group import Group

class IGroupRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Group]:
        pass

    @abstractmethod
    async def get_by_id(self, group_id: int) -> Optional[Group]:
        pass
        
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Group]:
        """Get a group by its name.
        
        Args:
            name (str): The name of the group
            
        Returns:
            Optional[Group]: The group if found, None otherwise
        """
        pass
        
    @abstractmethod
    async def exists_by_id(self, group_id: int) -> bool:
        pass

    @abstractmethod
    async def create(self, group: Group) -> Group:
        pass

    @abstractmethod
    async def update(self, group: Group) -> Group:
        pass

    @abstractmethod
    async def delete(self, group_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all(self) -> int:
        """Delete all groups from the database.
        
        Returns:
            int: The number of groups deleted
        """
        pass
