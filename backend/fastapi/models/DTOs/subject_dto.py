from pydantic import BaseModel
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    shortName: str
    studyProgram: str
    studyYear: int
    groupId: int
    teacherId: int

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    shortName: Optional[str] = None
    studyProgram: Optional[str] = None
    studyYear: Optional[int] = None
    groupId: Optional[int] = None
    teacherId: Optional[int] = None

class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True
