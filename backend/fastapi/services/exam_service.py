from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from datetime import datetime, date, time

from models.DTOs.exam_dto import ExamResponse
from models.DTOs.schedule_dto import ScheduleResponse
from repositories.abstract.exam_repository_interface import IExamRepository
from services.abstract.email_service_interface import IEmailService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.user_service_interface import IUserService
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.schedule_service_interface import IScheduleService
from services.abstract.exam_service_interface import IExamService
from services.abstract.config_service_interface import IConfigService
from models.DTOs.notification_dto import NotificationCreate

logger = logging.getLogger(__name__)

class ExamService(IExamService):
    """Implementation of IExamService interface"""
    
    def __init__(
        self, 
        exam_repository: IExamRepository,
        schedule_service: IScheduleService,
        email_service: Optional[IEmailService] = None,
        notification_service: Optional[INotificationService] = None,
        user_service: Optional[IUserService] = None,
        subject_service: Optional[ISubjectService] = None,
        config_service: Optional[IConfigService] = None
    ):
        """Initialize with required repositories and services"""
        self.exam_repository = exam_repository
        self.schedule_service = schedule_service
        self.email_service = email_service
        self.notification_service = notification_service
        self.user_service = user_service
        self.subject_service = subject_service
        self.config_service = config_service
        
    # Helper method to preprocess exam data before validation
    def _preprocess_exam_data(self, exam_data: Dict) -> Dict:
        """Preprocess exam data to ensure proper format for validation"""
        processed_data = exam_data.copy()
        
        # Convert date objects to strings
        if 'date' in processed_data and processed_data['date'] is not None:
            if isinstance(processed_data['date'], date):
                processed_data['date'] = processed_data['date'].isoformat()
        
        return processed_data
        
    async def _get_subject_ids_for_group(self, group_id: int) -> List[int]:
        """Get all subject IDs associated with a specific group
        
        Args:
            group_id (int): The group ID to find subjects for
            
        Returns:
            List[int]: List of subject IDs for the group
        """
        # We'll use the subject service if available, otherwise fall back to repository
        if self.subject_service:
            # This uses the proper layered approach going through the subject service
            subjects = await self.subject_service.get_subjects_by_group_id(group_id)
            return [subject.id for subject in subjects]
        else:
            # Fallback to repository call if service not available
            # Note: In production, you should ensure subject_service is always provided
            logger.warning(f"[DEBUG] ExamService - Subject service not available, using repository fallback for group {group_id}")
            return await self.exam_repository.get_subject_ids_by_group_id(group_id)
    
    async def _enrich_schedule_with_metadata(self, schedule: ScheduleResponse, subject_id: int, group_id: int) -> Dict[str, Any]:
        """Enrich a schedule with additional metadata to create an exam response
        
        Args:
            schedule: The schedule response from schedule service
            subject_id: The subject ID for additional details
            group_id: The group ID for additional details
            
        Returns:
            Dict: Enriched exam data with all required fields
        """
        # Start with schedule data
        # Handle date conversion explicitly
        date_value = schedule.date
        if isinstance(date_value, date):
            date_value = date_value.isoformat()
            
        exam_data = {
            "id": schedule.id,
            "date": date_value,
            "startTime": schedule.startTime,
            "endTime": schedule.endTime,
            "roomId": schedule.roomId,
            "status": schedule.status,
            "message": schedule.message
        }
        
        # Get subject details
        if self.subject_service:
            subject = await self.subject_service.get_subject_by_id(subject_id)
            if subject:
                exam_data["subjectId"] = subject.id
                exam_data["subjectName"] = subject.name
                exam_data["subjectShortName"] = subject.shortName
                
                # Get teacher details from subject
                if self.user_service and subject.teacherId:
                    teacher = await self.user_service.get_user_by_id(subject.teacherId)
                    if teacher:
                        exam_data["teacherId"] = teacher.id
                        exam_data["teacherName"] = f"{teacher.lastName} {teacher.firstName}"
                        exam_data["teacherEmail"] = teacher.email
                        exam_data["teacherPhone"] = teacher.phone
        
        # Get group details
        if group_id:
            # Use group repository or group service
            group = None
            if hasattr(self, 'group_service') and self.group_service:
                group = await self.group_service.get_group_by_id(group_id)
            
            if group:
                exam_data["groupId"] = group.id
                exam_data["groupName"] = group.name
                exam_data["specializationShortName"] = group.specializationShortName
                exam_data["studyYear"] = group.studyYear
            else:
                # Fallback values if group details can't be retrieved
                exam_data["groupId"] = group_id
                exam_data["groupName"] = "Unknown Group"
                exam_data["specializationShortName"] = "Unknown"
                exam_data["studyYear"] = 0
        
        # Calculate duration if both startTime and endTime exist
        if schedule.startTime and schedule.endTime:
            hours_diff = schedule.endTime.hour - schedule.startTime.hour
            if schedule.endTime.minute < schedule.startTime.minute:
                hours_diff -= 1
            exam_data["duration"] = max(1, hours_diff)  # Ensure at least 1 hour
        else:
            exam_data["duration"] = None
            
        return exam_data
    
    async def get_all_exams(self) -> List[ExamResponse]:
        """Get all exams with associated information
        
        Returns:
            List[ExamResponse]: List of exams with subject, teacher and group details
        """
        logger.info("[DEBUG] ExamService - get_all_exams: Starting execution")
        
        try:
            # Get exams with details from repository
            exam_data = await self.exam_repository.get_all_exams_with_details()
            
            # Convert to DTO response models with proper error handling
            exams = []
            for exam in exam_data:
                try:
                    # If we encounter validation errors, we can try to sanitize the data
                    exams.append(ExamResponse.model_validate(exam))
                except Exception as validation_error:
                    logger.warning(f"[DEBUG] ExamService - Validation error for exam ID {exam.get('id')}: {str(validation_error)}")
                    # Try sanitizing the problematic fields
                    sanitized_exam = exam.copy()
                    # If date field is causing issues, convert explicitly to None
                    if 'date' in sanitized_exam and sanitized_exam['date'] is not None:
                        # Log the original date for debugging
                        logger.info(f"[DEBUG] ExamService - Converting date from {sanitized_exam['date']} to None for exam ID {exam.get('id')}")
                        sanitized_exam['date'] = None
                    # Try validation again with sanitized data
                    try:
                        exams.append(ExamResponse.model_validate(sanitized_exam))
                    except Exception as second_error:
                        logger.error(f"[DEBUG] ExamService - Failed validation after sanitizing for exam ID {exam.get('id')}: {str(second_error)}")
                        # Skip this exam rather than failing the entire request
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams after validation")
            return exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in get_all_exams: {str(e)}")
            raise
    
    async def get_exams_by_study_program(self, program_code: str) -> List[ExamResponse]:
        """Get exams filtered by study program
        
        Args:
            program_code (str): Short name of the study program
            
        Returns:
            List[ExamResponse]: Filtered list of exams
        """
        logger.info(f"[DEBUG] ExamService - get_exams_by_study_program: {program_code}")
        
        try:
            # Get filtered exams from repository
            exam_data = await self.exam_repository.get_exams_by_study_program(program_code)
            
            # Convert to DTO response models with proper error handling
            exams = []
            for exam in exam_data:
                try:
                    # If we encounter validation errors, we can try to sanitize the data
                    exams.append(ExamResponse.model_validate(exam))
                except Exception as validation_error:
                    logger.warning(f"[DEBUG] ExamService - Validation error for exam ID {exam.get('id')}: {str(validation_error)}")
                    # Try sanitizing the problematic fields
                    sanitized_exam = exam.copy()
                    # If date field is causing issues, convert explicitly to None
                    if 'date' in sanitized_exam and sanitized_exam['date'] is not None:
                        # Log the original date for debugging
                        logger.info(f"[DEBUG] ExamService - Converting date from {sanitized_exam['date']} to None for exam ID {exam.get('id')}")
                        sanitized_exam['date'] = None
                    # Try validation again with sanitized data
                    try:
                        exams.append(ExamResponse.model_validate(sanitized_exam))
                    except Exception as second_error:
                        logger.error(f"[DEBUG] ExamService - Failed validation after sanitizing for exam ID {exam.get('id')}: {str(second_error)}")
                        # Skip this exam rather than failing the entire request
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for program {program_code} after validation")
            return exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in get_exams_by_study_program: {str(e)}")
            raise
        
    async def get_exams_by_teacher_id(self, teacher_id: int) -> List[ExamResponse]:
        """Get exams assigned to a specific teacher
        
        Args:
            teacher_id (int): ID of the teacher
            
        Returns:
            List[ExamResponse]: List of exams for the teacher
        """
        logger.info(f"[DEBUG] ExamService - get_exams_by_teacher_id: {teacher_id}")
        
        try:
            # Get filtered exams from repository
            exam_data = await self.exam_repository.get_exams_by_teacher_id(teacher_id)
            
            # Convert to DTO response models with proper error handling
            exams = []
            for exam in exam_data:
                try:
                    # If we encounter validation errors, we can try to sanitize the data
                    exams.append(ExamResponse.model_validate(exam))
                except Exception as validation_error:
                    logger.warning(f"[DEBUG] ExamService - Validation error for exam ID {exam.get('id')}: {str(validation_error)}")
                    # Try sanitizing the problematic fields
                    sanitized_exam = exam.copy()
                    # If date field is causing issues, convert explicitly to None
                    if 'date' in sanitized_exam and sanitized_exam['date'] is not None:
                        # Log the original date for debugging
                        logger.info(f"[DEBUG] ExamService - Converting date from {sanitized_exam['date']} to None for exam ID {exam.get('id')}")
                        sanitized_exam['date'] = None
                    # Try validation again with sanitized data
                    try:
                        exams.append(ExamResponse.model_validate(sanitized_exam))
                    except Exception as second_error:
                        logger.error(f"[DEBUG] ExamService - Failed validation after sanitizing for exam ID {exam.get('id')}: {str(second_error)}")
                        # Skip this exam rather than failing the entire request
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for teacher {teacher_id} after validation")
            return exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in get_exams_by_teacher_id: {str(e)}")
            raise
    
    async def get_exams_by_group_id(self, group_id: int) -> List[ExamResponse]:
        """Get exams for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            List[ExamResponse]: List of exams for the group
        """
        logger.info(f"[DEBUG] ExamService - get_exams_by_group_id: {group_id}")
        
        try:
            # First, get subject IDs for this group to identify relevant schedules
            subject_ids = await self._get_subject_ids_for_group(group_id)
            logger.info(f"[DEBUG] ExamService - Found {len(subject_ids)} subjects for group {group_id}")
            
            # Get exam data by mapping through schedules from the schedule service
            exams = []
            for subject_id in subject_ids:
                # Get schedules from the schedule service rather than directly from repository
                schedules = await self.schedule_service.get_schedules_by_subject_id(subject_id)
                
                # Map each schedule to an exam response with additional metadata
                for schedule in schedules:
                    try:
                        # Get required related data (subject, teacher, group info)
                        exam_data = await self._enrich_schedule_with_metadata(schedule, subject_id, group_id)
                        
                        # Process data before validation
                        processed_exam = self._preprocess_exam_data(exam_data)
                        
                        # Create ExamResponse
                        exams.append(ExamResponse.model_validate(processed_exam))
                    except Exception as e:
                        logger.error(f"[DEBUG] ExamService - Error processing schedule for subject {subject_id}: {str(e)}")
                        # Skip this schedule rather than failing the entire request
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for group {group_id} after processing")
            return exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in get_exams_by_group_id: {str(e)}")
            raise
    
    async def update_exam(self, exam_id: int, exam_data: Dict[str, Any]) -> ExamResponse:
        """Update an exam with new information
        
        Args:
            exam_id (int): ID of the exam to update
            exam_data (Dict[str, Any]): Updated exam data including date, location, professor, etc.
            
        Returns:
            ExamResponse: Updated exam data response
        """
        logger.info(f"[DEBUG] ExamService - update_exam: {exam_id}")
        
        try:
            # Update exam in repository
            updated_exam_data = await self.exam_repository.update_exam(exam_id, exam_data)
            
            # Convert to DTO response model with sanitization if needed
            try:
                exam_response = ExamResponse.model_validate(updated_exam_data)
            except Exception as validation_error:
                logger.warning(f"[DEBUG] ExamService - Validation error for updated exam {exam_id}: {str(validation_error)}")
                # Try sanitizing the problematic fields
                sanitized_exam = updated_exam_data.copy()
                # If date field is causing issues, convert explicitly to None
                if 'date' in sanitized_exam and sanitized_exam['date'] is not None:
                    logger.info(f"[DEBUG] ExamService - Converting date from {sanitized_exam['date']} to None for exam ID {exam_id}")
                    sanitized_exam['date'] = None
                # Try validation again with sanitized data
                exam_response = ExamResponse.model_validate(sanitized_exam)
                
            logger.info(f"[DEBUG] ExamService - Successfully updated exam {exam_id}")
            return exam_response
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in update_exam: {str(e)}")
            raise
            
    async def create_exam_proposal(self, proposal_data: Dict[str, Any]) -> ExamResponse:
        """Create a new exam proposal from a student group.
        
        Args:
            proposal_data: The exam proposal data including subject ID, date, time, etc.
            
        Returns:
            ExamResponse: The created exam response with all details
        """
        logger.info(f"[DEBUG] ExamService - Creating exam proposal with data: {proposal_data}")  
        
        try:
            # Validate the only required field is present
            if 'subjectId' not in proposal_data:
                raise ValueError("Subject ID is required for exam proposals")
                
            # Validate date is within the exam period, but only if date is provided
            if 'date' in proposal_data and proposal_data['date'] is not None:
                date_valid = await self._validate_date_in_exam_period(proposal_data['date'])
                if not date_valid:
                    raise ValueError("Proposed date is not within the configured exam period")
            
            # Handle optional status field - either from input or use specific value based on role logic
            # Status can now be null, but if provided we'll use it
            if 'status' in proposal_data and proposal_data['status']:
                logger.info(f"[DEBUG] ExamService - Using provided status: '{proposal_data['status']}'")
            else:
                # If no status is provided, we can either leave it as None or set a default
                # Here we'll still set a default for backward compatibility
                proposal_data['status'] = 'pending'  
                logger.info(f"[DEBUG] ExamService - Setting default status for proposal: 'pending'")
                
            # Handle message field if provided
            if 'message' in proposal_data and proposal_data['message']:
                # Safely truncate long messages in logs
                message_preview = proposal_data['message'][:50] + '...' if len(proposal_data['message']) > 50 else proposal_data['message']
                logger.info(f"[DEBUG] ExamService - Proposal includes message: '{message_preview}'")
            else:
                # Add empty message field if not provided
                proposal_data['message'] = None
                
            # Ensure we don't set default times if not provided
            # This ensures that when SG users only set a date, no times will be added
            if 'startTime' not in proposal_data or proposal_data['startTime'] is None:
                proposal_data['startTime'] = None
            if 'endTime' not in proposal_data or proposal_data['endTime'] is None:
                proposal_data['endTime'] = None
                
            # Create the exam proposal
            exam_data = await self.exam_repository.create_exam(proposal_data)
            
            # Preprocess data before validation to handle date objects
            processed_exam_data = self._preprocess_exam_data(exam_data)
            
            # Convert dictionary to ExamResponse if needed with sanitization handling
            if isinstance(processed_exam_data, dict):
                try:
                    exam_response = ExamResponse.model_validate(processed_exam_data)
                except Exception as validation_error:
                    logger.warning(f"[DEBUG] ExamService - Validation error for created exam: {str(validation_error)}")
                    # Try sanitizing the problematic fields if preprocessing wasn't enough
                    sanitized_exam = processed_exam_data.copy()
                    # If date field is still causing issues, try to handle it differently
                    if 'date' in sanitized_exam and sanitized_exam['date'] is not None:
                        logger.info(f"[DEBUG] ExamService - Converting problematic date from {sanitized_exam['date']} to None as validation failed")
                        sanitized_exam['date'] = None
                    # Try validation again with sanitized data
                    exam_response = ExamResponse.model_validate(sanitized_exam)
            else:
                exam_response = processed_exam_data
            
            # Send notification to course director if all services are available
            if self.email_service and self.notification_service and self.user_service and self.subject_service:
                await self._send_proposal_notification(proposal_data, exam_response)
            
            # Log success with safe access to status using the 'status' field (aligning with our standardized English statuses)
            status = getattr(exam_response, 'status', proposal_data.get('status', 'unknown'))
            logger.info(f"[DEBUG] ExamService - Successfully created exam proposal for subject {proposal_data.get('subjectId')} with status '{status}'")
            return exam_response
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamService - Error in create_exam_proposal: {str(e)}")
            raise
            
    async def _send_proposal_notification(self, proposal_data: Dict[str, Any], exam_response: ExamResponse) -> None:
        """Send email notification to course director about new exam proposal and log it
        
        Args:
            proposal_data: The original proposal data
            exam_response: The created exam response object
        """
        try:
            # Get the subject details to find the teacher (course director)
            subject_id = proposal_data.get('subjectId')
            group_id = proposal_data.get('groupId')
            date = proposal_data.get('date')
            
            logger.info(f"[DEBUG] ExamService - Sending notification for proposal - Subject ID: {subject_id}, Group ID: {group_id}, Date: {date}")
            
            # Get subject information to find the course director
            subject_details = await self.subject_service.get_subject_by_id(subject_id)
            if not subject_details:
                logger.warning(f"Cannot send notification: Subject {subject_id} not found")
                return
                
            # Get course director details
            teacher_id = subject_details.teacherId
            logger.info(f"[DEBUG] ExamService - Found subject with teacher ID: {teacher_id}")
            
            teacher = await self.user_service.get_user_by_id(teacher_id)
            if not teacher:
                logger.warning(f"Cannot send notification: Teacher {teacher_id} not found")
                return
                
            teacher_email = teacher.email
            logger.info(f"[DEBUG] ExamService - Found teacher with email: {teacher_email}")
            
            # Get group details for the notification message
            group = None
            try:
                # This is required - we need the group name for the notification
                group = await self.subject_service.get_group_by_id(group_id)
                if not group:
                    logger.warning(f"Group with ID {group_id} not found in database")
                    # Still continue with ID as fallback
            except Exception as e:
                logger.warning(f"Could not get group details: {str(e)}")
                
            # Use either group name or a more user-friendly fallback than just ID
            if group and hasattr(group, 'name') and group.name:
                group_name = group.name
            else:
                # More friendly fallback than just showing the ID
                group_name = f"Grupa cu ID: {group_id} (nume indisponibil)"
            subject_name = subject_details.name
            
            # Send email to course director using the dedicated method
            logger.info(f"[DEBUG] ExamService - Attempting to send email notification to {teacher_email} for subject '{subject_name}', group '{group_name}', date '{date}'")
            
            # Check if email service is initialized
            if not self.email_service:
                logger.error("[DEBUG] ExamService - Email service is not initialized")
                return
                
            email_sent = await self.email_service.send_exam_proposal_notification(
                teacher_email=teacher_email,
                subject_name=subject_name,
                group_name=group_name,
                date=date
            )
            
            # Log notification in database
            if email_sent:
                # Create notification for the course director
                notification_data = NotificationCreate(
                    userId=teacher_id,
                    message=f"Propunere nouă de examen pentru {subject_name} de la {group_name}, data: {date}",
                    status="trimis"
                )
                
                await self.notification_service.create_notification(notification_data)
                logger.info(f"Email notification sent to course director (ID: {teacher_id}) for exam proposal")
            else:
                logger.warning(f"Failed to send email notification to course director (ID: {teacher_id})")
                
        except Exception as e:
            logger.error(f"Error sending proposal notification: {str(e)}")
            # We don't re-raise the exception to avoid disrupting the main workflow
            # The proposal is still created even if notification fails
            
    async def _validate_date_in_exam_period(self, date) -> bool:
        """
        Validate that a proposed exam date is within the configured exam period.
        
        For now, this is a placeholder implementation that always returns True.
        In a future update, this should check against a configured exam period.
        
        Args:
            date: The date to validate
            
        Returns:
            bool: True if date is valid, False otherwise
        """
        logger.info(f"[DEBUG] ExamService - Validating exam date: {date}")
        
        # For now, we'll accept any date (placeholder implementation)
        # TODO: In the future, implement actual date range validation
        return True
