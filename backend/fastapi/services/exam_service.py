from typing import List, Dict, Any, Optional, Tuple
import logging

from models.DTOs.exam_dto import ExamResponse
from repositories.abstract.exam_repository_interface import IExamRepository
from services.abstract.email_service_interface import IEmailService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.user_service_interface import IUserService
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.exam_service_interface import IExamService
from models.DTOs.notification_dto import NotificationCreate

logger = logging.getLogger(__name__)

class ExamService(IExamService):
    """Service implementation for exam-related operations"""
    
    def __init__(self, 
                 exam_repository: IExamRepository,
                 email_service: Optional[IEmailService] = None,
                 notification_service: Optional[INotificationService] = None,
                 user_service: Optional[IUserService] = None,
                 subject_service: Optional[ISubjectService] = None):
        self.exam_repository = exam_repository
        self.email_service = email_service
        self.notification_service = notification_service
        self.user_service = user_service
        self.subject_service = subject_service
        
    async def get_all_exams(self) -> List[ExamResponse]:
        """Get all exams with associated information
        
        Returns:
            List[ExamResponse]: List of exams with subject, teacher and group details
        """
        logger.info("[DEBUG] ExamService - get_all_exams: Starting execution")
        
        try:
            # Get exams with details from repository
            exam_data = await self.exam_repository.get_all_exams_with_details()
            
            # Convert to DTO response models
            exams = [ExamResponse.model_validate(exam) for exam in exam_data]
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams")
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
            
            # Convert to DTO response models
            exams = [ExamResponse.model_validate(exam) for exam in exam_data]
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for program {program_code}")
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
            
            # Convert to DTO response models
            exams = [ExamResponse.model_validate(exam) for exam in exam_data]
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for teacher {teacher_id}")
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
            # Get filtered exams from repository
            exam_data = await self.exam_repository.get_exams_by_group_id(group_id)
            
            # Convert to DTO response models
            exams = [ExamResponse.model_validate(exam) for exam in exam_data]
            
            logger.info(f"[DEBUG] ExamService - Returning {len(exams)} exams for group {group_id}")
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
            
            # Convert to DTO response model
            exam_response = ExamResponse.model_validate(updated_exam_data)
            
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
            # Validate date is within the exam period
            if 'date' in proposal_data:
                date_valid = await self._validate_date_in_exam_period(proposal_data['date'])
                if not date_valid:
                    raise ValueError("Proposed date is not within the configured exam period")
            
            # Ensure status is set properly - either from input or default to 'proposed' for SG proposals
            if 'status' not in proposal_data or not proposal_data['status']:
                proposal_data['status'] = 'proposed'
                logger.info(f"[DEBUG] ExamService - Setting default status for proposal: 'proposed'")
            else:
                logger.info(f"[DEBUG] ExamService - Using provided status: '{proposal_data['status']}'")
                
            # Create the exam proposal
            exam_data = await self.exam_repository.create_exam(proposal_data)
            
            # Convert dictionary to ExamResponse if needed
            if isinstance(exam_data, dict):
                exam_response = ExamResponse.model_validate(exam_data)
            else:
                exam_response = exam_data
            
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
