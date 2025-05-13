from abc import ABC, abstractmethod
from typing import List, Optional
from models.room import Room

class IRoomRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Room]:
        pass

    @abstractmethod
    async def get_by_id(self, room_id: int) -> Optional[Room]:
        pass
    
    @abstractmethod
    async def get_by_building(self, building_name: str) -> List[Room]:
        pass

    @abstractmethod
    async def create(self, room: Room) -> Room:
        pass

    @abstractmethod
    async def update(self, room: Room) -> Room:
        pass

    @abstractmethod
    async def delete(self, room_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all(self) -> int:
        """Delete all rooms from the database.
        
        Returns:
            int: The number of rooms deleted
        """
        pass
