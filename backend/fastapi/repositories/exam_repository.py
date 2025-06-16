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
        
    async def update_sg_exam_statuses_to_pending(self) -> int:
        """Updates the status of exams for SG (Student Group) users to 'pending' status
        
        Returns:
            int: Number of exams updated
        """
        logger.info("[DEBUG] ExamRepository - update_sg_exam_statuses_to_pending: Starting execution")
        
        try:
            # Query to find schedules (exams) associated with SG users
            # The relation is: Schedule -> Subject -> Group -> users (where user.role == 'SG')
            query = (
                select(Schedule)
                .join(Schedule.subject)
                .join(Subject.group)
                .join(Group.users)  # This joins from Group to the Users who are the SG reps (plural: users)
                .where(
                    (User.role == "SG") & 
                    ((Schedule.status != "pending") | (Schedule.status.is_(None)))
                )
            )
            
            result = await self.db.execute(query)
            schedules = result.scalars().all()
            
            logger.info(f"[DEBUG] ExamRepository - Found {len(schedules)} SG exams to update")
            
            updated_count = 0
            for schedule in schedules:
                schedule.status = "pending"  # Set status to pending
                updated_count += 1
                
            await self.db.commit()
            
            logger.info(f"[DEBUG] ExamRepository - Updated {updated_count} exams to pending status")
            return updated_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[DEBUG] ExamRepository - Error in update_sg_exam_statuses_to_pending: {str(e)}")
            raise
        
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
                    joinedload(Schedule.subject).joinedload(Subject.teacher)
                    # We no longer have a direct relationship between Schedule and Room
                    # Instead, we have roomIds as a JSON array in Schedule
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
                    
                # Handle roomIds JSON array instead of direct room relation
                room_ids = schedule.get_room_ids()  # Use helper method from Schedule model
                room_id = None
                room_name = None
                
                # For backward compatibility, we'll use the first room ID if available
                if room_ids and len(room_ids) > 0:
                    # Get the first room ID and fetch the room
                    first_room_id = room_ids[0]
                    room_query = select(Room).where(Room.id == first_room_id)
                    room_result = await self.db.execute(room_query)
                    room = room_result.scalar_one_or_none()
                    
                    if room:
                        room_id = room.id
                        room_name = room.name
                
                # Handle nullable start and end times
                duration = None
                start_time = schedule.startTime
                end_time = schedule.endTime
                
                # Calculate duration only if both times are available
                if start_time is not None and end_time is not None:
                    # Calculate hours difference
                    hours_diff = end_time.hour - start_time.hour
                    if end_time.minute < start_time.minute:
                        hours_diff -= 1
                    
                    # Ensure duration is at least 1 hour
                    duration = max(1, hours_diff)
                
                # Create formatted exam entry with proper handling of nullable fields
                formatted_exam = {
                    "id": schedule.id,
                    "subjectId": subject.id,  # Only required field
                    "subjectName": subject.name,
                    "subjectShortName": subject.shortName,
                    "teacherId": teacher.id,
                    "teacherName": f"{teacher.lastName} {teacher.firstName}",
                    "teacherEmail": teacher.email,
                    "teacherPhone": teacher.phone,
                    "roomIds": schedule.get_room_ids(),  # New field with full list of room IDs
                    "roomId": room_id,        # Keep for backward compatibility (first room or null)
                    "roomName": room_name,     # Keep for backward compatibility (first room name or null)
                    "date": schedule.date,     # Nullable
                    "startTime": schedule.startTime, # Nullable
                    "endTime": schedule.endTime,   # Nullable
                    "duration": duration,      # Calculated field, may be None
                    "status": schedule.status, # Nullable
                    "message": schedule.message, # New nullable message field
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
            
    async def get_subject_ids_by_group_id(self, group_id: int) -> List[int]:
        """Get all subject IDs for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            List[int]: List of subject IDs for the group
        """
        logger.info(f"[DEBUG] ExamRepository - get_subject_ids_by_group_id: {group_id}")
        
        try:
            # Get subjects for the specified group using a join query
            query = (
                select(Subject.id)
                .join(Subject.group)
                .where(Group.id == group_id)
            )
            
            result = await self.db.execute(query)
            subject_ids = [row[0] for row in result.all()]
            
            logger.info(f"[DEBUG] ExamRepository - Found {len(subject_ids)} subjects for group {group_id}")
            return subject_ids
            
        except Exception as e:
            logger.error(f"[DEBUG] ExamRepository - Error in get_subject_ids_by_group_id: {str(e)}")
            raise
            
    async def update_exam(self, exam_id: int, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an exam with new information
        
        Args:
            exam_id (int): ID of the exam to update
            exam_data (Dict[str, Any]): Updated exam data including date, location, professor, etc.
            
        Returns:
            Dict[str, Any]: Updated exam data
        """
        logger.info(f"[DEBUG] ExamRepository - update_exam: {exam_id}")
        
        try:
            # Get the exam schedule by ID
            query = select(Schedule).where(Schedule.id == exam_id)
            result = await self.db.execute(query)
            schedule = result.scalars().first()
            
            if not schedule:
                logger.error(f"[DEBUG] ExamRepository - Exam with ID {exam_id} not found")
                raise ValueError(f"Exam with ID {exam_id} not found")
            
            # Update schedule fields
            if "date" in exam_data:
                schedule.date = exam_data["date"]
            if "startTime" in exam_data:
                schedule.startTime = exam_data["startTime"]
            if "endTime" in exam_data:
                schedule.endTime = exam_data["endTime"]
            if "status" in exam_data:
                schedule.status = exam_data["status"]
            if "notes" in exam_data:
                schedule.notes = exam_data["notes"]
                
            # Update room if provided
            if "roomId" in exam_data:
                room_query = select(Room).where(Room.id == exam_data["roomId"])
                room_result = await self.db.execute(room_query)
                room = room_result.scalars().first()
                
                if room:
                    schedule.room = room
                else:
                    logger.warning(f"[DEBUG] ExamRepository - Room with ID {exam_data['roomId']} not found")
            
            # Update teacher if provided
            if "teacherId" in exam_data:
                # We need to update the teacher in the subject relation
                subject = schedule.subject
                if subject:
                    teacher_query = select(User).where(User.id == exam_data["teacherId"])
                    teacher_result = await self.db.execute(teacher_query)
                    teacher = teacher_result.scalars().first()
                    
                    if teacher:
                        subject.teacher = teacher
                    else:
                        logger.warning(f"[DEBUG] ExamRepository - Teacher with ID {exam_data['teacherId']} not found")
                else:
                    logger.warning(f"[DEBUG] ExamRepository - Schedule {exam_id} has no subject relation")
            
            # Commit the changes
            await self.db.commit()
            
            # Refresh the schedule
            await self.db.refresh(schedule)
            
            # Get the updated exam with details
            all_exams = await self.get_all_exams_with_details()
            updated_exam = next((exam for exam in all_exams if exam["id"] == exam_id), None)
            
            if updated_exam:
                logger.info(f"[DEBUG] ExamRepository - Successfully updated exam {exam_id}")
                return updated_exam
            else:
                logger.error(f"[DEBUG] ExamRepository - Failed to retrieve updated exam {exam_id}")
                raise ValueError(f"Failed to retrieve updated exam {exam_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[DEBUG] ExamRepository - Error in update_exam: {str(e)}")
            raise

    async def create_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new exam proposal or scheduled exam
        
        Args:
            exam_data (Dict[str, Any]): Exam data including subject ID, date, time, etc.
            
        Returns:
            Dict[str, Any]: Created exam data with ID and other details
        """
        logger.info(f"[DEBUG] ExamRepository - Creating new exam for subject {exam_data.get('subjectId')}")
        
        try:
            # First check if there's an existing schedule for this subject
            if 'subjectId' in exam_data:
                subject_id = exam_data['subjectId']
                existing_schedule_query = select(Schedule).where(Schedule.subjectId == subject_id)
                result = await self.db.execute(existing_schedule_query)
                existing_schedule = result.scalars().first()
                
                if existing_schedule:
                    # If an exam already exists for this subject, update it instead of creating a new one
                    logger.info(f"[DEBUG] ExamRepository - Found existing exam for subject {subject_id}, updating instead")
                    
                    # Update the schedule with proposed date/time
                    if 'date' in exam_data:
                        existing_schedule.date = exam_data['date']
                    if 'startTime' in exam_data:
                        existing_schedule.startTime = exam_data['startTime']
                    if 'endTime' in exam_data:
                        existing_schedule.endTime = exam_data['endTime']
                    
                    # Set status to the value provided in exam_data, default to 'proposed' if not specified
                    existing_schedule.status = exam_data.get('status', 'proposed') 
                    
                    # Commit the changes
                    await self.db.commit()
                    await self.db.refresh(existing_schedule)
                    
                    # Get the updated exam with all details
                    all_exams = await self.get_all_exams_with_details()
                    updated_exam = next((exam for exam in all_exams if exam["id"] == existing_schedule.id), None)
                    
                    if updated_exam:
                        return updated_exam
                    else:
                        logger.error(f"[DEBUG] ExamRepository - Updated exam with ID {existing_schedule.id} not found in details list")
                        raise ValueError(f"Updated exam with ID {existing_schedule.id} not found")
            
            # No existing schedule found, create a new one
            new_schedule = Schedule()
            
            # Set basic attributes
            if 'date' in exam_data:
                new_schedule.date = exam_data['date']
            if 'startTime' in exam_data:
                new_schedule.startTime = exam_data['startTime']
            if 'endTime' in exam_data:
                new_schedule.endTime = exam_data['endTime']
            # Properly handle exam status based on the input or set default
            if 'status' in exam_data:
                # Use status from the input data
                new_schedule.status = exam_data['status']
                logger.info(f"[DEBUG] ExamRepository - Setting status from input: {exam_data['status']}")
            else:
                # Set default status for proposed exams
                new_schedule.status = 'proposed'  # Default for new proposed exams
                logger.info(f"[DEBUG] ExamRepository - Setting default status: proposed")
            
            # Set relationships
            if 'subjectId' in exam_data:
                # Get the subject
                subject_query = select(Subject).where(Subject.id == exam_data['subjectId'])
                result = await self.db.execute(subject_query)
                subject = result.scalars().first()
                
                if subject:
                    new_schedule.subject = subject
                    # Subject already contains the group information, so we can access it via this relationship
                    logger.info(f"[DEBUG] ExamRepository - Proposal for subject {subject.id} by group {subject.groupId}")
                else:
                    raise ValueError(f"Subject with ID {exam_data['subjectId']} not found")
            else:
                raise ValueError("Subject ID is required for exam creation")
            
            # Handle room requirement (roomId is NOT NULL in database)
            if 'roomId' in exam_data and exam_data['roomId']:
                # Get the room
                room_query = select(Room).where(Room.id == exam_data['roomId'])
                result = await self.db.execute(room_query)
                room = result.scalars().first()
                
                if room:
                    new_schedule.room = room
                else:
                    raise ValueError(f"Room with ID {exam_data['roomId']} not found")
            else:
                # For proposals, use a default room (to meet NOT NULL constraint)
                # First try to get room with ID 1 (assuming this is a default room)
                default_room_query = select(Room).limit(1)
                result = await self.db.execute(default_room_query)
                default_room = result.scalars().first()
                
                if default_room:
                    new_schedule.room = default_room
                    logger.info(f"[DEBUG] ExamRepository - Using default room (ID: {default_room.id}) for new exam proposal")
                else:
                    raise ValueError("Cannot create exam proposal: No rooms found in database (roomId cannot be NULL)")
                
            # Add and commit
            self.db.add(new_schedule)
            await self.db.commit()
            await self.db.refresh(new_schedule)
            
            # Get the created exam with all details
            all_exams = await self.get_all_exams_with_details()
            created_exam = next((exam for exam in all_exams if exam["id"] == new_schedule.id), None)
            
            if created_exam:
                return created_exam
            else:
                logger.error(f"[DEBUG] ExamRepository - Created exam with ID {new_schedule.id} not found in details list")
                raise ValueError(f"Created exam with ID {new_schedule.id} not found")
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[DEBUG] ExamRepository - Error in create_exam: {str(e)}")
            raise
