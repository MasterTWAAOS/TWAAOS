from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from models.excel_template import ExcelTemplate
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

    async def create(self, template: ExcelTemplate) -> ExcelTemplate:
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def update(self, template: ExcelTemplate) -> ExcelTemplate:
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
