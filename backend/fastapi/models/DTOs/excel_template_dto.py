from pydantic import BaseModel
from typing import Optional

class ExcelTemplateBase(BaseModel):
    name: str
    filePath: str
    description: Optional[str] = None

class ExcelTemplateCreate(ExcelTemplateBase):
    pass

class ExcelTemplateUpdate(BaseModel):
    name: Optional[str] = None
    filePath: Optional[str] = None
    description: Optional[str] = None

class ExcelTemplateResponse(ExcelTemplateBase):
    id: int

    class Config:
        from_attributes = True
