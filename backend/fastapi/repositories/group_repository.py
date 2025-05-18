from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import exists, select, func, delete
from sqlalchemy.future import select

from models.group import Group
from repositories.abstract.group_repository_interface import IGroupRepository

class GroupRepository(IGroupRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Group]:
        result = await self.db.execute(select(Group))
        return result.scalars().all()

    async def get_by_id(self, group_id: int) -> Optional[Group]:
        result = await self.db.execute(select(Group).filter(Group.id == group_id))
        return result.scalars().first()
        
    async def get_by_name(self, name: str) -> Optional[Group]:
        """Get a group by its name.
        
        Args:
            name (str): The name of the group
            
        Returns:
            Optional[Group]: The group if found, None otherwise
        """
        result = await self.db.execute(select(Group).filter(Group.name == name))
        return result.scalars().first()
        
    async def exists_by_id(self, group_id: int) -> bool:
        # Returns True if the group_id exists, False otherwise
        # We use exists() and scalar() for efficiency instead of fetching the whole object
        stmt = select(exists().where(Group.id == group_id))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def create(self, group: Group) -> Group:
        try:
            self.db.add(group)
            # Explicitly commit the change to ensure data persistence
            # This is critical for operations like sync where we need to ensure
            # that each entity is saved before proceeding to dependent entities
            await self.db.flush()
            await self.db.commit()  # Explicitly commit the transaction
            await self.db.refresh(group)
            return group
        except Exception as e:
            # Log the error and rollback before re-raising
            import logging
            logging.error(f"Error in group repository create: {str(e)}")
            await self.db.rollback()  # Explicitly rollback on error
            raise
    async def update(self, group: Group) -> Group:
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete(self, group_id: int) -> bool:
        group = await self.get_by_id(group_id)
        if group:
            self.db.delete(group)
            await self.db.commit()
            return True
        return False
        
    async def delete_all(self) -> int:
        """Delete all groups from the database.
        
        Returns:
            int: The number of groups deleted
        """
        # Get count first
        count_stmt = select(func.count()).select_from(Group)
        count_result = await self.db.execute(count_stmt)
        count = count_result.scalar()
        
        # Delete all
        stmt = delete(Group)
        await self.db.execute(stmt)
        await self.db.commit()
        return count
