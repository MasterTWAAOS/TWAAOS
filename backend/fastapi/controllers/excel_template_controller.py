from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependency_injector.wiring import inject, Provide

from models.DTOs.excel_template_dto import ExcelTemplateCreate, ExcelTemplateUpdate, ExcelTemplateResponse
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

@router.post("", response_model=ExcelTemplateResponse, status_code=status.HTTP_201_CREATED, summary="Create new excel template", description="Create a new excel template in the system")
@inject
async def create_template(
    template_data: ExcelTemplateCreate, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Create a new excel template.
    
    Args:
        template_data (ExcelTemplateCreate): The excel template data for creation
        
    Returns:
        ExcelTemplateResponse: The created excel template details
    """
    return await service.create_template(template_data)

@router.put("/{template_id}", response_model=ExcelTemplateResponse, summary="Update excel template", description="Update an existing excel template's information")
@inject
async def update_template(
    template_id: int, 
    template_data: ExcelTemplateUpdate, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Update an existing excel template.
    
    Args:
        template_id (int): The ID of the excel template to update
        template_data (ExcelTemplateUpdate): The updated excel template data
        
    Returns:
        ExcelTemplateResponse: The updated excel template details
        
    Raises:
        HTTPException: If the excel template is not found
    """
    updated_template = await service.update_template(template_id, template_data)
    if not updated_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excel template with ID {template_id} not found"
        )
    return updated_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete excel template", description="Delete an excel template from the system")
@inject
async def delete_template(
    template_id: int, 
    service: IExcelTemplateService = Depends(Provide[Container.excel_template_service])
):
    """Delete an excel template.
    
    Args:
        template_id (int): The ID of the excel template to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the excel template is not found
    """
    success = await service.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excel template with ID {template_id} not found"
        )
    return None
