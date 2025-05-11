from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependency_injector.wiring import inject, Provide

from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse
from services.abstract.subject_service_interface import ISubjectService
from config.containers import Container

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("", response_model=List[SubjectResponse], summary="Get all subjects", description="Retrieve a list of all subjects in the system")
@inject
def get_all_subjects(
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get all subjects endpoint.
    
    Returns:
        List[SubjectResponse]: A list of all subjects
    """
    return service.get_all_subjects()

@router.get("/{subject_id}", response_model=SubjectResponse, summary="Get subject by ID", description="Retrieve a specific subject by its ID")
@inject
def get_subject(
    subject_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get a specific subject by ID.
    
    Args:
        subject_id (int): The ID of the subject to retrieve
        
    Returns:
        SubjectResponse: The subject details
        
    Raises:
        HTTPException: If the subject is not found
    """
    subject = service.get_subject_by_id(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return subject

@router.get("/group/{group_id}", response_model=List[SubjectResponse], summary="Get subjects by group ID", description="Retrieve all subjects for a specific group")
@inject
def get_subjects_by_group(
    group_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get subjects for a specific group.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        List[SubjectResponse]: A list of subjects for the specified group
    """
    return service.get_subjects_by_group_id(group_id)

@router.get("/teacher/{teacher_id}", response_model=List[SubjectResponse], summary="Get subjects by teacher ID", description="Retrieve all subjects for a specific teacher")
@inject
def get_subjects_by_teacher(
    teacher_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get subjects for a specific teacher.
    
    Args:
        teacher_id (int): The ID of the teacher
        
    Returns:
        List[SubjectResponse]: A list of subjects for the specified teacher
    """
    return service.get_subjects_by_teacher_id(teacher_id)

@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Create new subject", description="Create a new subject in the system")
@inject
def create_subject(
    subject_data: SubjectCreate, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Create a new subject.
    
    Args:
        subject_data (SubjectCreate): The subject data for creation
        
    Returns:
        SubjectResponse: The created subject details
    """
    return service.create_subject(subject_data)

@router.put("/{subject_id}", response_model=SubjectResponse, summary="Update subject", description="Update an existing subject's information")
@inject
def update_subject(
    subject_id: int, 
    subject_data: SubjectUpdate, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Update an existing subject.
    
    Args:
        subject_id (int): The ID of the subject to update
        subject_data (SubjectUpdate): The updated subject data
        
    Returns:
        SubjectResponse: The updated subject details
        
    Raises:
        HTTPException: If the subject is not found
    """
    updated_subject = service.update_subject(subject_id, subject_data)
    if not updated_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return updated_subject

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete subject", description="Delete a subject from the system")
@inject
def delete_subject(
    subject_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Delete a subject.
    
    Args:
        subject_id (int): The ID of the subject to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the subject is not found
    """
    success = service.delete_subject(subject_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return None
