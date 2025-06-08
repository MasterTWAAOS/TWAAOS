from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
from enum import Enum

# Type enum for excel templates
class TemplateType(str, Enum):
    ROOM = "sali"  # Room schedule templates
    PROFESSOR = "cd"  # Professor schedule templates
    STUDENT = "sg"   # Student schedule templates
    EXAM = "exam"   # Exam report templates

class ExcelTemplateBase(BaseModel):
    name: str
    type: TemplateType
    groupId: Optional[int] = None
    description: Optional[str] = None

# For file upload and handling
class ExcelTemplateCreate(ExcelTemplateBase):
    # Note: file data is handled separately via FastAPI's File handling
    pass

class ExcelTemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TemplateType] = None
    groupId: Optional[int] = None
    description: Optional[str] = None

class ExcelTemplateResponse(ExcelTemplateBase):
    id: int
    uploaded_at: datetime
    # Note: file data is not returned in the response
    
    class Config:
        from_attributes = True
        use_enum_values = True  # Return enum values as strings
