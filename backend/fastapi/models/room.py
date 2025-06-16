from sqlalchemy import Column, Integer, String
from models.base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)
    buildingName = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    computers = Column(Integer, nullable=False)
    
    # No direct ORM relationship with Schedule
    # We're using a JSON array column in Schedule (roomIds), so we'll use repository methods
    # instead of SQLAlchemy relationships
