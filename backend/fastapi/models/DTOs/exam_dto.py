from typing import List, Optional
from pydantic import BaseModel
from datetime import date, time

class ExamResponse(BaseModel):
    """Response model for exam data with associated group, subject and teacher information"""
    id: int
    subjectId: int
    subjectName: str
    subjectShortName: str
    teacherId: int
    teacherName: str
    teacherEmail: str
    teacherPhone: Optional[str]
    roomId: int
    roomName: str
    date: date
    startTime: time
    endTime: time
    duration: int  # calculated field in hours
    status: str
    notes: Optional[str] = None
    # Group information
    groupId: int
    groupName: str
    specializationShortName: str
    studyYear: int
    
    class Config:
        from_attributes = True
