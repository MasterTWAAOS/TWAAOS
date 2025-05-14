from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import Base
from typing import List, Optional

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    shortName = Column(String, nullable=False)
    # Removed studyProgram and studyYear fields as requested
    groupId = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacherId = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Store assistant IDs directly as a JSON array instead of using a relationship
    # This defaults to an empty list
    assistantIds = Column(JSON, nullable=False, default=list)
    
    # Relationships
    group = relationship("Group", back_populates="subjects")
    teacher = relationship("User", foreign_keys=[teacherId])
    schedules = relationship("Schedule", back_populates="subject")
    
    def get_assistant_ids(self) -> List[int]:
        """Get the list of assistant IDs
        
        Returns:
            List[int]: List of assistant IDs or empty list if None
        """
        return self.assistantIds or []
