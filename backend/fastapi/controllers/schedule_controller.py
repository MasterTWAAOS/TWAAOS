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
def get_all_schedules(
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get all schedules endpoint.
    
    Returns:
        List[ScheduleResponse]: A list of all schedules
    """
    return service.get_all_schedules()

@router.get("/{schedule_id}", response_model=ScheduleResponse, summary="Get schedule by ID", description="Retrieve a specific schedule by its ID")
@inject
def get_schedule(
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
    schedule = service.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    return schedule

@router.get("/group/{group_id}", response_model=List[ScheduleResponse], summary="Get schedules by group ID", description="Retrieve all schedules for a specific group")
@inject
def get_schedules_by_group(
    group_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific group.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified group
    """
    return service.get_schedules_by_group_id(group_id)

@router.get("/teacher/{teacher_id}", response_model=List[ScheduleResponse], summary="Get schedules by teacher ID", description="Retrieve all schedules for a specific teacher")
@inject
def get_schedules_by_teacher(
    teacher_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific teacher.
    
    Args:
        teacher_id (int): The ID of the teacher
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified teacher
    """
    return service.get_schedules_by_teacher_id(teacher_id)

@router.get("/room/{room_id}", response_model=List[ScheduleResponse], summary="Get schedules by room ID", description="Retrieve all schedules for a specific room")
@inject
def get_schedules_by_room(
    room_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific room.
    
    Args:
        room_id (int): The ID of the room
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified room
    """
    return service.get_schedules_by_room_id(room_id)

@router.get("/subject/{subject_id}", response_model=List[ScheduleResponse], summary="Get schedules by subject ID", description="Retrieve all schedules for a specific subject")
@inject
def get_schedules_by_subject(
    subject_id: int, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific subject.
    
    Args:
        subject_id (int): The ID of the subject
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified subject
    """
    return service.get_schedules_by_subject_id(subject_id)

@router.get("/date/{schedule_date}", response_model=List[ScheduleResponse], summary="Get schedules by date", description="Retrieve all schedules for a specific date")
@inject
def get_schedules_by_date(
    schedule_date: date, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules for a specific date.
    
    Args:
        schedule_date (date): The date to retrieve schedules for
        
    Returns:
        List[ScheduleResponse]: A list of schedules for the specified date
    """
    return service.get_schedules_by_date(schedule_date)

@router.get("/status/{status}", response_model=List[ScheduleResponse], summary="Get schedules by status", description="Retrieve all schedules with a specific status")
@inject
def get_schedules_by_status(
    status: str, 
    service: IScheduleService = Depends(Provide[Container.schedule_service])
):
    """Get schedules with a specific status.
    
    Args:
        status (str): The status to filter by (e.g., 'propus', 'acceptat', 'respins')
        
    Returns:
        List[ScheduleResponse]: A list of schedules with the specified status
    """
    return service.get_schedules_by_status(status)

@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED, summary="Create new schedule", description="Create a new schedule in the system")
@inject
def create_schedule(
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
        return service.create_schedule(schedule_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{schedule_id}", response_model=ScheduleResponse, summary="Update schedule", description="Update an existing schedule's information")
@inject
def update_schedule(
    schedule_id: int, 
    schedule_data: ScheduleUpdate, 
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
    try:
        updated_schedule = service.update_schedule(schedule_id, schedule_data)
        if not updated_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with ID {schedule_id} not found"
            )
        return updated_schedule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete schedule", description="Delete a schedule from the system")
@inject
def delete_schedule(
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
    success = service.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    return None
