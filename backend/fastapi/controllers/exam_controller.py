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

@router.get("/teacher/{teacher_id}/dashboard", summary="Get teacher dashboard data", description="Returns aggregated data for the teacher dashboard including upcoming exams, pending exams, and proposals")
@inject
async def get_teacher_dashboard_data(
    teacher_id: int,
    service: IExamService = Depends(Provide[Container.exam_service])
):
    """Get dashboard data for a teacher including exams by status and various stats.
    
    Args:
        teacher_id (int): ID of the teacher
        
    Returns:
        Dict: Dashboard data including:
            - scheduledExams: List of approved exams
            - pendingExams: List of pending exams (no proposal yet)
            - pendingProposals: List of exams with 'proposed' status
            - nextExam: The next upcoming exam if any
            - stats: Various statistics (total subjects, exams by status)
    """
    print(f"[DEBUG] ExamController - get_teacher_dashboard_data for teacher: {teacher_id}")
    try:
        # Get all exams for this teacher
        exams = await service.get_exams_by_teacher_id(teacher_id)
        print(f"[DEBUG] ExamController - Retrieved {len(exams)} exams for teacher {teacher_id}")
        
        # Categorize exams by status
        scheduled_exams = [exam for exam in exams if exam.status.lower() == 'approved']
        pending_exams = [exam for exam in exams if exam.status.lower() == 'pending']
        pending_proposals = [exam for exam in exams if exam.status.lower() == 'proposed']
        rejected_exams = [exam for exam in exams if exam.status.lower() == 'rejected']
        
        # Basic stats
        total_subjects = len({exam.subjectId for exam in exams})
        
        # Find next exam (first upcoming approved exam)
        from datetime import datetime
        today = datetime.now().date()
        
        upcoming_exams = []
        next_exam = None
        
        for exam in scheduled_exams:
            exam_date = datetime.fromisoformat(exam.date.replace('Z', '+00:00')) if isinstance(exam.date, str) else exam.date
            if exam_date.date() >= today:
                upcoming_exams.append(exam)
        
        # Sort by date
        upcoming_exams.sort(key=lambda x: x.date if isinstance(x.date, str) else x.date.isoformat())
        
        if upcoming_exams:
            next_exam = upcoming_exams[0]
        
        print(f"[DEBUG] ExamController - Returning dashboard data for teacher {teacher_id} with "
              f"{len(scheduled_exams)} scheduled exams, {len(pending_exams)} pending exams, "
              f"{len(pending_proposals)} pending proposals, and {len(rejected_exams)} rejected exams")
              
        # Return aggregated dashboard data
        return {
            "scheduledExams": scheduled_exams,
            "pendingExams": pending_exams,
            "pendingProposals": pending_proposals,
            "rejectedExams": rejected_exams,
            "nextExam": next_exam,
            "stats": {
                "totalSubjects": total_subjects,
                "scheduledExams": len(scheduled_exams),
                "pendingExams": len(pending_exams),
                "pendingProposals": len(pending_proposals),
                "rejectedExams": len(rejected_exams)
            }
        }
    except Exception as e:
        print(f"[DEBUG] ExamController - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
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
