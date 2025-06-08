from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Path, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
import io
import pandas as pd
from datetime import datetime

from models.DTOs.excel_template_dto import ExcelTemplateResponse, TemplateType
from services.abstract.excel_template_service_interface import IExcelTemplateService
from config.containers import Container

router = APIRouter(prefix="/excel-templates", tags=["excel-templates"])

@router.get("", response_model=List[ExcelTemplateResponse], summary="Get all excel templates", description="Retrieve a list of all excel templates in the system")
@inject
async def get_all_templates(
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Get all excel templates endpoint.
    
    Returns:
        List[ExcelTemplateResponse]: A list of all excel templates
    """
    return await service.get_all_templates()

@router.get("/{template_id}", response_model=ExcelTemplateResponse, summary="Get excel template by ID", description="Retrieve a specific excel template by its ID")
@inject
async def get_template(
    template_id: int, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Get a specific excel template by ID.
    
    Args:
        template_id (int): The ID of the excel template to retrieve
        
    Returns:
        ExcelTemplateResponse: The excel template details
        
    Raises:
        HTTPException: If the excel template is not found
    """
    # First check if the template exists
    template = await service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excel template with ID {template_id} not found"
        )
    return template

@router.get("/name/{name}", response_model=ExcelTemplateResponse, summary="Get excel template by name", description="Retrieve a specific excel template by its name")
@inject
async def get_template_by_name(
    name: str, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Get a specific excel template by name.
    
    Args:
        name (str): The name of the excel template to retrieve
        
    Returns:
        ExcelTemplateResponse: The excel template details
        
    Raises:
        HTTPException: If the excel template is not found
    """
    template = await service.get_template_by_name(name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excel template with name '{name}' not found"
        )
    return template

@router.get("/group/{group_id}/type/{type}", response_model=ExcelTemplateResponse, summary="Get template by group and type", description="Retrieve a specific template by group ID and template type")
@inject
async def get_template_by_group_and_type(
    group_id: int = Path(..., description="The group ID"),
    type: TemplateType = Path(..., description="The template type (sali, cd, sg)"),
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Get a specific template by group ID and template type.
    
    Args:
        group_id (int): The group ID
        type (TemplateType): The template type
        
    Returns:
        ExcelTemplateResponse: The template details
        
    Raises:
        HTTPException: If the template is not found
    """
    # Check if the template exists
    template = await service.get_template_by_group_and_type(group_id, type)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template for group {group_id} with type '{type}' not found"
        )
    return template

@router.get("/type/{type}", response_model=List[ExcelTemplateResponse], summary="Get templates by type", description="Retrieve templates by type (sali, cd, sg)")
@inject
async def get_templates_by_type(
    type: TemplateType = Path(..., description="The template type (sali, cd, sg)"),
    name: Optional[str] = Query(None, description="Optional template name to filter by"),
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Get templates by type, optionally filtered by name.
    
    Args:
        type (TemplateType): The template type (sali, cd, sg)
        name (Optional[str]): Optional template name to filter by
        
    Returns:
        List[ExcelTemplateResponse]: List of templates matching the criteria
    """
    templates = await service.get_templates_by_type(type, name)
    return templates

@router.get("/download/{template_id}", summary="Download template file", description="Download the Excel file for a specific template")
@inject
async def download_template_file(
    template_id: int,
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Download the Excel file for a specific template.
    
    Args:
        template_id (int): The ID of the template to download
        
    Returns:
        StreamingResponse: The Excel file as a downloadable response
        
    Raises:
        HTTPException: If the template is not found or has no file
    """
    # First check if the template exists
    template = await service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    # Get the file content
    file_content = await service.get_file_by_id(template_id)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No file found for template with ID {template_id}"
        )
    
    # Create a streaming response with the file content
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={template.name.replace(' ', '_')}.xlsx"
        }
    )

