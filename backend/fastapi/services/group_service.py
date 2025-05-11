from typing import List, Optional

from models.group import Group
from models.DTOs.group_dto import GroupCreate, GroupUpdate, GroupResponse
from repositories.abstract.group_repository_interface import IGroupRepository
from services.abstract.group_service_interface import IGroupService

class GroupService(IGroupService):
    def __init__(self, group_repository: IGroupRepository):
        self.group_repository = group_repository

    def get_all_groups(self) -> List[GroupResponse]:
        groups = self.group_repository.get_all()
        return [GroupResponse.model_validate(group) for group in groups]

    def get_group_by_id(self, group_id: int) -> Optional[GroupResponse]:
        group = self.group_repository.get_by_id(group_id)
        if group:
            return GroupResponse.model_validate(group)
        return None

    def create_group(self, group_data: GroupCreate) -> GroupResponse:
        # Create new group object
        group = Group(
            name=group_data.name,
            studyYear=group_data.studyYear,
            specializationShortName=group_data.specializationShortName
        )
        
        # Save to database
        created_group = self.group_repository.create(group)
        return GroupResponse.model_validate(created_group)

    def update_group(self, group_id: int, group_data: GroupUpdate) -> Optional[GroupResponse]:
        group = self.group_repository.get_by_id(group_id)
        if not group:
            return None
            
        # Update group fields if provided
        if group_data.name is not None:
            group.name = group_data.name
        if group_data.studyYear is not None:
            group.studyYear = group_data.studyYear
        if group_data.specializationShortName is not None:
            group.specializationShortName = group_data.specializationShortName
            
        # Save changes
        updated_group = self.group_repository.update(group)
        return GroupResponse.model_validate(updated_group)

    def delete_group(self, group_id: int) -> bool:
        return self.group_repository.delete(group_id)
        
    def delete_all_groups(self) -> int:
        """Delete all groups from the database.
        
        Returns:
            int: The number of groups deleted
        """
        return self.group_repository.delete_all()
