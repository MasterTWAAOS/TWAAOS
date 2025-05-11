from sqlalchemy.orm import Session
from typing import List, Optional

from models.excel_template import ExcelTemplate
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository

class ExcelTemplateRepository(IExcelTemplateRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[ExcelTemplate]:
        return self.db.query(ExcelTemplate).all()

    def get_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        return self.db.query(ExcelTemplate).filter(ExcelTemplate.id == template_id).first()
    
    def get_by_name(self, name: str) -> Optional[ExcelTemplate]:
        return self.db.query(ExcelTemplate).filter(ExcelTemplate.name == name).first()

    def create(self, template: ExcelTemplate) -> ExcelTemplate:
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: ExcelTemplate) -> ExcelTemplate:
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: int) -> bool:
        template = self.get_by_id(template_id)
        if template:
            self.db.delete(template)
            self.db.commit()
            return True
        return False
