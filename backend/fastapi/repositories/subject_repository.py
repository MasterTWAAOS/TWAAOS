from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.future import select

from models.subject import Subject
from repositories.abstract.subject_repository_interface import ISubjectRepository

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
        
    async def get_by_assistant_id(self, assistant_id: int) -> List[Subject]:
        result = await self.db.execute(select(Subject).filter(Subject.assistantId == assistant_id))
        return result.scalars().all()

    async def create(self, subject: Subject) -> Subject:
        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)
        return subject

    async def update(self, subject: Subject) -> Subject:
        await self.db.commit()
        await self.db.refresh(subject)
        return subject

    async def delete(self, subject_id: int) -> bool:
        subject = await self.get_by_id(subject_id)
        if subject:
            self.db.delete(subject)
            await self.db.commit()
            return True
        return False
