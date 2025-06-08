from typing import List, Optional
from fastapi import UploadFile, HTTPException
import io

from models.excel_template import ExcelTemplate
from models.DTOs.excel_template_dto import ExcelTemplateResponse, TemplateType
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository
from services.abstract.excel_template_service_interface import IExcelTemplateService

class ExcelTemplateService(IExcelTemplateService):
    def __init__(self, template_repository: IExcelTemplateRepository):
        self.template_repository = template_repository

    async def get_all_templates(self) -> List[ExcelTemplateResponse]:
        """Get all templates"""
        templates = await self.template_repository.get_all()
        return [ExcelTemplateResponse.model_validate(template) for template in templates]

    async def get_template_by_id(self, template_id: int) -> Optional[ExcelTemplateResponse]:
        """Get template by ID"""
        template = await self.template_repository.get_by_id(template_id)
        if template:
            return ExcelTemplateResponse.model_validate(template)
        return None
    
    async def get_template_by_name(self, name: str) -> Optional[ExcelTemplateResponse]:
        """Get template by name"""
        template = await self.template_repository.get_by_name(name)
        if template:
            return ExcelTemplateResponse.model_validate(template)
        return None
        
    async def get_template_by_group_and_type(self, group_id: int, template_type: TemplateType) -> Optional[ExcelTemplateResponse]:
        """Get template by group ID and type"""
        template = await self.template_repository.get_by_group_and_type(group_id, template_type)
        if template:
            return ExcelTemplateResponse.model_validate(template)
        return None
    
    async def get_templates_by_type(self, template_type: TemplateType, name: Optional[str] = None) -> List[ExcelTemplateResponse]:
        """Get templates by type, optionally filtered by name"""
        templates = await self.template_repository.get_by_type(template_type, name)
        return [ExcelTemplateResponse.model_validate(template) for template in templates]
        
    async def get_file_by_id(self, template_id: int) -> Optional[bytes]:
        """Get the binary file content for a template"""
        return await self.template_repository.get_file_by_id(template_id)

    async def create_template(self, 
                            name: str,
                            file: UploadFile,
                            template_type: TemplateType,
                            group_id: Optional[int] = None,
                            description: Optional[str] = None) -> ExcelTemplateResponse:
        """Create a new template with file upload"""
        # Validate file type
        if not self._is_valid_excel_file(file.filename):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx, .xls)")
            
        # Read file content
        file_content = await file.read()
        
        # Create template with binary file content
        created_template = await self.template_repository.create(
            name=name,
            file_content=file_content,
            template_type=template_type,
            group_id=group_id,
            description=description
        )
        
        return ExcelTemplateResponse.model_validate(created_template)

    async def create_template_from_bytes(self, 
                             name: str,
                             file_bytes: bytes,
                             template_type: TemplateType,
                             group_id: Optional[int] = None,
                             description: Optional[str] = None) -> ExcelTemplateResponse:
        """Create a new template from raw bytes data
        
        This method is specifically for internal generation of Excel files,
        not for handling user uploads through the API.
        """
        # Create template with binary file content
        created_template = await self.template_repository.create(
            name=name,
            file_content=file_bytes,
            template_type=template_type,
            group_id=group_id,
            description=description
        )
        
        return ExcelTemplateResponse.model_validate(created_template)

    async def update_template(self, 
                            template_id: int, 
                            name: Optional[str] = None,
                            file: Optional[UploadFile] = None,
                            template_type: Optional[TemplateType] = None,
                            group_id: Optional[int] = None,
                            description: Optional[str] = None) -> Optional[ExcelTemplateResponse]:
        """Update an existing template"""
        # Check if template exists
        template = await self.template_repository.get_by_id(template_id)
        if not template:
            return None
            
        # Process file if uploaded
        file_content = None
        if file is not None:
            # Validate file type
            if not self._is_valid_excel_file(file.filename):
                raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx, .xls)")
                
            # Read file content
            file_content = await file.read()
        
        # Update template with the new values
        updated_template = await self.template_repository.update(
            template_id=template_id,
            name=name,
            file_content=file_content,
            template_type=template_type,
            group_id=group_id, 
            description=description
        )
        
        return ExcelTemplateResponse.model_validate(updated_template)

    async def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        return await self.template_repository.delete(template_id)
    
    def _is_valid_excel_file(self, filename: str) -> bool:
        """Check if the file is a valid Excel file based on extension"""
        if not filename:
            return False
            
        # Check for valid Excel extensions
        valid_extensions = [".xlsx", ".xls", ".xlsm"]
        return any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    async def get_subject_teacher_data(self):
        """Fetch subject data with teacher information for exam Excel report
        
        Returns:
            list: A list of dictionaries containing subject and teacher data grouped by program, year, and group
        """
        print("[DEBUG] Service - get_subject_teacher_data: Starting execution")
        
        # Use the repository to fetch data from the database
        # This will join the subjects, groups, and users (teachers) tables
        print("[DEBUG] Service - Calling repository.get_subject_teacher_data()")
        query_result = await self.template_repository.get_subject_teacher_data()
        
        if not query_result:
            print("[DEBUG] Service - No data returned from repository")
            return []
        
        print(f"[DEBUG] Service - Repository returned {len(query_result)} items")
        
        # Format the data for the Excel report
        print("[DEBUG] Service - Formatting data for Excel report")
        formatted_data = []
        for i, item in enumerate(query_result):
            try:
                formatted_item = {
                    'specializationShortName': item.group.specializationShortName,
                    'studyYear': item.group.studyYear,
                    'groupName': item.group.name,
                    'subjectName': item.name,
                    'subjectShortName': item.shortName,
                    'teacherName': f"{item.teacher.lastName} {item.teacher.firstName}",
                    'teacherEmail': item.teacher.email,
                    'teacherPhone': item.teacher.phone or 'N/A'  # Fixed: using 'phone' instead of 'phoneNumber'
                }
                formatted_data.append(formatted_item)
            except Exception as e:
                print(f"[DEBUG] Service - Error formatting item {i}: {str(e)}")
                print(f"[DEBUG] Service - Item details: id={item.id}, name={item.name}")
                # Continue with next item
        
        print(f"[DEBUG] Service - Formatted {len(formatted_data)} items for Excel")
        if formatted_data:
            print(f"[DEBUG] Service - Sample item: {formatted_data[0]}")
        
        return formatted_data
        
    async def get_room_data(self):
        """Fetch room data for room Excel report
        
        Returns:
            list: A list of dictionaries containing room data sorted by building and room name
        """
        print("[DEBUG] Service - get_room_data: Starting execution")
        
        # Use the repository to fetch data from the database
        print("[DEBUG] Service - Calling repository.get_room_data()")
        query_result = await self.template_repository.get_room_data()
        
        if not query_result:
            print("[DEBUG] Service - No data returned from repository")
            return []
        
        print(f"[DEBUG] Service - Repository returned {len(query_result)} items")
        
        # Format the data for the Excel report
        print("[DEBUG] Service - Formatting data for Excel report")
        formatted_data = []
        for i, room in enumerate(query_result):
            try:
                formatted_item = {
                    'buildingName': room.buildingName,
                    'name': room.name,
                    'shortName': room.shortName,
                    'capacity': room.capacity,
                    'computers': 'Da' if room.computers else 'Nu'
                }
                formatted_data.append(formatted_item)
            except Exception as e:
                print(f"[DEBUG] Service - Error formatting item {i}: {str(e)}")
                print(f"[DEBUG] Service - Item details: id={room.id}, name={room.name if hasattr(room, 'name') else 'unknown'}")
                # Continue with next item
        
        print(f"[DEBUG] Service - Formatted {len(formatted_data)} items for Excel")
        if formatted_data:
            print(f"[DEBUG] Service - Sample item: {formatted_data[0]}")
        
        return formatted_data
