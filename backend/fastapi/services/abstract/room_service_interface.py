from abc import ABC, abstractmethod
from typing import List, Optional
from models.DTOs.room_dto import RoomCreate, RoomUpdate, RoomResponse

class IRoomService(ABC):
    @abstractmethod
    async def get_all_rooms(self) -> List[RoomResponse]:
        pass

    @abstractmethod
    async def get_room_by_id(self, room_id: int) -> Optional[RoomResponse]:
        pass
    
    @abstractmethod
    async def get_rooms_by_building(self, building_name: str) -> List[RoomResponse]:
        pass

    @abstractmethod
    async def create_room(self, room_data: RoomCreate) -> RoomResponse:
        pass

    @abstractmethod
    async def update_room(self, room_id: int, room_data: RoomUpdate) -> Optional[RoomResponse]:
        pass

    @abstractmethod
    async def delete_room(self, room_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all_rooms(self) -> int:
        """Delete all rooms from the database.
        
        Returns:
            int: The number of rooms deleted
        """
        pass
        
    @abstractmethod
    async def get_room_count(self) -> int:
        """Get the total count of rooms in the system.
        
        Returns:
            int: The total number of rooms
        """
        pass
