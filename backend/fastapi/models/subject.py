from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)
    studyProgram = Column(String, nullable=False)
    studyYear = Column(Integer, nullable=False)
    groupId = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacherId = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    group = relationship("Group", back_populates="subjects")
    teacher = relationship("User", foreign_keys=[teacherId])
    schedules = relationship("Schedule", back_populates="subject")
