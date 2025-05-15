from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Config(Base):
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)
