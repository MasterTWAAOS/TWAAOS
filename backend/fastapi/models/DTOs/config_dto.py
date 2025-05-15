from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConfigBase(BaseModel):
    startDate: datetime
    endDate: datetime

class ConfigCreate(ConfigBase):
    pass

class ConfigUpdate(BaseModel):
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None

class ConfigResponse(ConfigBase):
    id: int
    modified_at: datetime
    
    class Config:
        from_attributes = True
