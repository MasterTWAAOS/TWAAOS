from abc import ABC, abstractmethod
from typing import List, Optional
from models.DTOs.group_dto import GroupCreate, GroupUpdate, GroupResponse

class IGroupService(ABC):
    @abstractmethod
    def get_all_groups(self) -> List[GroupResponse]:
        pass

    @abstractmethod
    def get_group_by_id(self, group_id: int) -> Optional[GroupResponse]:
        pass

    @abstractmethod
    def create_group(self, group_data: GroupCreate) -> GroupResponse:
        pass

    @abstractmethod
    def update_group(self, group_id: int, group_data: GroupUpdate) -> Optional[GroupResponse]:
        pass

    @abstractmethod
    def delete_group(self, group_id: int) -> bool:
        pass
