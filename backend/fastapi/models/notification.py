from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    dateSent = Column(DateTime, default=func.now(), nullable=False)
    status = Column(String, nullable=False)  # ex: 'trimis', 'citit'
    
    # Relationships
    user = relationship("User")
