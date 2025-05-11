from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)
    buildingName = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    computers = Column(Integer, nullable=False)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="room")
