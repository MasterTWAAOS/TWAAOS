from abc import ABC, abstractmethod
from typing import List, Optional
from models.DTOs.group_dto import GroupCreate, GroupUpdate, GroupResponse

class IGroupService(ABC):
    @abstractmethod
    async def get_all_groups(self) -> List[GroupResponse]:
        pass

    @abstractmethod
    async def get_group_by_id(self, group_id: int) -> Optional[GroupResponse]:
        pass

    @abstractmethod
    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    async def update_group(self, group_id: int, group_data: GroupUpdate) -> Optional[GroupResponse]:
        pass

    @abstractmethod
    async def delete_group(self, group_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all_groups(self) -> int:
        """Delete all groups from the database.
        
        Returns:
            int: The number of groups deleted
        """
        pass
        
    @abstractmethod
    async def exists_by_id(self, group_id: int) -> bool:
        """Check if a group exists by its ID.
        
        Args:
            group_id: The ID of the group to check
            
        Returns:
            bool: True if the group exists, False otherwise
        """
        pass
