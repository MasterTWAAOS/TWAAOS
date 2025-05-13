from abc import ABC, abstractmethod
from typing import List, Optional
from models.DTOs.excel_template_dto import ExcelTemplateCreate, ExcelTemplateUpdate, ExcelTemplateResponse

class IExcelTemplateService(ABC):
    @abstractmethod
    async def get_all_templates(self) -> List[ExcelTemplateResponse]:
        pass

    @abstractmethod
    async def get_template_by_id(self, template_id: int) -> Optional[ExcelTemplateResponse]:
        pass
    
    @abstractmethod
    async def get_template_by_name(self, name: str) -> Optional[ExcelTemplateResponse]:
        pass

    @abstractmethod
    async def create_template(self, template_data: ExcelTemplateCreate) -> ExcelTemplateResponse:
        pass

    @abstractmethod
    async def update_template(self, template_id: int, template_data: ExcelTemplateUpdate) -> Optional[ExcelTemplateResponse]:
        pass

    @abstractmethod
    async def delete_template(self, template_id: int) -> bool:
        pass
