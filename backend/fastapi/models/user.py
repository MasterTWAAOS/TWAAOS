from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'SG', 'CD', 'SEC', 'ADM'
    groupId = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Only for SG users
    department = Column(String, nullable=True)  # For CD users
    phone = Column(String(15), nullable=True)  # Optional
    passwordHash = Column(String, nullable=True)  # Only for ADM users
    googleId = Column(String, unique=True, nullable=True)  # ID from Google JWT token
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="users")