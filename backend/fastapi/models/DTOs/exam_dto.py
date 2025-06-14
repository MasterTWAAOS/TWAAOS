from typing import List, Optional
from pydantic import BaseModel, Field
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
    roomId: Optional[int] = None
    roomName: Optional[str] = None
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    duration: Optional[int] = None  # calculated field in hours
    status: Optional[str] = None
    message: Optional[str] = None  # New message field from CD to SG
    notes: Optional[str] = None
    # Group information
    groupId: int
    groupName: str
    specializationShortName: str
    studyYear: int
    
    model_config = {
        "from_attributes": True
    }

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
    
    model_config = {
        "json_schema_extra": {
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
    }

class ExamProposalRequest(BaseModel):
    """Request model for student group leader proposing an exam date"""
    subjectId: int
    date: date
    startTime: time
    endTime: time
    groupId: int
    notes: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "subjectId": 1,
                "date": "2025-06-15",
                "startTime": "10:00:00",
                "endTime": "12:00:00",
                "groupId": 1,
                "notes": "We prefer morning exams if possible"
            }
        }
    }