@router.post("", response_model=ExcelTemplateResponse, status_code=status.HTTP_201_CREATED, summary="Create new template", description="Create a new Excel template with an uploaded file")
@inject
async def create_template(
    name: str = Form(..., description="Template name"),
    template_type: TemplateType = Form(..., description="Template type (sali, cd, sg)"),
    file: UploadFile = File(..., description="Excel file to upload"),
    group_id: Optional[str] = Form(None, description="Group ID (optional)"),
    description: Optional[str] = Form(None, description="Template description (optional)"),
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Create a new Excel template with an uploaded file.
    
    Args:
        name (str): Template name
        template_type (TemplateType): Template type
        file (UploadFile): Excel file to upload
        group_id (Optional[int]): Group ID (optional)
        description (Optional[str]): Template description (optional)
        
    Returns:
        ExcelTemplateResponse: The created template details
    """
    # Convert empty string to None for group_id, or convert to int if it has a value
    processed_group_id = None
    if group_id and group_id.strip():
        processed_group_id = int(group_id)
        
    return await service.create_template(name, file, template_type, processed_group_id, description)

@router.put("/{template_id}", response_model=ExcelTemplateResponse, summary="Update template", description="Update an existing Excel template")
@inject
async def update_template(
    template_id: int,
    name: Optional[str] = Form(None, description="Template name"),
    template_type: Optional[TemplateType] = Form(None, description="Template type (sali, cd, sg)"),
    file: Optional[UploadFile] = File(None, description="Excel file to upload"),
    group_id: Optional[str] = Form(None, description="Group ID"),
    description: Optional[str] = Form(None, description="Template description"),
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Update an existing Excel template.
    
    Args:
        template_id (int): The ID of the template to update
        name (Optional[str]): Template name
        template_type (Optional[TemplateType]): Template type
        file (Optional[UploadFile]): Excel file to upload
        group_id (Optional[int]): Group ID
        description (Optional[str]): Template description
        
    Returns:
        ExcelTemplateResponse: The updated template details
        
    Raises:
        HTTPException: If the template is not found
    """
    # Convert empty string to None for group_id, or convert to int if it has a value
    processed_group_id = None
    if group_id and group_id.strip():
        processed_group_id = int(group_id)
        
    # Update the template
    updated_template = await service.update_template(
        template_id=template_id,
        name=name,
        file=file,
        template_type=template_type,
        group_id=processed_group_id,
        description=description
    )
    
    if not updated_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
        
    return updated_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete template", description="Delete an existing template")
@inject
async def delete_template(
    template_id: int, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Delete a template.
    
    Args:
        template_id (int): The ID of the template to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the template is not found
    """
    # First check if the template exists
    template = await service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
        
    # Delete the template
    await service.delete_template(template_id)
    return None


@router.get("/exams/generate-excel", summary="Generate Excel with Exam Information", description="Generate an Excel file with exam information grouped by program, year, and group")
@inject
async def generate_exam_excel(
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Generate an Excel file with exam information grouped by program, year, and group.
    The Excel file is both saved to the database and returned as a downloadable response.
    
    Returns:
        StreamingResponse: The Excel file as a downloadable response
        
    Raises:
        HTTPException: If there's an error generating the Excel file
    """
    print("[DEBUG] Controller - generate_exam_excel: Request received")
    try:
        # Get exam data from database
        print("[DEBUG] Controller - Calling service.get_subject_teacher_data()")
        subjects = await service.get_subject_teacher_data()
        
        if not subjects:
            print("[DEBUG] Controller - No subjects returned from service")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No exam data available"
            )
        
        print(f"[DEBUG] Controller - Received {len(subjects)} items from service")
        print(f"[DEBUG] Controller - Sample columns: {list(subjects[0].keys()) if subjects else 'None'}")
        
        # Create a pandas DataFrame from the exam data
        print("[DEBUG] Controller - Creating pandas DataFrame")
        df = pd.DataFrame(subjects)
        print(f"[DEBUG] Controller - DataFrame shape: {df.shape}")
        
        # Group the data by program, year, and group
        # Note: We're using the structure from the database models
        print("[DEBUG] Controller - Sorting DataFrame by program, year, group")
        grouped_df = df.sort_values(by=['specializationShortName', 'studyYear', 'groupName'])
        
        # Create Excel file in memory
        print("[DEBUG] Controller - Creating Excel file in memory")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            grouped_df.to_excel(writer, sheet_name='Examene', index=False)
            
            # Auto-adjust columns width
            print("[DEBUG] Controller - Auto-adjusting column widths")
            worksheet = writer.sheets['Examene']
            for i, col in enumerate(grouped_df.columns):
                column_width = max(grouped_df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)
        
        # Get the Excel file as bytes from the BytesIO object
        output.seek(0)
        excel_bytes = output.getvalue()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lista_examene_{timestamp}.xlsx"
        print(f"[DEBUG] Controller - Generated filename: {filename}")
        
        # Save the Excel file to the database
        print("[DEBUG] Controller - Saving Excel file to database")
        from models.DTOs.excel_template_dto import TemplateType
        await service.create_template_from_bytes(
            name=filename,
            file_bytes=excel_bytes,
            template_type=TemplateType.EXAM,
            description="Generated exam list with teacher details"
        )
        print("[DEBUG] Controller - Excel file saved to database successfully")
        
        # Reset the BytesIO cursor position to beginning for streaming
        output.seek(0)
        
        # Return the Excel file as a streaming response
        print("[DEBUG] Controller - Returning StreamingResponse with Excel file")
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        print(f"[DEBUG] Controller - Error: {str(e)}")
        import traceback
        print(f"[DEBUG] Controller - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Excel file: {str(e)}"
        )
