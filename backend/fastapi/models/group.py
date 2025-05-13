from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.orm import relationship
from models.base import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    studyYear = Column(Integer, nullable=False)
    specializationShortName = Column(String, nullable=False)
    groupIds = Column(ARRAY(Integer), nullable=True)  # List of original IDs from USV API
    
    # Relationships
    users = relationship("User", back_populates="group")
    subjects = relationship("Subject", back_populates="group")
