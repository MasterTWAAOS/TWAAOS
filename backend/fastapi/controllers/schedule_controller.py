from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from dependency_injector.wiring import inject, Provide

from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from models.DTOs.user_dto import UserResponse
from services.abstract.schedule_service_interface import IScheduleService
from config.containers import Container

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("", response_model=List[ScheduleResponse], summary="Get all schedules", description="Retrieve a list of all schedules in the system")
@inject
async def get_all_schedules(
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get all schedules endpoint.
    
    Returns:
        List[ScheduleResponse]: A list of all schedules
    """
    return await service.get_all_schedules()

@router.get("/{schedule_id}", response_model=ScheduleResponse, summary="Get schedule by ID", description="Retrieve a specific schedule by its ID")
@inject
async def get_schedule(
    schedule_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get a specific schedule by ID.
    
    Args:
        schedule_id (int): The ID of the schedule to retrieve
        
    Returns:
        ScheduleResponse: The schedule details
        
    Raises:
        HTTPException: If the schedule is not found
    """
    schedule = await service.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    return schedule

# Endpoint removed: groupId is no longer associated with schedules

# Endpoint removed: teacher/assistantId is now associated with subjects, not schedules

@router.get("/room/{room_id}", response_model=List[ScheduleResponse], summary="Get schedules by room", description="Retrieve all schedules for a specific room")
@inject
async def get_schedules_by_room(
    room_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific room.
    
    Args:
        room_id (int): The ID of the room
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified room
    """
    return await service.get_schedules_by_room_id(room_id)

@router.get("/subject/{subject_id}", response_model=List[ScheduleResponse], summary="Get schedules by subject", description="Retrieve all schedules for a specific subject")
@inject
async def get_schedules_by_subject(
    subject_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific subject.
    
    Args:
        subject_id (int): The ID of the subject
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified subject
    """
    return await service.get_schedules_by_subject_id(subject_id)

@router.get("/date/{schedule_date}", response_model=List[ScheduleResponse], summary="Get schedules by date", description="Retrieve all schedules for a specific date")
@inject
async def get_schedules_by_date(
    schedule_date: date, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific date.
    
    Args:
        schedule_date (date): The date to retrieve schedules for
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified date
    """
    return await service.get_schedules_by_date(schedule_date)

@router.get("/status/{status}", response_model=List[ScheduleResponse], summary="Get schedules by status", description="Retrieve all schedules with a specific status")
@inject
async def get_schedules_by_status(
    status: str, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules with a specific status.
    
    Args:
        status (str): The status to filter by (e.g., 'pending', 'proposed', 'approved', 'rejected')
        
    Returns:
        List[ScheduleResponse]: A list of schedules with the specified status
    """
    return await service.get_schedules_by_status(status)
    
@router.get("/teacher/{teacher_id}", response_model=List[ScheduleResponse], summary="Get schedules by teacher ID", description="Retrieve all schedules for subjects where the specified teacher is the professor")
@inject
async def get_schedules_by_teacher(
    teacher_id: int,
    status: Optional[str] = None,
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific teacher's subjects.
    
    Args:
        teacher_id (int): The ID of the teacher (professor/CD)
        status (Optional[str]): Optional status filter (e.g., 'pending', 'proposed', 'approved', 'rejected')
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the teacher's subjects
    """
    # Get all schedules for the teacher's subjects
    schedules = await service.get_schedules_by_teacher_id(teacher_id)
    
    # Apply status filter if provided
    if status:
        schedules = [s for s in schedules if s.status == status]
        
    return schedules

@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED, summary="Create new schedule", description="Create a new schedule in the system")
@inject
async def create_schedule(
    schedule_data: ScheduleCreate, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Create a new schedule.
    
    Args:
        schedule_data (ScheduleCreate): The schedule data for creation
        
    Returns:
        ScheduleResponse: The created schedule details
        
    Raises:
        HTTPException: If validation fails for foreign keys
    """
    try:
        return await service.create_schedule(schedule_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

from fastapi.encoders import jsonable_encoder
from fastapi import Body

@router.get("/assistants/{subject_id}", response_model=List[UserResponse], summary="Get assistants for a subject", description="Get all assistants (CD users) associated with a specific subject")
@inject
async def get_subject_assistants(
    subject_id: int,
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get all assistants associated with a specific subject.
    
    Args:
        subject_id (int): The ID of the subject
        
    Returns:
        List[UserResponse]: A list of users who are assistants for this subject
    """
    # First validate that the subject exists
    subject_valid, error_msg = await service.validate_subject_id(subject_id)
    if not subject_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )
    
    return await service.get_subject_assistants(subject_id)

@router.put("/{schedule_id}", response_model=ScheduleResponse, summary="Update schedule", description="Update an existing schedule's information")
@inject
async def update_schedule(
    schedule_id: int, 
    # Allow direct JSON data to help with validations
    schedule_data: ScheduleUpdate = Body(...),
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Update an existing schedule.
    
    Args:
        schedule_id (int): The ID of the schedule to update
        schedule_data (ScheduleUpdate): The updated schedule data
        
    Returns:
        ScheduleResponse: The updated schedule details
        
    Raises:
        HTTPException: If the schedule is not found or validation fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the received data for debugging
    logger.info(f"[DEBUG] Updating schedule {schedule_id} with data: {schedule_data}")
    
    # Make sure date and time fields are properly formatted
    try:
        # Check for time format issues - these are common causes of 422 errors
        if schedule_data.startTime and not isinstance(schedule_data.startTime, str):
            logger.info(f"[DEBUG] startTime format: {type(schedule_data.startTime)}")
            
        if schedule_data.endTime and not isinstance(schedule_data.endTime, str):
            logger.info(f"[DEBUG] endTime format: {type(schedule_data.endTime)}")
    
        # Proceed with update
        updated_schedule = await service.update_schedule(schedule_id, schedule_data)
        if not updated_schedule:
            logger.error(f"[DEBUG] Schedule with ID {schedule_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with ID {schedule_id} not found"
            )
        logger.info(f"[DEBUG] Successfully updated schedule {schedule_id}")
        return updated_schedule
    except ValueError as e:
        logger.error(f"[DEBUG] Value error updating schedule {schedule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[DEBUG] Unexpected error updating schedule {schedule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating schedule: {str(e)}"
        )

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete schedule", description="Delete a schedule by ID")
@inject
async def delete_schedule(
    schedule_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Delete a schedule.
    
    Args:
        schedule_id (int): The ID of the schedule to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the schedule is not found
    """
    result = await service.delete_schedule(schedule_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    return None


class ConflictCheckRequest(BaseModel):
    date: date
    startTime: str
    endTime: str
    scheduleId: int
    roomIds: List[int]
    assistantIds: List[int]


@router.post("/check-conflicts", summary="Check scheduling conflicts", description="Check for conflicts with rooms, assistants, and teacher availability")
@inject
async def check_conflicts(
    conflict_data: ConflictCheckRequest, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Check for scheduling conflicts.
    
    Args:
        conflict_data (ConflictCheckRequest): Data for conflict checking
        
    Returns:
        Dict: Conflict information including roomConflicts, assistantConflicts, and teacherConflicts
    """
    # Convert string times to actual time objects if needed by the service
    result = await service.check_conflicts(
        schedule_id=conflict_data.scheduleId,
        date=conflict_data.date,
        start_time=conflict_data.startTime,
        end_time=conflict_data.endTime,
        room_ids=conflict_data.roomIds,
        assistant_ids=conflict_data.assistantIds
    )
    return result
