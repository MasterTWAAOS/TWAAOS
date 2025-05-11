from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import exists

from models.group import Group
from repositories.abstract.group_repository_interface import IGroupRepository

class GroupRepository(IGroupRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Group]:
        return self.db.query(Group).all()

    def get_by_id(self, group_id: int) -> Optional[Group]:
        return self.db.query(Group).filter(Group.id == group_id).first()
        
    def exists_by_id(self, group_id: int) -> bool:
        # Returns True if the group_id exists, False otherwise
        # We use exists() and scalar() for efficiency instead of fetching the whole object
        return self.db.query(
            exists().where(Group.id == group_id)
        ).scalar()

    def create(self, group: Group) -> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def update(self, group: Group) -> Group:
        self.db.commit()
        self.db.refresh(group)
        return group

    def delete(self, group_id: int) -> bool:
        group = self.get_by_id(group_id)
        if group:
            self.db.delete(group)
            self.db.commit()
            return True
        return False
