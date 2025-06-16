from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Dict, Any
from datetime import date, datetime, time
import logging

from models.schedule import Schedule
from models.subject import Subject
from models.room import Room
from repositories.abstract.schedule_repository_interface import IScheduleRepository

logger = logging.getLogger(__name__)

class ScheduleRepository(IScheduleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Schedule]:
        result = await self.db.execute(select(Schedule))
        return result.scalars().all()

    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.id == schedule_id))
        return result.scalar_one_or_none()
    
    async def get_by_assistant_id(self, assistant_id: int) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.assistantId == assistant_id))
        return result.scalars().all()
    
    async def get_by_room_id(self, room_id: int) -> List[Schedule]:
        # Need to query the JSON array column for containment
        # Using the JSON containment operator to find schedules where roomIds contains the room_id
        query = select(Schedule).filter(Schedule.roomIds.contains([room_id]))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_subject_id(self, subject_id: int) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.subjectId == subject_id))
        return result.scalars().all()
    
    async def get_by_date(self, schedule_date: date) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.date == schedule_date))
        return result.scalars().all()
    
    async def get_by_status(self, status: str) -> List[Schedule]:
        result = await self.db.execute(select(Schedule).filter(Schedule.status == status))
        return result.scalars().all()

    async def create(self, schedule: Schedule) -> Schedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def update(self, schedule: Schedule) -> Schedule:
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def delete(self, schedule_id: int) -> bool:
        schedule = await self.get_by_id(schedule_id)
        if schedule:
            await self.db.delete(schedule)
            await self.db.commit()
            return True
        return False
    
    async def delete_all_schedules(self) -> int:
        """Delete all schedule records
        
        Returns:
            int: Number of deleted records
        """
        logger.info("[DEBUG] Repository - delete_all_schedules: Starting execution")
        try:
            # Create a delete statement for all schedules
            delete_stmt = delete(Schedule)
            
            # Execute the delete statement and get the result
            result = await self.db.execute(delete_stmt)
            
            # Commit the transaction
            await self.db.commit()
            
            # Return the number of rows deleted
            deleted_count = result.rowcount
            logger.info(f"[DEBUG] Repository - delete_all_schedules: Deleted {deleted_count} schedules")
            return deleted_count
        except Exception as e:
            logger.error(f"[DEBUG] Repository - delete_all_schedules error: {str(e)}")
            raise
    
    async def populate_from_subjects(self) -> Dict[str, Any]:
        """Populate schedules table with preliminary entries based on subjects
        
        This creates initial schedule entries for each subject in the database,
        allowing users to modify dates and times later
        
        Returns:
            Dict[str, Any]: Statistics about the population process
        """
        logger.info("[DEBUG] Repository - populate_from_subjects: Starting execution")
        stats = {
            "processed": 0,
            "created": 0,
            "errors": 0,
            "error_details": []
        }
        
        try:
            # First, get all subjects joined with their groups and teachers
            logger.info("[DEBUG] Repository - Querying all subjects")
            query = select(Subject).order_by(Subject.id)
            result = await self.db.execute(query)
            subjects = result.scalars().all()
            
            logger.info(f"[DEBUG] Repository - Found {len(subjects)} subjects to process")
            
            if not subjects:
                logger.warning("[DEBUG] Repository - No subjects found to create schedules from")
                return stats
            
            # We'll set most fields to None to utilize the nullable fields
            # This allows other roles to progressively populate the schedule data
            # The only required field is subjectId
            
            # Process each subject
            for subject in subjects:
                try:
                    stats["processed"] += 1
                    
                    # Create a new schedule for this subject with only the required subjectId
                    # All other fields are set to None or default values to utilize the nullable fields we've implemented
                    # This supports the multi-role workflow where different roles progressively fill data
                    new_schedule = Schedule(
                        subjectId=subject.id,
                        roomIds=[],        # Start with empty list of room IDs
                        date=None,         # Nullable field - will be filled by appropriate role
                        startTime=None,    # Nullable field - will be filled by appropriate role
                        endTime=None,      # Nullable field - will be filled by appropriate role
                        status=None,       # Nullable field - will be filled by appropriate role
                        message=None       # New nullable field for messages from CD to SG
                    )
                    
                    # Add to database
                    self.db.add(new_schedule)
                    await self.db.flush()
                    
                    stats["created"] += 1
                    
                    # Log progress every 50 subjects
                    if stats["processed"] % 50 == 0:
                        logger.info(f"[DEBUG] Repository - Processed {stats['processed']}/{len(subjects)} subjects")
                        
                except Exception as subject_error:
                    stats["errors"] += 1
                    error_msg = f"Error creating schedule for subject ID {subject.id}: {str(subject_error)}"
                    stats["error_details"].append(error_msg)
                    logger.error(f"[DEBUG] Repository - {error_msg}")
            
            # Commit all changes at once
            await self.db.commit()
            
            logger.info(f"[DEBUG] Repository - populate_from_subjects completed: "
                      f"{stats['created']} schedules created, {stats['errors']} errors")
            
            return stats
            
        except Exception as e:
            logger.error(f"[DEBUG] Repository - populate_from_subjects error: {str(e)}")
            raise
