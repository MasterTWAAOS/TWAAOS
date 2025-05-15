from abc import ABC, abstractmethod
from typing import List, Optional, BinaryIO
from fastapi import UploadFile
from models.DTOs.excel_template_dto import ExcelTemplateCreate, ExcelTemplateUpdate, ExcelTemplateResponse, TemplateType

class IExcelTemplateService(ABC):
    @abstractmethod
    async def get_all_templates(self) -> List[ExcelTemplateResponse]:
        """Get all templates"""
        pass

    @abstractmethod
    async def get_template_by_id(self, template_id: int) -> Optional[ExcelTemplateResponse]:
        """Get template by ID"""
        pass
    
    @abstractmethod
    async def get_template_by_name(self, name: str) -> Optional[ExcelTemplateResponse]:
        """Get template by name"""
        pass
        
    @abstractmethod
    async def get_template_by_group_and_type(self, group_id: int, template_type: TemplateType) -> Optional[ExcelTemplateResponse]:
        """Get template by group ID and type"""
        pass
        
    @abstractmethod
    async def get_file_by_id(self, template_id: int) -> Optional[bytes]:
        """Get the binary file content for a template"""
        pass

    @abstractmethod
    async def create_template(self, 
                            name: str,
                            file: UploadFile,
                            template_type: TemplateType,
                            group_id: Optional[int] = None,
                            description: Optional[str] = None) -> ExcelTemplateResponse:
        """Create a new template with file upload"""
        pass

    @abstractmethod
    async def update_template(self, 
                            template_id: int, 
                            name: Optional[str] = None,
                            file: Optional[UploadFile] = None,
                            template_type: Optional[TemplateType] = None,
                            group_id: Optional[int] = None,
                            description: Optional[str] = None) -> Optional[ExcelTemplateResponse]:
        """Update an existing template"""
        pass

    @abstractmethod
    async def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        pass
