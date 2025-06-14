from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    subjectId = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    roomId = Column(Integer, ForeignKey("rooms.id"), nullable=True)  # Now nullable for CD to set later
    date = Column(Date, nullable=True)  # Now nullable for SG to set later
    startTime = Column(Time, nullable=True)  # Now nullable for CD to set later
    endTime = Column(Time, nullable=True)  # Now nullable for CD to set later
    status = Column(String, nullable=True)  # ex: 'pending', 'proposed', 'approved', 'rejected', null means not ready but its not an label
    message = Column(String(200), nullable=True)  # New field for CD to give guidance to SG
    
    # Relationships
    subject = relationship("Subject", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
