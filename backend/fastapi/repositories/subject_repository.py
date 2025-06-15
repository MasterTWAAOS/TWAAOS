from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.future import select
import logging

from models.subject import Subject
from repositories.abstract.subject_repository_interface import ISubjectRepository

logger = logging.getLogger(__name__)

class SubjectRepository(ISubjectRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Subject]:
        result = await self.db.execute(select(Subject))
        return result.scalars().all()

    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        result = await self.db.execute(select(Subject).filter(Subject.id == subject_id))
        return result.scalars().first()
    
    async def get_by_group_id(self, group_id: int) -> List[Subject]:
        result = await self.db.execute(select(Subject).filter(Subject.groupId == group_id))
        return result.scalars().all()
    
    async def get_by_teacher_id(self, teacher_id: int) -> List[Subject]:
        result = await self.db.execute(select(Subject).filter(Subject.teacherId == teacher_id))
        return result.scalars().all()
        
    async def get_subject_with_teacher(self, subject_id: int) -> Optional[Subject]:
        """Get a subject by ID with its teacher relationship loaded.
        
        Args:
            subject_id (int): The subject ID
            
        Returns:
            Optional[Subject]: The subject with teacher relationship or None
        """
        from sqlalchemy.orm import joinedload
        from models.user import User
        
        # Use joinedload to eagerly load the teacher relationship
        query = select(Subject).options(
            joinedload(Subject.teacher)
        ).filter(Subject.id == subject_id)
        
        result = await self.db.execute(query)
        return result.scalars().first()
        
    async def get_by_assistant_id(self, assistant_id: int) -> List[Subject]:
        # Use JSON containment to find subjects where the assistant ID is in the assistantIds array
        from sqlalchemy import text
        
        # In PostgreSQL, we need to check if the array contains the value
        # Use the ? operator to check if the value exists in the JSON array
        query = select(Subject).where(
            text(f"assistantIds @> '[{assistant_id}]'::jsonb")
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, subject: Subject) -> Subject:
        try:
            self.db.add(subject)
            await self.db.commit()
            await self.db.refresh(subject)
            return subject
        except Exception as e:
            # Roll back the transaction in case of any error
            await self.db.rollback()
            # Re-raise the exception after rollback
            raise e

    async def update(self, subject: Subject) -> Subject:
        try:
            await self.db.commit()
            await self.db.refresh(subject)
            return subject
        except Exception as e:
            # Roll back the transaction in case of any error
            await self.db.rollback()
            # Re-raise the exception after rollback
            raise e

    async def delete(self, subject_id: int) -> bool:
        try:
            subject = await self.get_by_id(subject_id)
            if subject:
                # Clear assistant relationships first to avoid FK issues
                if hasattr(subject, 'assistants') and subject.assistants:
                    subject.assistants = []
                    await self.db.flush()
                    
                # Now delete the subject - IMPORTANT: must use await here
                await self.db.delete(subject)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            # Roll back the transaction in case of any error
            await self.db.rollback()
            # Re-raise the exception after rollback
            raise e
            
    async def update_teacher_for_group_subjects(self, group_id: int, teacher_id: int) -> int:
        """Update the teacherId for all subjects assigned to a specific group.
        
        Args:
            group_id (int): The ID of the group whose subjects will be updated
            teacher_id (int): The new teacher ID to set for these subjects
            
        Returns:
            int: The number of subjects updated
        """
        try:
            # First get all subjects for this group
            subjects = await self.get_by_group_id(group_id)
            count = len(subjects)
            logger.info(f"Found {count} subjects for group ID {group_id} to update teacher to ID {teacher_id}")
            
            # Update each subject's teacherId
            for subject in subjects:
                subject.teacherId = teacher_id
                
            # Commit the changes
            await self.db.commit()
            logger.info(f"Successfully updated {count} subjects with new teacher ID {teacher_id}")
            return count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating teacher ID for group subjects: {str(e)}")
            raise e
    
    async def delete_all(self) -> int:
        """Delete all subjects from the database using a direct SQL DELETE statement.
        
        This method handles clearing relationships and foreign key constraints before deletion.
        
        Returns:
            int: The number of subjects deleted
        """
        # Get count first
        result = await self.db.execute(select(Subject))
        subjects = result.scalars().all()
        count = len(subjects)
        
        # Delete all subjects
        await self.db.execute(delete(Subject))
        await self.db.commit()
        return count
