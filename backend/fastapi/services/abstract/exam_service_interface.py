from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.DTOs.exam_dto import ExamResponse

class IExamService(ABC):
    """Interface defining methods for exam-related operations"""
    
    @abstractmethod
    async def get_all_exams(self) -> List[ExamResponse]:
        """Get all exams with associated information
        
        Returns:
            List[ExamResponse]: List of exams with subject, teacher and group details
        """
        pass
    
    @abstractmethod
    async def get_exams_by_study_program(self, program_code: str) -> List[ExamResponse]:
        """Get exams filtered by study program
        
        Args:
            program_code (str): Short name of the study program
            
        Returns:
            List[ExamResponse]: Filtered list of exams
        """
        pass
        
    @abstractmethod
    async def get_exams_by_teacher_id(self, teacher_id: int) -> List[ExamResponse]:
        """Get exams assigned to a specific teacher
        
        Args:
            teacher_id (int): ID of the teacher
            
        Returns:
            List[ExamResponse]: List of exams for the teacher
        """
        pass
    
    @abstractmethod 
    async def get_exams_by_group_id(self, group_id: int) -> List[ExamResponse]:
        """Get exams for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            List[ExamResponse]: List of exams for the group
        """
        pass
