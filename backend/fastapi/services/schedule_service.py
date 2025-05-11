from typing import List, Optional
from datetime import date

from models.schedule import Schedule
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from repositories.abstract.schedule_repository_interface import IScheduleRepository
from services.abstract.schedule_service_interface import IScheduleService

class ScheduleService(IScheduleService):
    def __init__(self, schedule_repository: IScheduleRepository):
        self.schedule_repository = schedule_repository

    def get_all_schedules(self) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_all()
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleResponse]:
        schedule = self.schedule_repository.get_by_id(schedule_id)
        if schedule:
            return ScheduleResponse.model_validate(schedule)
        return None
    
    def get_schedules_by_group_id(self, group_id: int) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_group_id(group_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    def get_schedules_by_teacher_id(self, teacher_id: int) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_teacher_id(teacher_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    def get_schedules_by_room_id(self, room_id: int) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_room_id(room_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    def get_schedules_by_subject_id(self, subject_id: int) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_subject_id(subject_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    def get_schedules_by_date(self, schedule_date: date) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_date(schedule_date)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    def get_schedules_by_status(self, status: str) -> List[ScheduleResponse]:
        schedules = self.schedule_repository.get_by_status(status)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    def create_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        # Create new schedule object
        schedule = Schedule(
            subjectId=schedule_data.subjectId,
            teacherId=schedule_data.teacherId,
            roomId=schedule_data.roomId,
            groupId=schedule_data.groupId,
            date=schedule_data.date,
            startTime=schedule_data.startTime,
            endTime=schedule_data.endTime,
            status=schedule_data.status
        )
        
        # Save to database
        created_schedule = self.schedule_repository.create(schedule)
        return ScheduleResponse.model_validate(created_schedule)

    def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[ScheduleResponse]:
        schedule = self.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return None
            
        # Update schedule fields if provided
        if schedule_data.subjectId is not None:
            schedule.subjectId = schedule_data.subjectId
        if schedule_data.teacherId is not None:
            schedule.teacherId = schedule_data.teacherId
        if schedule_data.roomId is not None:
            schedule.roomId = schedule_data.roomId
        if schedule_data.groupId is not None:
            schedule.groupId = schedule_data.groupId
        if schedule_data.date is not None:
            schedule.date = schedule_data.date
        if schedule_data.startTime is not None:
            schedule.startTime = schedule_data.startTime
        if schedule_data.endTime is not None:
            schedule.endTime = schedule_data.endTime
        if schedule_data.status is not None:
            schedule.status = schedule_data.status
            
        # Save changes
        updated_schedule = self.schedule_repository.update(schedule)
        return ScheduleResponse.model_validate(updated_schedule)

    def delete_schedule(self, schedule_id: int) -> bool:
        return self.schedule_repository.delete(schedule_id)
