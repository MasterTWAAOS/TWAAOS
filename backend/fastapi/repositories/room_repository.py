from sqlalchemy.orm import Session
from typing import List, Optional

from models.room import Room
from repositories.abstract.room_repository_interface import IRoomRepository

class RoomRepository(IRoomRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Room]:
        return self.db.query(Room).all()

    def get_by_id(self, room_id: int) -> Optional[Room]:
        return self.db.query(Room).filter(Room.id == room_id).first()
    
    def get_by_building(self, building_name: str) -> List[Room]:
        return self.db.query(Room).filter(Room.buildingName == building_name).all()

    def create(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def update(self, room: Room) -> Room:
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete(self, room_id: int) -> bool:
        room = self.get_by_id(room_id)
        if room:
            self.db.delete(room)
            self.db.commit()
            return True
        return False
