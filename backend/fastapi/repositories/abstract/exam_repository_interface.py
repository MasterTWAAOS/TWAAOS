from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

class IExamRepository(ABC):
    """Interface for exam repository operations"""
    
    @abstractmethod
    async def update_sg_exam_statuses_to_pending(self) -> int:
        """Updates the status of exams for SG (Student Group) users to 'pending' status
        
        Returns:
            int: Number of exams updated
        """
        pass
    
    @abstractmethod
    async def get_all_exams_with_details(self) -> List[Dict[str, Any]]:
        """Get all exams with joined details from related tables
        
        Returns:
            List[Dict[str, Any]]: List of exam data with subject, teacher, room and group details
        """
        pass
    
    @abstractmethod
    async def get_exams_by_study_program(self, program_code: str) -> List[Dict[str, Any]]:
        """Get exams filtered by study program
        
        Args:
            program_code (str): Short name of the study program
            
        Returns:
            List[Dict[str, Any]]: Filtered list of exam data
        """
        pass
        
    @abstractmethod
    async def get_exams_by_teacher_id(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get exams for a specific teacher
        
        Args:
            teacher_id (int): ID of the teacher
            
        Returns:
            List[Dict[str, Any]]: List of exam data for the teacher
        """
        pass
    
    @abstractmethod
    async def get_exams_by_group_id(self, group_id: int) -> List[Dict[str, Any]]:
        """Get exams for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            List[Dict[str, Any]]: List of exam data for the group
        """
        pass
    
    @abstractmethod
    async def update_exam(self, exam_id: int, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an exam with new information
        
        Args:
            exam_id (int): ID of the exam to update
            exam_data (Dict[str, Any]): Updated exam data including date, location, professor, etc.
            
        Returns:
            Dict[str, Any]: Updated exam data
        """
        pass
    
    @abstractmethod
    async def create_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new exam proposal or scheduled exam
        
        Args:
            exam_data (Dict[str, Any]): Exam data including subject ID, group ID, date, time, etc.
            
        Returns:
            Dict[str, Any]: Created exam data with ID and other details
        """
        pass
