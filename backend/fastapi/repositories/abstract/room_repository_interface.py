from abc import ABC, abstractmethod
from typing import List, Optional
from models.room import Room

class IRoomRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Room]:
        pass

    @abstractmethod
    def get_by_id(self, room_id: int) -> Optional[Room]:
        pass
    
    @abstractmethod
    def get_by_building(self, building_name: str) -> List[Room]:
        pass

    @abstractmethod
    def create(self, room: Room) -> Room:
        pass

    @abstractmethod
    def update(self, room: Room) -> Room:
        pass

    @abstractmethod
    def delete(self, room_id: int) -> bool:
        pass
