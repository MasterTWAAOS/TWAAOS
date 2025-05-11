from typing import List, Optional, Tuple
from datetime import date

from models.schedule import Schedule
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from repositories.abstract.schedule_repository_interface import IScheduleRepository
from repositories.abstract.subject_repository_interface import ISubjectRepository
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.room_repository_interface import IRoomRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from services.abstract.schedule_service_interface import IScheduleService

class ScheduleService(IScheduleService):
    def __init__(self, schedule_repository: IScheduleRepository,
                 subject_repository: ISubjectRepository,
                 user_repository: IUserRepository,
                 room_repository: IRoomRepository,
                 group_repository: IGroupRepository):
        self.schedule_repository = schedule_repository
        self.subject_repository = subject_repository
        self.user_repository = user_repository
        self.room_repository = room_repository
        self.group_repository = group_repository

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
        
    def validate_subject_id(self, subject_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the subject_id exists.
        
        Args:
            subject_id: The subject ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if subject exists
        subject = self.subject_repository.get_by_id(subject_id)
        if not subject:
            return False, f"Subject with ID {subject_id} does not exist"
        
        # All checks passed
        return True, None
        
    def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the teacher_id exists and belongs to a user with role 'CD'.
        
        Args:
            teacher_id: The teacher ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if teacher exists
        teacher = self.user_repository.get_by_id(teacher_id)
        if not teacher:
            return False, f"User with ID {teacher_id} does not exist"
            
        # Check if user is a teacher (CD role)
        if teacher.role != 'CD':
            return False, f"User with ID {teacher_id} is not a teacher (role 'CD')"
        
        # All checks passed
        return True, None
        
    def validate_room_id(self, room_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the room_id exists.
        
        Args:
            room_id: The room ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if room exists
        room = self.room_repository.get_by_id(room_id)
        if not room:
            return False, f"Room with ID {room_id} does not exist"
        
        # All checks passed
        return True, None
        
    def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the group_id exists.
        
        Args:
            group_id: The group ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if group exists
        if not self.group_repository.exists_by_id(group_id):
            return False, f"Group with ID {group_id} does not exist"
        
        # All checks passed
        return True, None

    def create_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        # Validate all foreign keys
        # Validate subject ID
        is_valid, error_message = self.validate_subject_id(schedule_data.subjectId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Validate teacher ID
        is_valid, error_message = self.validate_teacher_id(schedule_data.teacherId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Validate room ID
        is_valid, error_message = self.validate_room_id(schedule_data.roomId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Validate group ID
        is_valid, error_message = self.validate_group_id(schedule_data.groupId)
        if not is_valid:
            raise ValueError(error_message)
        
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
            
        # Validate foreign keys if provided
        if schedule_data.subjectId is not None:
            is_valid, error_message = self.validate_subject_id(schedule_data.subjectId)
            if not is_valid:
                raise ValueError(error_message)
                
        if schedule_data.teacherId is not None:
            is_valid, error_message = self.validate_teacher_id(schedule_data.teacherId)
            if not is_valid:
                raise ValueError(error_message)
                
        if schedule_data.roomId is not None:
            is_valid, error_message = self.validate_room_id(schedule_data.roomId)
            if not is_valid:
                raise ValueError(error_message)
                
        if schedule_data.groupId is not None:
            is_valid, error_message = self.validate_group_id(schedule_data.groupId)
            if not is_valid:
                raise ValueError(error_message)
            
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
