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
        
    @abstractmethod
    async def update_exam(self, exam_id: int, exam_data: Dict[str, Any]) -> ExamResponse:
        """Update an exam with new information
        
        Args:
            exam_id (int): ID of the exam to update
            exam_data (Dict[str, Any]): Updated exam data including date, location, professor, etc.
            
        Returns:
            ExamResponse: Updated exam data response
        """
        pass
        
    @abstractmethod
    async def create_exam_proposal(self, proposal_data: Dict[str, Any]) -> ExamResponse:
        """Create a new exam proposal from a student group
        
        Args:
            proposal_data (Dict[str, Any]): Proposal data including subject ID, date, time, group ID
            
        Returns:
            ExamResponse: Created exam proposal with details
        """
        pass
