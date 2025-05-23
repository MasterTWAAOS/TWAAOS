from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Path, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
import io

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
