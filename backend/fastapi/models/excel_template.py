from sqlalchemy import Column, Integer, String, Text
from models.base import Base

class ExcelTemplate(Base):
    __tablename__ = "excel_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filePath = Column(String, nullable=False)
    description = Column(Text, nullable=True)
