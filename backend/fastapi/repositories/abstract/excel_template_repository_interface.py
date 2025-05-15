from abc import ABC, abstractmethod
from typing import List, Optional, BinaryIO
from models.excel_template import ExcelTemplate
from models.DTOs.excel_template_dto import TemplateType

class IExcelTemplateRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[ExcelTemplate]:
        """Get all excel templates"""
        pass

    @abstractmethod
    async def get_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        """Get template by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ExcelTemplate]:
        """Get template by name"""
        pass
        
    @abstractmethod
    async def get_by_group_and_type(self, group_id: int, template_type: TemplateType) -> Optional[ExcelTemplate]:
        """Get template by group ID and type"""
        pass
        
    @abstractmethod
    async def get_file_by_id(self, template_id: int) -> Optional[bytes]:
        """Get the actual Excel file content by template ID"""
        pass

    @abstractmethod
    async def create(self, 
                   name: str, 
                   file_content: bytes, 
                   template_type: TemplateType, 
                   group_id: Optional[int] = None, 
                   description: Optional[str] = None) -> ExcelTemplate:
        """Create a new template with the given file content"""
        pass

    @abstractmethod
    async def update(self, 
                   template_id: int, 
                   name: Optional[str] = None,
                   file_content: Optional[bytes] = None, 
                   template_type: Optional[TemplateType] = None, 
                   group_id: Optional[int] = None, 
                   description: Optional[str] = None) -> ExcelTemplate:
        """Update an existing template"""
        pass

    @abstractmethod
    async def delete(self, template_id: int) -> bool:
        """Delete a template"""
        pass
