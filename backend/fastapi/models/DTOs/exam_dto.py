from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, validator, model_validator, field_serializer
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
    roomIds: List[int] = Field(default_factory=list)
    roomNames: List[str] = Field(default_factory=list)
    # For backward compatibility
    roomId: Optional[int] = None
    roomName: Optional[str] = None
    
    @model_validator(mode='before')
    @classmethod
    def handle_room_ids(cls, data: Any) -> Any:
        """Support both legacy roomId and new roomIds list"""
        if isinstance(data, dict):
            # If roomIds is missing but roomId is present, create roomIds from roomId
            if 'roomId' in data and data['roomId'] and 'roomIds' not in data:
                data['roomIds'] = [data['roomId']]
            # Ensure roomIds is a list
            if 'roomIds' in data and data['roomIds'] is None:
                data['roomIds'] = []
        return data
    date: Optional[Union[date, str]] = None  # Accept either date object or string
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
        "from_attributes": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True  # Allow more flexible typing
    }
    
    # Serialize date field correctly
    @field_serializer('date')
    def serialize_date(self, date_value: Optional[Union[date, str]]) -> Optional[str]:
        if date_value is None:
            return None
        if isinstance(date_value, str):
            return date_value
        if isinstance(date_value, date):
            return date_value.isoformat()
        return str(date_value)
    
    # Process incoming data before validation
    @model_validator(mode='before')
    @classmethod
    def validate_dates(cls, data: Any) -> Any:
        """Pre-process date fields to ensure compatibility"""
        if isinstance(data, dict) and 'date' in data:
            # Handle empty values
            if data['date'] in (None, '', 'None', 'null'):
                data['date'] = None
            # If it's a date object, convert it to string (isoformat)
            elif isinstance(data['date'], date):
                data['date'] = data['date'].isoformat()
        return data

class ExamUpdateRequest(BaseModel):
    """Request model for updating exam information"""
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    roomIds: Optional[List[int]] = None
    # For backward compatibility
    roomId: Optional[int] = None
    teacherId: Optional[int] = None
    groups: Optional[List[int]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    
    @model_validator(mode='before')
    @classmethod
    def handle_room_ids(cls, data: Any) -> Any:
        """Support both legacy roomId and new roomIds list"""
        if isinstance(data, dict):
            # If roomIds is missing but roomId is present, create roomIds from roomId
            if 'roomId' in data and data['roomId'] is not None and ('roomIds' not in data or not data.get('roomIds')):
                data['roomIds'] = [data['roomId']]
        return data
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-06-15",
                "startTime": "10:00:00",
                "endTime": "12:00:00",
                "roomIds": [1, 2],
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
    startTime: Optional[time] = None
    endTime: Optional[time] = None
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
