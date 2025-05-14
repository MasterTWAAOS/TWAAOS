from pydantic import BaseModel
from typing import Optional, List

class SubjectBase(BaseModel):
    name: str
    shortName: str
    # Removed studyProgram and studyYear fields
    groupId: int
    teacherId: int
    assistantIds: List[int]  # Changed assistantId to assistantIds list

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    shortName: Optional[str] = None
    # Removed studyProgram and studyYear fields
    groupId: Optional[int] = None
    teacherId: Optional[int] = None
    assistantIds: Optional[List[int]] = None  # Changed assistantId to assistantIds list

class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True
