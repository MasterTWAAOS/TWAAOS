from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from dependency_injector.wiring import inject, Provide
from typing import List, Dict, Any

from models.DTOs.exam_dto import ExamResponse, ExamUpdateRequest, ExamProposalRequest
from services.abstract.exam_service_interface import IExamService
from config.containers import Container

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.get("", response_model=List[ExamResponse], summary="Get all exams", description="Returns a list of all exams with detailed information")
@inject
async def get_all_exams(
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Get all exams with associated information.
    
    Returns:
        List[ExamResponse]: List of exams with subject, teacher and group details
    """
    print("[DEBUG] ExamController - get_all_exams: Request received")
    try:
        exams = await service.get_all_exams()
        print(f"[DEBUG] ExamController - Returning {len(exams)} exams")
        return exams
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exams: {str(e)}"
        )

@router.get("/program/{program_code}", response_model=List[ExamResponse], summary="Get exams by program", description="Returns exams for a specific study program")
@inject
async def get_exams_by_program(
    program_code: str,
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Get exams filtered by study program
    
    Args:
        program_code (str): Short name of the study program
        
    Returns:
        List[ExamResponse]: Filtered list of exams
    """
    print(f"[DEBUG] ExamController - get_exams_by_program: {program_code}")
    try:
        exams = await service.get_exams_by_study_program(program_code)
        print(f"[DEBUG] ExamController - Returning {len(exams)} exams for program {program_code}")
        return exams
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exams: {str(e)}"
        )

@router.get("/teacher/{teacher_id}", response_model=List[ExamResponse], summary="Get exams by teacher", description="Returns exams assigned to a specific teacher")
@inject
async def get_exams_by_teacher(
    teacher_id: int,
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Get exams assigned to a specific teacher
    
    Args:
        teacher_id (int): ID of the teacher
        
    Returns:
        List[ExamResponse]: List of exams for the teacher
    """
    print(f"[DEBUG] ExamController - get_exams_by_teacher: {teacher_id}")
    try:
        exams = await service.get_exams_by_teacher_id(teacher_id)
        print(f"[DEBUG] ExamController - Returning {len(exams)} exams for teacher {teacher_id}")
        return exams
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exams: {str(e)}"
        )

@router.get("/group/{group_id}", response_model=List[ExamResponse], summary="Get exams by group", description="Returns exams for a specific group")
@inject
async def get_exams_by_group(
    group_id: int,
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Get exams for a specific group
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        List[ExamResponse]: List of exams for the group
    """
    print(f"[DEBUG] ExamController - get_exams_by_group: {group_id}")
    try:
        exams = await service.get_exams_by_group_id(group_id)
        print(f"[DEBUG] ExamController - Returning {len(exams)} exams for group {group_id}")
        return exams
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exams: {str(e)}"
        )
        
@router.put("/{exam_id}", response_model=ExamResponse, summary="Update exam details", description="Update exam details such as date, time, room, professor, etc.")
@inject
async def update_exam(
    exam_id: int = Path(..., description="The ID of the exam to update"),
    exam_data: ExamUpdateRequest = Body(..., description="Updated exam details"),
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Update exam details.
    
    This endpoint allows Secretariat (SEC) users to modify exam details such as date, time,
    room, professor, status and notes.
    
    Args:
        exam_id (int): The ID of the exam to update
        exam_data (ExamUpdateRequest): Updated exam information
        
    Returns:
        ExamResponse: The updated exam information
        
    Raises:
        HTTPException: If the exam is not found or there's an error updating it
    """
    print(f"[DEBUG] ExamController - update_exam: {exam_id}")
    
    try:
        # Convert Pydantic model to dict for service layer
        update_data = exam_data.dict(exclude_unset=True)
        updated_exam = await service.update_exam(exam_id, update_data)
        
        print(f"[DEBUG] ExamController - Successfully updated exam {exam_id}")
        return updated_exam
        
    except ValueError as e:
        print(f"[DEBUG] ExamController - Value error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating exam: {str(e)}"
        )

@router.post("/propose", response_model=ExamResponse, status_code=status.HTTP_201_CREATED, summary="Propose exam date", description="Student Group Leaders (SG) propose exam dates for their group")
@inject
async def propose_exam_date(
    proposal: ExamProposalRequest = Body(..., description="Exam proposal details"),
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Propose a new exam date for a subject.
    
    This endpoint allows Student Group Leaders (SG) to propose exam dates for their group.
    The proposal is initially created with 'pending' status and awaits teacher approval.
    
    Args:
        proposal (ExamProposalRequest): The exam proposal data
        
    Returns:
        ExamResponse: The created exam proposal with details
        
    Raises:
        HTTPException: If there's an error processing the proposal
    """
    print(f"[DEBUG] ExamController - propose_exam_date for subject {proposal.subjectId} and group {proposal.groupId}")
    
    try:
        # Convert the proposal to a dict and set correct proposal status
        proposal_dict = proposal.dict()
        proposal_dict["status"] = "proposed"
        
        # Create the exam proposal
        exam = await service.create_exam_proposal(proposal_dict)
        
        print(f"[DEBUG] ExamController - Successfully created exam proposal for subject {proposal.subjectId}")
        return exam
        
    except ValueError as e:
        print(f"[DEBUG] ExamController - Value error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating exam proposal: {str(e)}"
        )
