from typing import List, Optional, Tuple, Dict, Any, Set
from datetime import date, time
import logging

from models.schedule import Schedule
from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from models.DTOs.user_dto import UserResponse

logger = logging.getLogger(__name__)
from repositories.abstract.schedule_repository_interface import IScheduleRepository
from repositories.abstract.subject_repository_interface import ISubjectRepository
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.room_repository_interface import IRoomRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from services.abstract.schedule_service_interface import IScheduleService

class ScheduleService(IScheduleService):
    # Define the permitted status values for exams - English only
    VALID_STATUSES: Set[str] = {
        'pending',       # Waiting for approval
        'proposed',      # Proposed by student group
        'approved',      # Approved by course director
        'rejected'       # Rejected by course director
    }
    
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
        
        logger.info(f"Processing schedules for teacher_id={teacher_id}, found {len(all_schedules)} total schedules")
        
        for schedule in all_schedules:
            subject = await self.subject_repository.get_by_id(schedule.subjectId)
            if subject and subject.teacherId == teacher_id:
                # Get the group information for this subject
                group = await self.group_repository.get_by_id(subject.groupId) if subject.groupId else None
                
                # Create a dict from the schedule to be able to add additional fields
                schedule_dict = {**schedule.__dict__}
                if group:
                    logger.info(f"Adding group data to schedule {schedule.id}: groupId={group.id}, groupName={group.name}")
                    schedule_dict['groupId'] = group.id
                    schedule_dict['groupName'] = group.name
                else:
                    logger.warning(f"No group found for schedule {schedule.id}, subject {schedule.subjectId} with groupId {subject.groupId if subject else None}")
                
                result_schedules.append(schedule_dict)
                
        # Convert the enhanced dictionaries to ScheduleResponse objects
        return [ScheduleResponse.model_validate(schedule_data) for schedule_data in result_schedules]
        
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
        
    async def get_subject_assistants(self, subject_id: int) -> List[UserResponse]:
        """Get assistants (CD users) associated with a specific subject
        
        Args:
            subject_id (int): The ID of the subject
            
        Returns:
            List[UserResponse]: List of users who are assistants for this subject
        """
        # Get the subject to access its assistantIds
        subject = await self.subject_repository.get_by_id(subject_id)
        if not subject or not subject.assistantIds:
            return []
        
        # Get user details for all assistant IDs in a single operation
        assistants = []
        for assistant_id in subject.assistantIds:
            user = await self.user_repository.get_by_id(assistant_id)
            if user and user.role == "CD":  # Verify the user exists and has CD role
                assistants.append(UserResponse.model_validate(user))
        
        return assistants
    
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        teacher = await self.user_repository.get_by_id(teacher_id)
        if not teacher:
            return False, f"Teacher with ID {teacher_id} does not exist"
        if teacher.role != 'CD': 
            return False, f"User with ID {teacher_id} is not a teacher"
        return True, None
    
    async def validate_assistant_id(self, assistant_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the assistant_id exists and is a valid teacher/assistant.
        
        Args:
            assistant_id: The user ID to validate as an assistant
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        assistant = await self.user_repository.get_by_id(assistant_id)
        if not assistant:
            return False, f"Assistant with ID {assistant_id} does not exist"
        # Assistants can be CD or other roles that can assist in exams
        if assistant.role not in ['CD', 'SEC']:  # Adjust roles as needed
            return False, f"User with ID {assistant_id} cannot be assigned as an assistant"
        return True, None
        
    async def validate_assistant_ids(self, assistant_ids: List[int]) -> Tuple[bool, Optional[str]]:
        """Validates a list of assistant IDs.
        
        Args:
            assistant_ids: List of assistant IDs to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        if not assistant_ids:
            return True, None
            
        for assistant_id in assistant_ids:
            is_valid, error_message = await self.validate_assistant_id(assistant_id)
            if not is_valid:
                return False, error_message
                
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
        # Check if room exists
        room = await self.room_repository.get_by_id(room_id)
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
        
    async def validate_status(self, status: str) -> Tuple[bool, Optional[str]]:
        """Validates if the status value is permitted.
        
        Args:
            status: The status value to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        if not status:
            return False, "Status cannot be empty"
            
        if status.lower() not in {s.lower() for s in self.VALID_STATUSES}:
            valid_statuses = "', '".join(sorted(self.VALID_STATUSES))
            return False, f"Invalid status '{status}'. Valid status values are: '{valid_statuses}'"
            
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
            
        # Validate status
        is_valid, error_message = await self.validate_status(schedule_data.status)
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

    async def check_for_room_conflicts(self, schedule_id: int, room_ids: List[int], date: date, start_time: time, end_time: time) -> Tuple[bool, List[str]]:
        """Check for conflicts with other scheduled exams in the same rooms.
        
        Args:
            schedule_id: The ID of the current schedule (to exclude from conflict check)
            room_ids: List of room IDs to check for conflicts
            date: The date of the exam
            start_time: Start time of the exam
            end_time: End time of the exam
            
        Returns:
            Tuple of (has_conflicts, conflict_messages)
        """
        conflicts = []
        
        # Get all schedules for the same date that are approved
        all_schedules = await self.schedule_repository.get_all()
        same_day_schedules = [
            s for s in all_schedules 
            if s.date == date and s.status == 'approved' and s.id != schedule_id
        ]
        
        for schedule in same_day_schedules:
            # Check for time overlap
            if (start_time < schedule.endTime and end_time > schedule.startTime):
                # Check if any of the rooms conflict
                if schedule.roomId in room_ids:
                    room = await self.room_repository.get_by_id(schedule.roomId)
                    if room:
                        conflicts.append(f"Room {room.name} is already booked between {schedule.startTime} - {schedule.endTime}")
                
                # We would also check additional room relationships here if we had them in the database
                # This would require a related table for additional rooms
        
        return len(conflicts) > 0, conflicts
        
    async def check_for_assistant_conflicts(self, schedule_id: int, assistant_ids: List[int], date: date, start_time: time, end_time: time) -> Tuple[bool, List[str]]:
        """Check for conflicts with assistants already assigned to other exams at the same time.
        
        Args:
            schedule_id: The ID of the current schedule (to exclude from conflict check)
            assistant_ids: List of assistant user IDs to check for conflicts
            date: The date of the exam
            start_time: Start time of the exam
            end_time: End time of the exam
            
        Returns:
            Tuple of (has_conflicts, conflict_messages)
        """
        # In a complete implementation, we would query a related table that links
        # assistants to schedules. Since that's likely not implemented yet, this
        # is a placeholder for the conflict detection logic.
        
        # For the current implementation, we'll assume no conflicts
        return False, []
        
    async def check_conflicts(self, schedule_id: int, date: date, start_time: str, end_time: str, room_ids: List[int], assistant_ids: List[int]) -> Dict[str, Any]:
        """Check for conflicts with existing schedules for rooms, assistants, and teacher
        
        Args:
            schedule_id: ID of the schedule to exclude from conflict check
            date: Date for the proposed schedule
            start_time: Start time of proposed schedule in format HH:MM
            end_time: End time of proposed schedule in format HH:MM
            room_ids: List of room IDs to check for conflicts
            assistant_ids: List of assistant IDs to check for conflicts
            
        Returns:
            Dict[str, Any]: Dictionary with conflict information
        """
        # Convert string times to time objects
        try:
            start_time_obj = time.fromisoformat(start_time)
            end_time_obj = time.fromisoformat(end_time)
        except ValueError:
            # If the time format is not ISO (HH:MM), try parsing it
            try:
                hour_start, minute_start = map(int, start_time.split(':'))
                hour_end, minute_end = map(int, end_time.split(':'))
                start_time_obj = time(hour=hour_start, minute=minute_start)
                end_time_obj = time(hour=hour_end, minute=minute_end)
            except Exception as e:
                logger.error(f"Error parsing time values: {e}")
                raise ValueError(f"Invalid time format. Expected HH:MM, got {start_time} and {end_time}")
        
        # Check for room conflicts
        has_room_conflicts, room_conflict_msgs = await self.check_for_room_conflicts(
            schedule_id, room_ids, date, start_time_obj, end_time_obj
        )
        
        # Check for assistant conflicts
        has_assistant_conflicts, assistant_conflict_msgs = await self.check_for_assistant_conflicts(
            schedule_id, assistant_ids, date, start_time_obj, end_time_obj
        )
        
        # Prepare detailed conflict information for frontend
        room_conflicts = []
        if has_room_conflicts:
            # Get all schedules for the same date that are approved
            all_schedules = await self.schedule_repository.get_all()
            same_day_schedules = [
                s for s in all_schedules 
                if s.date == date and s.status == 'approved' and s.id != schedule_id
            ]
            
            for schedule in same_day_schedules:
                # Check for time overlap
                if (start_time_obj < schedule.endTime and end_time_obj > schedule.startTime):
                    # Check if any of the rooms conflict
                    if schedule.roomId in room_ids:
                        room = await self.room_repository.get_by_id(schedule.roomId)
                        subject = None
                        try:
                            subject = await self.subject_repository.get_by_id(schedule.subjectId)
                        except Exception:
                            pass
                        
                        room_conflicts.append({
                            "roomId": room.id,
                            "roomName": room.name,
                            "subjectId": schedule.subjectId,
                            "subjectName": subject.name if subject else f"Subject {schedule.subjectId}",
                            "startTime": schedule.startTime.isoformat(),
                            "endTime": schedule.endTime.isoformat()
                        })
        
        # For now, we'll return empty arrays for assistant and teacher conflicts
        # but with the proper structure for the frontend to handle
        assistant_conflicts = []
        teacher_conflicts = []
        
        return {
            "roomConflicts": room_conflicts,
            "assistantConflicts": assistant_conflicts,
            "teacherConflicts": teacher_conflicts
        }
    
    async def send_notification_email(self, schedule_id: int, recipient_email: str, subject: str, message: str) -> bool:
        """Send notification email for schedule changes.
        
        Args:
            schedule_id: The ID of the schedule
            recipient_email: Email address of the recipient
            subject: Email subject
            message: Email message content
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        # In a real implementation, this would use an email service/client
        # For now, we'll just log the email that would be sent
        logger.info(f"[EMAIL] Would send email for schedule {schedule_id} to {recipient_email}:")
        logger.info(f"[EMAIL] Subject: {subject}")
        logger.info(f"[EMAIL] Message: {message}")
        
        # Here you would implement actual email sending logic
        # For example:
        # from services.email_service import send_email
        # return await send_email(recipient_email, subject, message)
        
        return True
    
    async def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[ScheduleResponse]:
        schedule = await self.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            return None
        
        logger.info(f"[DEBUG] Updating schedule {schedule_id} with data: {schedule_data}")
            
        # Validate foreign keys if provided
        if schedule_data.subjectId is not None:
            is_valid, error_message = await self.validate_subject_id(schedule_data.subjectId)
            if not is_valid:
                raise ValueError(error_message)
                
        if schedule_data.roomId is not None:
            is_valid, error_message = await self.validate_room_id(schedule_data.roomId)
            if not is_valid:
                raise ValueError(error_message)
        
        # Validate additional rooms if provided
        if schedule_data.additionalRoomIds is not None:
            for room_id in schedule_data.additionalRoomIds:
                is_valid, error_message = await self.validate_room_id(room_id)
                if not is_valid:
                    raise ValueError(error_message)
        
        # Validate assistants if provided
        if schedule_data.assistantIds is not None:
            is_valid, error_message = await self.validate_assistant_ids(schedule_data.assistantIds)
            if not is_valid:
                raise ValueError(error_message)
                
        # Validate status if provided
        if schedule_data.status is not None:
            is_valid, error_message = await self.validate_status(schedule_data.status)
            if not is_valid:
                raise ValueError(error_message)
        
        # Check for conflicts if approving a schedule
        if schedule_data.status == 'approved':
            date_to_check = schedule_data.date or schedule.date
            start_time_to_check = schedule_data.startTime or schedule.startTime
            end_time_to_check = schedule_data.endTime or schedule.endTime
            
            # Get all rooms (primary + additional)
            all_room_ids = []
            if schedule_data.roomId is not None:
                all_room_ids.append(schedule_data.roomId)
            if schedule_data.additionalRoomIds:
                all_room_ids.extend(schedule_data.additionalRoomIds)
                
            # If no rooms specified in update, use the existing room
            if not all_room_ids and schedule.roomId:
                all_room_ids.append(schedule.roomId)
            
            # Check room conflicts
            has_room_conflicts, room_conflict_msgs = await self.check_for_room_conflicts(
                schedule_id, all_room_ids, date_to_check, start_time_to_check, end_time_to_check)
            
            # Check assistant conflicts if assistants are being assigned
            assistant_ids = schedule_data.assistantIds or []
            if assistant_ids:
                has_assistant_conflicts, assistant_conflict_msgs = await self.check_for_assistant_conflicts(
                    schedule_id, assistant_ids, date_to_check, start_time_to_check, end_time_to_check)
                
                # Combine conflict messages
                if has_assistant_conflicts:
                    has_room_conflicts = True  # Set overall conflict flag
                    room_conflict_msgs.extend(assistant_conflict_msgs)
            
            # If conflicts detected, you might want to raise an error or just log warnings
            if has_room_conflicts:
                logger.warning(f"[CONFLICTS] Detected conflicts for schedule {schedule_id}: {room_conflict_msgs}")
                # Uncommenting the line below would prevent approving if conflicts exist
                # raise ValueError(f"Cannot approve due to conflicts: {', '.join(room_conflict_msgs)}")
        
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
            logger.info(f"[DEBUG] Updating schedule {schedule_id} status to: {schedule_data.status}")
            old_status = schedule.status
            schedule.status = schedule_data.status
            
            # Handle special actions based on status changes
            if schedule_data.status == 'rejected' and schedule_data.sendEmail:
                # Send rejection notification to SG
                subject = await self.subject_repository.get_by_id(schedule.subjectId)
                if subject:
                    group = await self.group_repository.get_by_id(subject.groupId)
                    if group:
                        # Find SG user for this group
                        sg_users = await self.user_repository.get_by_role_and_group('SG', group.id)
                        for sg_user in sg_users:
                            if sg_user.email:
                                # Send notification email
                                subject_line = f"Proposed exam date rejected: {subject.name}"
                                message = f"Dear {sg_user.name},\n\nYour proposed exam date for {subject.name} has been rejected."
                                
                                if schedule_data.reason:
                                    message += f"\n\nReason: {schedule_data.reason}"
                                    
                                message += "\n\nPlease propose a new date.\n\nRegards,\nExam Management System"
                                
                                await self.send_notification_email(
                                    schedule_id, 
                                    sg_user.email, 
                                    subject_line, 
                                    message
                                )
        
        # Handle additional rooms and assistants
        # Since the Schedule model only supports one room directly, we'll store the primary room
        # in the Schedule and handle additional data differently
        
        # For rooms - we use the primary roomId in the Schedule table and update any related records
        # for additional rooms (in a production system, this would be in a relationship table)
        if schedule_data.additionalRoomIds:
            logger.info(f"[DEBUG] Additional rooms for schedule {schedule_id}: {schedule_data.additionalRoomIds}")
            # In this implementation, we're limited by the database schema
            # For a complete solution, we would need to create a schedule_rooms relationship table
            # For now, just use the first additional room as the primary if no primary is specified
            if schedule_data.roomId is None and schedule_data.additionalRoomIds:
                schedule.roomId = schedule_data.additionalRoomIds[0]
        
        # For assistants - update the assistantIds in the Subject if needed
        if schedule_data.assistantIds:
            logger.info(f"[DEBUG] Assistants for schedule {schedule_id}: {schedule_data.assistantIds}")
            # Get the associated subject and update its assistantIds
            subject = await self.subject_repository.get_by_id(schedule.subjectId)
            if subject:
                # In real implementation, we'd need to be careful not to overwrite existing assistants
                # that might be assigned to this subject for other schedules
                subject.assistantIds = schedule_data.assistantIds
                await self.subject_repository.update(subject)
            
        # Save changes to the main schedule record
        updated_schedule = await self.schedule_repository.update(schedule)
        return ScheduleResponse.model_validate(updated_schedule)

    async def delete_schedule(self, schedule_id: int) -> bool:
        return await self.schedule_repository.delete(schedule_id)
