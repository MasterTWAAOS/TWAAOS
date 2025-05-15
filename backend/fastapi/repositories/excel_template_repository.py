from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from models.excel_template import ExcelTemplate
from models.DTOs.excel_template_dto import TemplateType
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository

class ExcelTemplateRepository(IExcelTemplateRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[ExcelTemplate]:
        result = await self.db.execute(select(ExcelTemplate))
        return result.scalars().all()

    async def get_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        result = await self.db.execute(select(ExcelTemplate).filter(ExcelTemplate.id == template_id))
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[ExcelTemplate]:
        result = await self.db.execute(select(ExcelTemplate).filter(ExcelTemplate.name == name))
        return result.scalar_one_or_none()
        
    async def get_by_group_and_type(self, group_id: int, template_type: TemplateType) -> Optional[ExcelTemplate]:
        result = await self.db.execute(
            select(ExcelTemplate)
            .filter(ExcelTemplate.groupId == group_id)
            .filter(ExcelTemplate.type == template_type)
        )
        return result.scalar_one_or_none()
        
    async def get_file_by_id(self, template_id: int) -> Optional[bytes]:
        result = await self.db.execute(
            select(ExcelTemplate.file)
            .filter(ExcelTemplate.id == template_id)
        )
        file_data = result.scalar_one_or_none()
        return file_data

    async def create(self, 
                   name: str, 
                   file_content: bytes, 
                   template_type: TemplateType, 
                   group_id: Optional[int] = None, 
                   description: Optional[str] = None) -> ExcelTemplate:
        # Create a new template object
        template = ExcelTemplate(
            name=name,
            type=template_type,
            groupId=group_id,
            file=file_content,
            description=description
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def update(self, 
                   template_id: int, 
                   name: Optional[str] = None,
                   file_content: Optional[bytes] = None, 
                   template_type: Optional[TemplateType] = None, 
                   group_id: Optional[int] = None, 
                   description: Optional[str] = None) -> ExcelTemplate:
        # Get existing template
        template = await self.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with id {template_id} not found")
            
        # Update fields if provided
        if name is not None:
            template.name = name
        if template_type is not None:
            template.type = template_type
        if group_id is not None:
            template.groupId = group_id
        if file_content is not None:
            template.file = file_content
        if description is not None:
            template.description = description
            
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete(self, template_id: int) -> bool:
        template = await self.get_by_id(template_id)
        if template:
            await self.db.delete(template)
            await self.db.commit()
            return True
        return False
