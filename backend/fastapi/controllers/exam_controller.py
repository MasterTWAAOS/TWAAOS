from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from models.DTOs.exam_dto import ExamResponse
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
