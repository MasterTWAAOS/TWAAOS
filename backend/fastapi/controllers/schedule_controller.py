from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date
from dependency_injector.wiring import inject, Provide

from models.DTOs.schedule_dto import ScheduleCreate, ScheduleUpdate, ScheduleResponse
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

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete schedule", description="Delete a schedule from the system")
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
    success = await service.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    return None
