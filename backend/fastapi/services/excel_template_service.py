from typing import List, Optional

from models.excel_template import ExcelTemplate
from models.DTOs.excel_template_dto import ExcelTemplateCreate, ExcelTemplateUpdate, ExcelTemplateResponse
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository
from services.abstract.excel_template_service_interface import IExcelTemplateService

class ExcelTemplateService(IExcelTemplateService):
    def __init__(self, template_repository: IExcelTemplateRepository):
        self.template_repository = template_repository

    def get_all_templates(self) -> List[ExcelTemplateResponse]:
        templates = self.template_repository.get_all()
        return [ExcelTemplateResponse.model_validate(template) for template in templates]

    def get_template_by_id(self, template_id: int) -> Optional[ExcelTemplateResponse]:
        template = self.template_repository.get_by_id(template_id)
        if template:
            return ExcelTemplateResponse.model_validate(template)
        return None
    
    def get_template_by_name(self, name: str) -> Optional[ExcelTemplateResponse]:
        template = self.template_repository.get_by_name(name)
        if template:
            return ExcelTemplateResponse.model_validate(template)
        return None

    def create_template(self, template_data: ExcelTemplateCreate) -> ExcelTemplateResponse:
        # Create new template object
        template = ExcelTemplate(
            name=template_data.name,
            filePath=template_data.filePath,
            description=template_data.description
        )
        
        # Save to database
        created_template = self.template_repository.create(template)
        return ExcelTemplateResponse.model_validate(created_template)

    def update_template(self, template_id: int, template_data: ExcelTemplateUpdate) -> Optional[ExcelTemplateResponse]:
        template = self.template_repository.get_by_id(template_id)
        if not template:
            return None
            
        # Update template fields if provided
        if template_data.name is not None:
            template.name = template_data.name
        if template_data.filePath is not None:
            template.filePath = template_data.filePath
        if template_data.description is not None:
            template.description = template_data.description
            
        # Save changes
        updated_template = self.template_repository.update(template)
        return ExcelTemplateResponse.model_validate(updated_template)

    def delete_template(self, template_id: int) -> bool:
        return self.template_repository.delete(template_id)
