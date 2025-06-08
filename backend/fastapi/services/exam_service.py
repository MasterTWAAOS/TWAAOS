from typing import List, Dict, Any, Optional
import logging

from models.DTOs.exam_dto import ExamResponse
from repositories.abstract.exam_repository_interface import IExamRepository
from services.abstract.exam_service_interface import IExamService

logger = logging.getLogger(__name__)

class ExamService(IExamService):
    """Service implementation for exam-related operations"""
    
    def __init__(self, exam_repository: IExamRepository):
        self.exam_repository = exam_repository
        
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
