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
    
    async def get_by_type(self, template_type: TemplateType, name: Optional[str] = None) -> List[ExcelTemplate]:
        query = select(ExcelTemplate).filter(ExcelTemplate.type == template_type)
        
        # Add name filter if provided
        if name:
            query = query.filter(ExcelTemplate.name.ilike(f"%{name}%"))
            
        result = await self.db.execute(query)
        return result.scalars().all()
        
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
    
    async def get_subject_teacher_data(self):
        """Get subject data with teacher information grouped by program, year, and group
        
        Returns:
            List: List of subjects with associated teacher and group data
        """
        print("[DEBUG] Repository - get_subject_teacher_data: Starting execution")
        
        from sqlalchemy import select, join
        from sqlalchemy.orm import joinedload, aliased
        from models.subject import Subject
        from models.group import Group
        from models.user import User
        
        # Create query to join Subject with Group and User (teacher)
        print("[DEBUG] Repository - Building query with Subject, Group, and User joins")
        
        # Using joinedload to eagerly load related Group and User (teacher) objects
        # This ensures we have all the data we need in one query
        query = (
            select(Subject)
            .options(
                joinedload(Subject.group),  # Loads the group relationship
                joinedload(Subject.teacher)  # Loads the teacher relationship
            )
        )
        
        # Execute the query
        print("[DEBUG] Repository - Executing database query")
        result = await self.db.execute(query)
        subjects = result.unique().scalars().all()
        
        # Log query results
        print(f"[DEBUG] Repository - Query returned {len(subjects)} subjects")
        if subjects:
            print(f"[DEBUG] Repository - First subject: id={subjects[0].id}, name={subjects[0].name}")
            try:
                print(f"[DEBUG] Repository - First subject group: {subjects[0].group.name if subjects[0].group else 'None'}")
            except Exception as e:
                print(f"[DEBUG] Repository - Error accessing group: {str(e)}")
            
            try:
                print(f"[DEBUG] Repository - First subject teacher: {subjects[0].teacher.lastName if subjects[0].teacher else 'None'} {subjects[0].teacher.firstName if subjects[0].teacher else ''}")
            except Exception as e:
                print(f"[DEBUG] Repository - Error accessing teacher: {str(e)}")
        
        # Sort the subjects by program, year, and group name using Python
        # This avoids SQL-level ordering issues
        try:
            sorted_subjects = sorted(
                subjects,
                key=lambda x: (
                    x.group.specializationShortName if x.group else '',
                    x.group.studyYear if x.group else 0,
                    x.group.name if x.group else ''
                )
            )
            print(f"[DEBUG] Repository - Successfully sorted {len(sorted_subjects)} subjects")
            return sorted_subjects
        except Exception as e:
            print(f"[DEBUG] Repository - Error sorting subjects: {str(e)}")
            # Return unsorted subjects if sorting fails
            return subjects
            
    async def get_room_data(self):
        """Get room data for Excel export
        
        Returns:
            List: List of rooms with their details
        """
        print("[DEBUG] Repository - get_room_data: Starting execution")
        
        from sqlalchemy import select
        from models.room import Room
        
        # Create query to select all rooms
        print("[DEBUG] Repository - Building query for rooms")
        query = select(Room)
        
        # Execute the query
        print("[DEBUG] Repository - Executing database query")
        result = await self.db.execute(query)
        rooms = result.scalars().all()
        
        # Log query results
        print(f"[DEBUG] Repository - Query returned {len(rooms)} rooms")
        
        # Sort the rooms by building name and room name using Python
        try:
            sorted_rooms = sorted(
                rooms,
                key=lambda x: (x.buildingName or '', x.name or '')
            )
            print(f"[DEBUG] Repository - Successfully sorted {len(sorted_rooms)} rooms")
            return sorted_rooms
        except Exception as e:
            print(f"[DEBUG] Repository - Error sorting rooms: {str(e)}")
            # Return unsorted rooms if sorting fails
            return rooms
