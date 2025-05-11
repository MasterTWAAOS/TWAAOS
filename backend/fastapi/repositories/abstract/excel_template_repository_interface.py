from abc import ABC, abstractmethod
from typing import List, Optional
from models.excel_template import ExcelTemplate

class IExcelTemplateRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[ExcelTemplate]:
        pass

    @abstractmethod
    def get_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[ExcelTemplate]:
        pass

    @abstractmethod
    def create(self, template: ExcelTemplate) -> ExcelTemplate:
        pass

    @abstractmethod
    def update(self, template: ExcelTemplate) -> ExcelTemplate:
        pass

    @abstractmethod
    def delete(self, template_id: int) -> bool:
        pass
