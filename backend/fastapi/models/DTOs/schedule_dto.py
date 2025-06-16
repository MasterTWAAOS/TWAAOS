from pydantic import BaseModel, model_validator, field_validator, field_serializer
from typing import Optional, Dict, Any, List, Union
from datetime import date, time, datetime

class ScheduleBase(BaseModel):
    subjectId: int
    roomIds: Optional[List[int]] = None  # Store room IDs as a list
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None  # ex: 'pending', 'proposed', 'approved', 'rejected'
    message: Optional[str] = None  # New field for CD to give guidance to SG (up to 200 chars)

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    subjectId: Optional[int] = None
    roomIds: Optional[List[int]] = None  # List of room IDs
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None
    reason: Optional[str] = None  # Reason for rejection
    comments: Optional[str] = None  # Additional comments
    message: Optional[str] = None  # CD message to SG about preferred dates
    
    # Keep these for backward compatibility with frontend
    roomId: Optional[int] = None  # Primary room (kept for backward compatibility)
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
                "roomIds": [1182, 1183, 1184],  # Updated to use roomIds
                "assistantIds": [2001, 2002],
                "date": "2025-07-10",
                "startTime": "09:00:00",
                "endTime": "11:00:00",
                "status": "approved",
                "message": "Please schedule for early July if possible.",
                "sendEmail": True
            }
        }
    }
    
    # Process incoming data - combine roomId and additionalRoomIds into roomIds
    @model_validator(mode='before')
    @classmethod
    def combine_room_ids(cls, data):
        if isinstance(data, dict):
            # Initialize roomIds if not present
            if 'roomIds' not in data or data['roomIds'] is None:
                data['roomIds'] = []
            
            # Add primary roomId if provided
            if 'roomId' in data and data['roomId'] is not None:
                # Avoid duplication
                if data['roomId'] not in data['roomIds']:
                    data['roomIds'].append(data['roomId'])
            
            # Add additional room IDs if provided
            if 'additionalRoomIds' in data and data['additionalRoomIds'] is not None:
                for room_id in data['additionalRoomIds']:
                    # Avoid duplication
                    if room_id not in data['roomIds']:
                        data['roomIds'].append(room_id)
                        
        return data
    
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
    roomIds: Optional[List[int]] = None  # List of room IDs
    date: Optional[Union[date, str]] = None  # Accept either date object or string
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None
    message: Optional[str] = None
    # Include group name information
    groupId: Optional[int] = None
    groupName: Optional[str] = None
    
    # For backward compatibility
    roomId: Optional[int] = None
    
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
    
    # Set roomId for backward compatibility
    @model_validator(mode='before')
    @classmethod
    def set_backward_compatible_room_id(cls, data):
        """Set roomId from roomIds for backward compatibility"""
        if isinstance(data, dict):
            # If we have roomIds but no roomId
            if 'roomIds' in data and data['roomIds'] and ('roomId' not in data or data['roomId'] is None):
                # Set roomId to first room in roomIds list for backward compatibility
                data['roomId'] = data['roomIds'][0]
            # If we have roomId but no roomIds
            elif 'roomId' in data and data['roomId'] is not None and ('roomIds' not in data or not data['roomIds']):
                # Set roomIds to [roomId] for consistency
                data['roomIds'] = [data['roomId']]
        return data
    
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
