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

class ExamUpdateRequest(BaseModel):
    """Request model for updating exam information"""
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    roomId: Optional[int] = None
    teacherId: Optional[int] = None
    groups: Optional[List[int]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-06-15",
                "startTime": "10:00:00",
                "endTime": "12:00:00",
                "roomId": 1,
                "teacherId": 5,
                "groups": [1, 2, 3],
                "status": "scheduled",
                "notes": "Exam rescheduled due to room availability"
            }
        }
