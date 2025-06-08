from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from models.room import Room
from repositories.abstract.room_repository_interface import IRoomRepository

class RoomRepository(IRoomRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Room]:
        result = await self.db.execute(select(Room))
        return result.scalars().all()

    async def get_by_id(self, room_id: int) -> Optional[Room]:
        result = await self.db.execute(select(Room).filter(Room.id == room_id))
        return result.scalar_one_or_none()
    
    async def get_by_building(self, building_name: str) -> List[Room]:
        result = await self.db.execute(select(Room).filter(Room.buildingName == building_name))
        return result.scalars().all()

    async def create(self, room: Room) -> Room:
        try:
            self.db.add(room)
            # Explicitly commit the change to ensure data persistence
            # This is critical for operations like sync where we need to ensure
            # that each entity is saved before proceeding to dependent entities
            await self.db.flush()
            await self.db.commit()  # Explicitly commit the transaction
            await self.db.refresh(room)
            return room
        except Exception as e:
            # Log the error and rollback before re-raising
            import logging
            logging.error(f"Error in room repository create: {str(e)}")
            await self.db.rollback()  # Explicitly rollback on error
            raise

    async def update(self, room: Room) -> Room:
        try:
            # The commit is now handled by the database provider in the get_db function
            await self.db.flush()
            await self.db.refresh(room)
            return room
        except Exception as e:
            import logging
            logging.error(f"Error in room repository update: {str(e)}")
            raise

    async def delete(self, room_id: int) -> bool:
        try:
            room = await self.get_by_id(room_id)
            if room:
                await self.db.delete(room)
                # The commit is now handled by the database provider in the get_db function
                await self.db.flush()
                return True
            return False
        except Exception as e:
            import logging
            logging.error(f"Error in room repository delete: {str(e)}")
            raise
        
    async def delete_all(self) -> int:
        """Delete all rooms from the database.
        
        Returns:
            int: The number of rooms deleted
        """
        # Get count first
        result = await self.db.execute(select(Room))
        rooms = result.scalars().all()
        count = len(rooms)
        
        # Delete all rooms
        await self.db.execute(delete(Room))
        await self.db.commit()
        return count