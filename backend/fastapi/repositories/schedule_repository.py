from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from models.schedule import Schedule
from repositories.abstract.schedule_repository_interface import IScheduleRepository

class ScheduleRepository(IScheduleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Schedule]:
        return self.db.query(Schedule).all()

    def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        return self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    def get_by_group_id(self, group_id: int) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.groupId == group_id).all()
    
    def get_by_teacher_id(self, teacher_id: int) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.teacherId == teacher_id).all()
    
    def get_by_room_id(self, room_id: int) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.roomId == room_id).all()
    
    def get_by_subject_id(self, subject_id: int) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.subjectId == subject_id).all()
    
    def get_by_date(self, schedule_date: date) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.date == schedule_date).all()
    
    def get_by_status(self, status: str) -> List[Schedule]:
        return self.db.query(Schedule).filter(Schedule.status == status).all()

    def create(self, schedule: Schedule) -> Schedule:
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def update(self, schedule: Schedule) -> Schedule:
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete(self, schedule_id: int) -> bool:
        schedule = self.get_by_id(schedule_id)
        if schedule:
            self.db.delete(schedule)
            self.db.commit()
            return True
        return False
