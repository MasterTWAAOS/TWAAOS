from typing import List, Optional, Tuple, Dict, Any
from datetime import date
import logging

from models.schedule import Schedule
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse

logger = logging.getLogger(__name__)
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

    async def get_all_schedules(self) -> List[ScheduleResponse]:
        schedules = await self.schedule_repository.get_all()
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

    async def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleResponse]:
        schedule = await self.schedule_repository.get_by_id(schedule_id)
        if schedule:
            return ScheduleResponse.model_validate(schedule)
        return None
    
    # Method removed since groupId and assistantId are no longer used in the schedules table
    
    async def get_schedules_by_room_id(self, room_id: int) -> List[ScheduleResponse]:
        schedules = await self.schedule_repository.get_by_room_id(room_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    async def get_schedules_by_subject_id(self, subject_id: int) -> List[ScheduleResponse]:
        schedules = await self.schedule_repository.get_by_subject_id(subject_id)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    async def get_schedules_by_date(self, schedule_date: date) -> List[ScheduleResponse]:
        schedules = await self.schedule_repository.get_by_date(schedule_date)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
    
    async def get_schedules_by_status(self, status: str) -> List[ScheduleResponse]:
        schedules = await self.schedule_repository.get_by_status(status)
        return [ScheduleResponse.model_validate(schedule) for schedule in schedules]
        
    async def delete_all_schedules(self) -> int:
        """Delete all schedules from the database
        
        Returns:
            int: Number of deleted schedules
        """
        logger.info("[DEBUG] Service - delete_all_schedules: Starting execution")
        try:
            deleted_count = await self.schedule_repository.delete_all_schedules()
            logger.info(f"[DEBUG] Service - Deleted {deleted_count} schedules")
            return deleted_count
        except Exception as e:
            logger.error(f"[DEBUG] Service - Error deleting schedules: {str(e)}")
            raise
    
    async def populate_schedules_from_subjects(self) -> Dict[str, Any]:
        """Populate schedules table with preliminary entries based on subjects
        
        This creates initial schedule entries for each subject in the database,
        allowing users to modify dates and times later
        
        Returns:
            Dict[str, Any]: Statistics about the population process
        """
        logger.info("[DEBUG] Service - populate_schedules_from_subjects: Starting execution")
        try:
            stats = await self.schedule_repository.populate_from_subjects()
            logger.info(f"[DEBUG] Service - Populated schedules from subjects: "
                        f"Created {stats['created']} schedules, {stats['errors']} errors")
            return stats
        except Exception as e:
            logger.error(f"[DEBUG] Service - Error populating schedules: {str(e)}")
            raise
        
    async def get_schedules_by_group_id(self, group_id: int) -> List[ScheduleResponse]:
        # Since we don't have a direct relationship to groups in the Schedule model,
        # we need to get all schedules and filter them by checking the group_id relationship
        # through the related subjects
        all_schedules = await self.schedule_repository.get_all()
        result_schedules = []
        
        for schedule in all_schedules:
            subject = await self.subject_repository.get_by_id(schedule.subjectId)
            if subject and subject.groupId == group_id:
                result_schedules.append(schedule)
                
        return [ScheduleResponse.model_validate(schedule) for schedule in result_schedules]
    
    async def get_schedules_by_teacher_id(self, teacher_id: int) -> List[ScheduleResponse]:
        # Get all schedules where the subject's teacher is the specified teacher_id
        all_schedules = await self.schedule_repository.get_all()
        result_schedules = []
        
        for schedule in all_schedules:
            subject = await self.subject_repository.get_by_id(schedule.subjectId)
            if subject and subject.teacherId == teacher_id:
                result_schedules.append(schedule)
                
        return [ScheduleResponse.model_validate(schedule) for schedule in result_schedules]
        
    async def validate_subject_id(self, subject_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the subject_id exists.
        
        Args:
            subject_id: The subject ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if subject exists
        subject = await self.subject_repository.get_by_id(subject_id)
        if not subject:
            return False, f"Subject with ID {subject_id} does not exist"
        return True, None
    
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        teacher = await self.user_repository.get_by_id(teacher_id)
        if not teacher:
            return False, f"Teacher with ID {teacher_id} does not exist"
        if teacher.role != 'CD': 
            return False, f"User with ID {teacher_id} is not a teacher"
        return True, None
    
    async def validate_room_id(self, room_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the room_id exists.
        
        Args:
            room_id: The room ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if room exists        room = await self.room_repository.get_by_id(room_id)
        if not room:
            return False, f"Room with ID {room_id} does not exist"
        return True, None
        
    async def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the group_id exists.
        
        Args:
            group_id: The group ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if group exists
        if not await self.group_repository.exists_by_id(group_id):
            return False, f"Group with ID {group_id} does not exist"
        
        # All checks passed
        return True, None

    async def create_schedule(self, schedule_data: ScheduleCreate) -> ScheduleResponse:
        # Validate all foreign keys
        # Validate subject ID
        is_valid, error_message = await self.validate_subject_id(schedule_data.subjectId)
        if not is_valid:
            raise ValueError(error_message)
            

            
        # Validate room ID
        is_valid, error_message = await self.validate_room_id(schedule_data.roomId)
        if not is_valid:
            raise ValueError(error_message)
        
        # Create new schedule object
        schedule = Schedule(
            subjectId=schedule_data.subjectId,
            roomId=schedule_data.roomId,
            date=schedule_data.date,
            startTime=schedule_data.startTime,
            endTime=schedule_data.endTime,
            status=schedule_data.status
        )
        
        # Save to database
        created_schedule = await self.schedule_repository.create(schedule)
        return ScheduleResponse.model_validate(created_schedule)

    async def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[ScheduleResponse]:
        schedule = await self.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return None
            
        # Validate foreign keys if provided
        if schedule_data.subjectId is not None:
            is_valid, error_message = await self.validate_subject_id(schedule_data.subjectId)
            if not is_valid:
                raise ValueError(error_message)
                

                
        if schedule_data.roomId is not None:
            is_valid, error_message = await self.validate_room_id(schedule_data.roomId)
            if not is_valid:
                raise ValueError(error_message)
            
        # Update schedule fields if provided
        if schedule_data.subjectId is not None:
            schedule.subjectId = schedule_data.subjectId

        if schedule_data.roomId is not None:
            schedule.roomId = schedule_data.roomId
        if schedule_data.date is not None:
            schedule.date = schedule_data.date
        if schedule_data.startTime is not None:
            schedule.startTime = schedule_data.startTime
        if schedule_data.endTime is not None:
            schedule.endTime = schedule_data.endTime
        if schedule_data.status is not None:
            schedule.status = schedule_data.status
            
        # Save changes
        updated_schedule = await self.schedule_repository.update(schedule)
        return ScheduleResponse.model_validate(updated_schedule)

    async def delete_schedule(self, schedule_id: int) -> bool:
        return await self.schedule_repository.delete(schedule_id)
