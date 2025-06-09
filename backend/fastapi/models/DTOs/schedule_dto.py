from pydantic import BaseModel, model_validator, field_validator
from typing import Optional, Dict, Any
from datetime import date, time, datetime

class ScheduleBase(BaseModel):
    subjectId: int
    roomId: int
    date: date
    startTime: time
    endTime: time
    status: str  # ex: 'pending', 'proposed', 'approved', 'rejected'

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    subjectId: Optional[int] = None
    roomId: Optional[int] = None
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = None
    
    # Use proper Pydantic V2 config
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "subjectId": 986,
                "roomId": 1182,
                "date": "2025-07-10",
                "startTime": "09:00:00",
                "endTime": "11:00:00",
                "status": "proposed"
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

class ScheduleResponse(ScheduleBase):
    id: int

    class Config:
        from_attributes = True
