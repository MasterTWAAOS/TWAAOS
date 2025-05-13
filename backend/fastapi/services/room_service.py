from typing import List, Optional

from models.room import Room
from models.DTOs.room_dto import RoomCreate, RoomUpdate, RoomResponse
from repositories.abstract.room_repository_interface import IRoomRepository
from services.abstract.room_service_interface import IRoomService

class RoomService(IRoomService):
    def __init__(self, room_repository: IRoomRepository):
        self.room_repository = room_repository

    async def get_all_rooms(self) -> List[RoomResponse]:
        rooms = await self.room_repository.get_all()
        return [RoomResponse.model_validate(room) for room in rooms]

    async def get_room_by_id(self, room_id: int) -> Optional[RoomResponse]:
        room = await self.room_repository.get_by_id(room_id)
        if room:
            return RoomResponse.model_validate(room)
        return None
    
    async def get_rooms_by_building(self, building_name: str) -> List[RoomResponse]:
        rooms = await self.room_repository.get_by_building(building_name)
        return [RoomResponse.model_validate(room) for room in rooms]

    async def create_room(self, room_data: RoomCreate) -> RoomResponse:
        # Create new room object
        room = Room(
            name=room_data.name,
            shortName=room_data.shortName,
            buildingName=room_data.buildingName,
            capacity=room_data.capacity,
            computers=room_data.computers
        )
        
        # Save to database
        created_room = await self.room_repository.create(room)
        return RoomResponse.model_validate(created_room)

    async def update_room(self, room_id: int, room_data: RoomUpdate) -> Optional[RoomResponse]:
        room = await self.room_repository.get_by_id(room_id)
        if not room:
            return None
            
        # Update room fields if provided
        if room_data.name is not None:
            room.name = room_data.name
        if room_data.shortName is not None:
            room.shortName = room_data.shortName
        if room_data.buildingName is not None:
            room.buildingName = room_data.buildingName
        if room_data.capacity is not None:
            room.capacity = room_data.capacity
        if room_data.computers is not None:
            room.computers = room_data.computers
            
        # Save changes
        updated_room = await self.room_repository.update(room)
        return RoomResponse.model_validate(updated_room)

    async def delete_room(self, room_id: int) -> bool:
        return await self.room_repository.delete(room_id)
        
    async def delete_all_rooms(self) -> int:
        """Delete all rooms from the database.
        
        Returns:
            int: The number of rooms deleted
        """
        return await self.room_repository.delete_all()
