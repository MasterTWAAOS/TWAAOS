from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Dict, Any
from datetime import date
import logging

from models.schedule import Schedule
from models.subject import Subject
from models.user import User
from models.room import Room
from models.group import Group
from repositories.abstract.exam_repository_interface import IExamRepository

logger = logging.getLogger(__name__)

class ExamRepository(IExamRepository):
    """Repository implementation for exam-related operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_all_exams_with_details(self) -> List[Dict[str, Any]]:
        """Get all exams with joined details from related tables
        
        Returns:
            List[Dict[str, Any]]: List of exam data with subject, teacher, room and group details
        """
        logger.info("[DEBUG] ExamRepository - get_all_exams_with_details: Starting execution")
        
        try:
            # Build a query that joins schedules with related tables
            query = (
                select(Schedule)
                .options(
                    joinedload(Schedule.subject).joinedload(Subject.group),
                    joinedload(Schedule.subject).joinedload(Subject.teacher),
                    joinedload(Schedule.room)
                )
            )
            
            # Execute the query
            result = await self.db.execute(query)
            schedules = result.unique().scalars().all()
            
            logger.info(f"[DEBUG] ExamRepository - Query returned {len(schedules)} schedules")
            
            # Format the result with calculated fields
            formatted_exams = []
            for schedule in schedules:
                # Get associated objects safely
                subject = schedule.subject
                if not subject:
                    logger.warning(f"[DEBUG] ExamRepository - Schedule {schedule.id} has no subject relation")
                    continue
                    
                group = subject.group
                if not group:
                    logger.warning(f"[DEBUG] ExamRepository - Subject {subject.id} has no group relation")
                    continue
                    
                teacher = subject.teacher
                if not teacher:
                    logger.warning(f"[DEBUG] ExamRepository - Subject {subject.id} has no teacher relation")
                    continue
                    
                room = schedule.room
                if not room:
                    logger.warning(f"[DEBUG] ExamRepository - Schedule {schedule.id} has no room relation")
                    continue
                
                # Calculate duration in hours
                start_time = schedule.startTime
                end_time = schedule.endTime
                
                # Calculate hours difference
                hours_diff = end_time.hour - start_time.hour
                if end_time.minute < start_time.minute:
                    hours_diff -= 1
                
                # Ensure duration is at least 1 hour
                duration = max(1, hours_diff)
                
                # Create formatted exam entry
                formatted_exam = {
                    "id": schedule.id,
                    "subjectId": subject.id,
                    "subjectName": subject.name,
                    "subjectShortName": subject.shortName,
                    "teacherId": teacher.id,
                    "teacherName": f"{teacher.lastName} {teacher.firstName}",
                    "teacherEmail": teacher.email,
                    "teacherPhone": teacher.phone,
                    "roomId": room.id,
                    "roomName": room.name,
                    "date": schedule.date,
                    "startTime": schedule.startTime,
                    "endTime": schedule.endTime,
                    "duration": duration,
                    "status": schedule.status,
                    "groupId": group.id,
                    "groupName": group.name,
                    "specializationShortName": group.specializationShortName,
                    "studyYear": group.studyYear
                }
                formatted_exams.append(formatted_exam)
            
            logger.info(f"[DEBUG] ExamRepository - Formatted {len(formatted_exams)} exam records")
            return formatted_exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamRepository - Error in get_all_exams_with_details: {str(e)}")
            raise
    
    async def get_exams_by_study_program(self, program_code: str) -> List[Dict[str, Any]]:
        """Get exams filtered by study program
        
        Args:
            program_code (str): Short name of the study program
            
        Returns:
            List[Dict[str, Any]]: Filtered list of exam data
        """
        logger.info(f"[DEBUG] ExamRepository - get_exams_by_study_program: {program_code}")
        
        try:
            # Get all exams with details first
            all_exams = await self.get_all_exams_with_details()
            
            # Filter by program code
            filtered_exams = [
                exam for exam in all_exams
                if exam["specializationShortName"] == program_code
            ]
            
            logger.info(f"[DEBUG] ExamRepository - Found {len(filtered_exams)} exams for program {program_code}")
            return filtered_exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamRepository - Error in get_exams_by_study_program: {str(e)}")
            raise
        
    async def get_exams_by_teacher_id(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get exams for a specific teacher
        
        Args:
            teacher_id (int): ID of the teacher
            
        Returns:
            List[Dict[str, Any]]: List of exam data for the teacher
        """
        logger.info(f"[DEBUG] ExamRepository - get_exams_by_teacher_id: {teacher_id}")
        
        try:
            # Get all exams with details first
            all_exams = await self.get_all_exams_with_details()
            
            # Filter by teacher ID
            filtered_exams = [
                exam for exam in all_exams
                if exam["teacherId"] == teacher_id
            ]
            
            logger.info(f"[DEBUG] ExamRepository - Found {len(filtered_exams)} exams for teacher {teacher_id}")
            return filtered_exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamRepository - Error in get_exams_by_teacher_id: {str(e)}")
            raise
    
    async def get_exams_by_group_id(self, group_id: int) -> List[Dict[str, Any]]:
        """Get exams for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            List[Dict[str, Any]]: List of exam data for the group
        """
        logger.info(f"[DEBUG] ExamRepository - get_exams_by_group_id: {group_id}")
        
        try:
            # Get all exams with details first
            all_exams = await self.get_all_exams_with_details()
            
            # Filter by group ID
            filtered_exams = [
                exam for exam in all_exams
                if exam["groupId"] == group_id
            ]
            
            logger.info(f"[DEBUG] ExamRepository - Found {len(filtered_exams)} exams for group {group_id}")
            return filtered_exams
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamRepository - Error in get_exams_by_group_id: {str(e)}")
            raise
