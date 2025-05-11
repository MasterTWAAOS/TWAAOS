from sqlalchemy.orm import Session
from typing import List, Optional

from models.subject import Subject
from repositories.abstract.subject_repository_interface import ISubjectRepository

class SubjectRepository(ISubjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Subject]:
        return self.db.query(Subject).all()

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()
    
    def get_by_group_id(self, group_id: int) -> List[Subject]:
        return self.db.query(Subject).filter(Subject.groupId == group_id).all()
    
    def get_by_teacher_id(self, teacher_id: int) -> List[Subject]:
        return self.db.query(Subject).filter(Subject.teacherId == teacher_id).all()

    def create(self, subject: Subject) -> Subject:
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def update(self, subject: Subject) -> Subject:
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def delete(self, subject_id: int) -> bool:
        subject = self.get_by_id(subject_id)
        if subject:
            self.db.delete(subject)
            self.db.commit()
            return True
        return False
