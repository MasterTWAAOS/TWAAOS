from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
from datetime import datetime

from models.DTOs.config_dto import ConfigResponse, ConfigCreate
from services.abstract.config_service_interface import IConfigService
from config.containers import Container

router = APIRouter(prefix="/configs", tags=["configs"])

@router.get("/current", response_model=ConfigResponse, summary="Get current configuration", description="Retrieve the current active configuration")
@inject
async def get_current_config(
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Get the current active configuration.
    
    Returns:
        ConfigResponse: The current configuration details
        
    Raises:
        HTTPException: If no configuration exists
    """
    config = await service.get_current_config()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No configuration found in the system"
        )
    return config

@router.get("", response_model=List[ConfigResponse], summary="Get all configurations", description="Retrieve all configuration records")
@inject
async def get_all_configs(
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Get all configuration records.
    
    Returns:
        List[ConfigResponse]: A list of all configurations
    """
    return await service.get_all_configs()

@router.get("/{config_id}", response_model=ConfigResponse, summary="Get configuration by ID", description="Retrieve a specific configuration by its ID")
@inject
async def get_config_by_id(
    config_id: int,
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Get a specific configuration by ID.
    
    Args:
        config_id (int): The ID of the configuration to retrieve
        
    Returns:
        ConfigResponse: The configuration details
        
    Raises:
        HTTPException: If the configuration is not found
    """
    config = await service.get_config_by_id(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with ID {config_id} not found"
        )
    return config

@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED, summary="Create new configuration", description="Create a new system configuration")
@inject
async def create_config(
    start_date: datetime = Body(..., description="Start date of the academic period"),
    end_date: datetime = Body(..., description="End date of the academic period"),
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Create a new system configuration.
    
    Args:
        start_date (datetime): Start date of the academic period
        end_date (datetime): End date of the academic period
        
    Returns:
        ConfigResponse: The created configuration details
    """
    return await service.create_config(start_date, end_date)

@router.put("/{config_id}", response_model=ConfigResponse, summary="Update configuration", description="Update an existing system configuration")
@inject
async def update_config(
    config_id: int,
    start_date: Optional[datetime] = Body(None, description="Start date of the academic period"),
    end_date: Optional[datetime] = Body(None, description="End date of the academic period"),
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Update an existing system configuration.
    
    Args:
        config_id (int): The ID of the configuration to update
        start_date (Optional[datetime]): Updated start date
        end_date (Optional[datetime]): Updated end date
        
    Returns:
        ConfigResponse: The updated configuration details
        
    Raises:
        HTTPException: If the configuration is not found
    """
    updated_config = await service.update_config(
        config_id=config_id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not updated_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with ID {config_id} not found"
        )
        
    return updated_config

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete configuration", description="Delete an existing system configuration")
@inject
async def delete_config(
    config_id: int,
    service: IConfigService = Depends(Provide[Container.config_service])
):
    """Delete a system configuration.
    
    Args:
        config_id (int): The ID of the configuration to delete
        
    Returns:
        None: No content is returned
        
    Raises:
        HTTPException: If the configuration is not found
    """
    # First check if the config exists
    config = await service.get_config_by_id(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with ID {config_id} not found"
        )
        
    # Delete the config
    await service.delete_config(config_id)
    return None
