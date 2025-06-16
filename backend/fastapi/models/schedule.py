from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import Base
from typing import List, Optional

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    subjectId = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    # Replace single roomId with roomIds as JSON array
    roomIds = Column(JSON, nullable=True, default=list)  # Store room IDs as a JSON array
    date = Column(Date, nullable=True)  # Now nullable for SG to set later
    startTime = Column(Time, nullable=True)  # Now nullable for CD to set later
    endTime = Column(Time, nullable=True)  # Now nullable for CD to set later
    status = Column(String, nullable=True)  # ex: 'pending', 'proposed', 'approved', 'rejected', null means not ready but its not an label
    message = Column(String(200), nullable=True)  # New field for CD to give guidance to SG
    
    # Relationships
    subject = relationship("Subject", back_populates="schedules")
    
    # Helper method to get the list of room IDs
    def get_room_ids(self) -> List[int]:
        """Get the list of room IDs
        
        Returns:
            List[int]: List of room IDs or empty list if None
        """
        return self.roomIds or []
