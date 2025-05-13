from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    subjectId = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    roomId = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    date = Column(Date, nullable=False)
    startTime = Column(Time, nullable=False)
    endTime = Column(Time, nullable=False)
    status = Column(String, nullable=False)  # ex: 'propus', 'acceptat', 'respins'
    
    # Relationships
    subject = relationship("Subject", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
