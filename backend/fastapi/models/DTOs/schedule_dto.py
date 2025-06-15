from pydantic import BaseModel, model_validator, field_validator, field_serializer
from typing import Optional, Dict, Any, List, Union
from datetime import date, time, datetime

class ScheduleBase(BaseModel):
    subjectId: int
    roomId: Optional[int] = None
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None  # ex: 'pending', 'proposed', 'approved', 'rejected'
    message: Optional[str] = None  # New field for CD to give guidance to SG (up to 200 chars)

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    subjectId: Optional[int] = None
    roomId: Optional[int] = None  # Primary room (kept for backward compatibility)
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None
    reason: Optional[str] = None  # Reason for rejection
    comments: Optional[str] = None  # Additional comments
    message: Optional[str] = None  # CD message to SG about preferred dates
    
    # New fields for CD functionality
    additionalRoomIds: Optional[list[int]] = None  # Additional rooms for the exam
    assistantIds: Optional[list[int]] = None  # Assistants assigned to the exam
    sendEmail: Optional[bool] = None  # Flag to trigger email notifications
    
    # Use proper Pydantic V2 config
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "subjectId": 986,
                "roomId": 1182,
                "additionalRoomIds": [1183, 1184],
                "assistantIds": [2001, 2002],
                "date": "2025-07-10",
                "startTime": "09:00:00",
                "endTime": "11:00:00",
                "status": "approved",
                "comments": "Exam approved with multiple rooms",
                "message": "Please schedule for early July if possible.",
                "sendEmail": True
            }
        }
    }
    
    # Time format validators using Pydantic V2 syntax
    @field_validator('startTime', 'endTime', mode='before')
    @classmethod
    def validate_time_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%H:%M:%S').time()
            except ValueError:
                try:
                    return datetime.strptime(v, '%H:%M').time()
                except ValueError:
                    raise ValueError(f"Invalid time format: {v}. Expected format: HH:MM:SS or HH:MM")
        return v

class ScheduleResponse(BaseModel):
    id: int
    subjectId: int
    roomId: Optional[int] = None
    date: Optional[Union[date, str]] = None  # Accept either date object or string
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None
    message: Optional[str] = None
    # Include group name information
    groupId: Optional[int] = None
    groupName: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True  # Allow more flexible typing
    }
    
    # Serialize date field correctly
    @field_serializer('date')
    def serialize_date(self, date_value: Optional[Union[date, str]]) -> Optional[str]:
        """Convert date to string format or None"""
        if date_value is None:
            return None
        if isinstance(date_value, str):
            return date_value
        if isinstance(date_value, date):
            return date_value.isoformat()
        return str(date_value)  # Fallback for any other type
    
    # Process incoming data before validation
    @model_validator(mode='before')
    @classmethod
    def validate_dates(cls, data: Any) -> Any:
        """Pre-process date fields to ensure compatibility"""
        if isinstance(data, dict) and 'date' in data:
            # Handle various null values
            if data['date'] in (None, '', 'None', 'null'):
                data['date'] = None
            # Convert date objects to ISO format strings
            elif isinstance(data['date'], date):
                data['date'] = data['date'].isoformat()
            # Keep strings as they are
        return data
