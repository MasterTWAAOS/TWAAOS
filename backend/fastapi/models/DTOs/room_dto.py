from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    name: str
    shortName: str
    buildingName: str
    capacity: int
    computers: int

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    shortName: Optional[str] = None
    buildingName: Optional[str] = None
    capacity: Optional[int] = None
    computers: Optional[int] = None

class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True
