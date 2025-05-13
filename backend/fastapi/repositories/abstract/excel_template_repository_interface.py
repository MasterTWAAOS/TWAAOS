from abc import ABC, abstractmethod
from typing import List, Optional
from models.excel_template import ExcelTemplate

class IExcelTemplateRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[ExcelTemplate]:
        pass

    @abstractmethod
    async def get_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ExcelTemplate]:
        pass

    @abstractmethod
    async def create(self, template: ExcelTemplate) -> ExcelTemplate:
        pass

    @abstractmethod
    async def update(self, template: ExcelTemplate) -> ExcelTemplate:
        pass

    @abstractmethod
    async def delete(self, template_id: int) -> bool:
        pass
