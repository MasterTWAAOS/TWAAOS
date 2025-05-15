from sqlalchemy import Column, Integer, String, Enum, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class ExcelTemplate(Base):
    __tablename__ = "excel_templates"

    id = Column(Integer, primary_key=True, index=True)
    groupId = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Can be null for templates not specific to a group
    type = Column(String, nullable=False)  # 'sali', 'cd', 'sg'
    name = Column(String, nullable=False)  # Name of the template
    file = Column(LargeBinary, nullable=False)  # Store the Excel file as binary data
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)  # Creation timestamp
    description = Column(String, nullable=True)
    
    # Relationship with Group
    group = relationship("Group", back_populates="excel_templates")
