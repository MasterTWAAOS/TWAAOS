import logging

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.exam_service_interface import IExamService
from services.abstract.user_service_interface import IUserService
from config.containers import Container
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("", response_model=List[SubjectResponse], summary="Get all subjects", description="Retrieve a list of all subjects in the system")
@inject
async def get_all_subjects(
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get all subjects endpoint.
    
    Returns:
        List[SubjectResponse]: A list of all subjects
    """
    return await service.get_all_subjects()

@router.get("/{subject_id}", response_model=SubjectResponse, summary="Get subject by ID", description="Retrieve a specific subject by its ID")
@inject
async def get_subject(
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
    subject = await service.get_subject_by_id(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return subject

@router.get("/group/{group_id}", response_model=List[SubjectResponse], summary="Get subjects by group", description="Retrieve all subjects for a specific group")
@inject
async def get_subjects_by_group(
    group_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get subjects for a specific group.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        List[SubjectResponse]: A list of subjects for the specified group
    """
    return await service.get_subjects_by_group_id(group_id)

@router.get("/group/{group_id}/pending", response_model=List[SubjectResponse], summary="Get subjects needing proposals", description="Retrieve subjects that need exam date proposals for a specific group")
@inject
async def get_pending_subjects_by_group(
    group_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service]),
    exam_service: IExamService = Depends(Provide[Container.exam_service]),
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """Get subjects that need an exam date proposal for a specific group.
    
    Args:
        group_id (int): The ID of the group to retrieve pending exam subjects for
        
    Returns:
        List[SubjectResponse]: List of subjects without proposed exam dates
    """
    # Get all subjects for the group
    subjects = await service.get_subjects_by_group_id(group_id)
    
    # Get all exams for the group to check which subjects already have proposals
    exams = await exam_service.get_exams_by_group_id(group_id)
    
    # Log how many subjects and exams we found
    logger.info(f"[DEBUG] Found {len(subjects)} total subjects for group {group_id}")
    logger.info(f"[DEBUG] Found {len(exams)} exams for group {group_id}")
    
    # Find subjects that this specific group has already proposed exams for
    # We need to check if each exam is specifically proposed by THIS group
    subjects_with_proposals_by_this_group = set()
    
    for exam in exams:
        # Check if this exam is proposed by this group specifically
        # We consider an exam to be proposed by this group if:
        # 1. The subject belongs to this group
        # 2. The status is 'proposed', 'pending', 'approved' or similar
        # Since we can't rely on proposedByGroupId field, we'll have to infer from status
        if hasattr(exam, 'subjectId') and exam.subjectId:
            # Check if exam status indicates it's a proposal
            status_lower = exam.status.lower() if hasattr(exam, 'status') and exam.status else ''
            # Only exclude subjects with proposals that are proposed or approved
            # We want to INCLUDE subjects with pending exams in the list of subjects that need proposals
            if status_lower in ['proposed', 'approved', 'rejected']:
                # This is likely a proposed exam for this subject
                subjects_with_proposals_by_this_group.add(exam.subjectId)
    
    logger.info(f"[DEBUG] Found subjects with proposals by group {group_id}: {subjects_with_proposals_by_this_group}")
    
    # Filter subjects that need proposals (those that don't already have exams proposed by this group)
    pending_subjects = [subject for subject in subjects if subject.id not in subjects_with_proposals_by_this_group]
    logger.info(f"[DEBUG] Filtered to {len(pending_subjects)} pending subjects that need proposals")
    
    # Add flag to clearly indicate these need proposals and ensure we have teacher data
    enhanced_subjects = []
    for subject in pending_subjects:
        # Add custom flag to indicate these need proposals
        subject_dict = subject.model_dump()
        subject_dict['needsProposal'] = True
        
        # Use the existing subject-teacher relationship to get teacher details
        # Get the full subject with teacher relationship loaded
        subject_with_teacher = await service.get_subject_with_teacher(subject.id)
        
        # Add teacher details if available
        if subject_with_teacher and subject_with_teacher.teacher:
            teacher = subject_with_teacher.teacher
            subject_dict['professorName'] = f"{teacher.firstName} {teacher.lastName}"
            subject_dict['professorEmail'] = teacher.email if hasattr(teacher, 'email') else ''
            logger.info(f"[DEBUG] Added teacher info for subject {subject.id}: {subject_dict['professorName']}")
        else:
            # Fallback if teacher not found
            subject_dict['professorName'] = "Profesor necunoscut"
            subject_dict['professorEmail'] = ""
            logger.warning(f"[DEBUG] No teacher found for subject {subject.id}, using fallback name")
            
            # Try to find teacher directly from the injected user service as a backup
            try:
                if hasattr(subject, 'teacherId') and subject.teacherId:
                    teacher = await user_service.get_user_by_id(subject.teacherId)
                    if teacher:
                        subject_dict['professorName'] = f"{teacher.firstName} {teacher.lastName}"
                        subject_dict['professorEmail'] = teacher.email if hasattr(teacher, 'email') else ''
                        logger.info(f"[DEBUG] Found teacher via backup method for subject {subject.id}: {subject_dict['professorName']}")
            except Exception as e:
                logger.error(f"[DEBUG] Error in backup teacher lookup: {str(e)}")
            
        # Add subject code from shortName if not present
        if 'code' not in subject_dict or not subject_dict['code']:
            subject_dict['code'] = subject.shortName
        
        enhanced_subject = SubjectResponse.model_validate(subject_dict)
        enhanced_subjects.append(enhanced_subject)
    
    # Debug what we're sending back
    logger.info(f"[DEBUG] Returning {len(enhanced_subjects)} pending subjects for group {group_id}")
    if enhanced_subjects:
        logger.info(f"[DEBUG] Sample subject: {enhanced_subjects[0].model_dump()}")
    
    return enhanced_subjects

@router.get("/teacher/{teacher_id}", response_model=List[SubjectResponse], summary="Get subjects by teacher", description="Retrieve all subjects for a specific teacher")
@inject
async def get_subjects_by_teacher(
    teacher_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get subjects for a specific teacher.
    
    Args:
        teacher_id (int): The ID of the teacher
        
    Returns:
        List[SubjectResponse]: A list of subjects for the specified teacher
    """
    return await service.get_subjects_by_teacher_id(teacher_id)

@router.get("/assistant/{assistant_id}", response_model=List[SubjectResponse], summary="Get subjects by assistant", description="Retrieve all subjects for a specific assistant")
@inject
async def get_subjects_by_assistant(
    assistant_id: int, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Get subjects for a specific assistant.
    
    Args:
        assistant_id (int): The ID of the assistant
        
    Returns:
        List[SubjectResponse]: A list of subjects for the specified assistant
    """
    return await service.get_subjects_by_assistant_id(assistant_id)

@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Create subject", description="Create a new subject in the system")
@inject
async def create_subject(
    subject_data: SubjectCreate, 
    service: ISubjectService = Depends(Provide[Container.subject_service])
):
    """Create a new subject.
    
    Args:
        subject_data (SubjectCreate): The subject data for creation
        
    Returns:
        SubjectResponse: The created subject details
        
    Raises:
        HTTPException: If validation fails for foreign keys
    """
    try:
        return await service.create_subject(subject_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{subject_id}", response_model=SubjectResponse, summary="Update subject", description="Update an existing subject's information")
@inject
async def update_subject(
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
        HTTPException: If the subject is not found or validation fails
    """
    try:
        subject = await service.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        updated_subject = await service.update_subject(subject_id, subject_data)
        return updated_subject
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete subject", description="Delete a subject from the system")
@inject
async def delete_subject(
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
