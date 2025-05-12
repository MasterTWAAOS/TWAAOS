from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GroupBase(BaseModel):
    name: str
    studyYear: int
    specializationShortName: str
    groupIds: Optional[List[int]] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    studyYear: Optional[int] = None
    specializationShortName: Optional[str] = None
    groupIds: Optional[List[int]] = None

class GroupResponse(GroupBase):
    id: int

    class Config:
        from_attributes = True
