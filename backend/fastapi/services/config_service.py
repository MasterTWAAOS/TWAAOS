from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

from models.config import Config
from models.DTOs.config_dto import ConfigResponse
from repositories.abstract.config_repository_interface import IConfigRepository
from services.abstract.config_service_interface import IConfigService

class ConfigService(IConfigService):
    def __init__(self, config_repository: IConfigRepository):
        self.config_repository = config_repository

    async def get_current_config(self) -> Optional[ConfigResponse]:
        """Get the current/latest configuration"""
        config = await self.config_repository.get_current_config()
        if config:
            return ConfigResponse.model_validate(config)
        return None
        
    async def get_config_by_id(self, config_id: int) -> Optional[ConfigResponse]:
        """Get configuration by ID"""
        config = await self.config_repository.get_by_id(config_id)
        if config:
            return ConfigResponse.model_validate(config)
        return None
        
    async def get_all_configs(self) -> List[ConfigResponse]:
        """Get all configuration records"""
        configs = await self.config_repository.get_all()
        return [ConfigResponse.model_validate(config) for config in configs]

    async def create_config(self, 
                          start_date: datetime,
                          end_date: datetime) -> ConfigResponse:
        """Create a new configuration"""
        # Validate date range
        if start_date >= end_date:
            raise HTTPException(
                status_code=400, 
                detail="End date must be after start date"
            )
            
        # Create the config
        created_config = await self.config_repository.create(
            start_date=start_date, 
            end_date=end_date
        )
        
        return ConfigResponse.model_validate(created_config)
        
    async def update_config(self, 
                          config_id: int,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Optional[ConfigResponse]:
        """Update an existing configuration"""
        # Check if config exists
        config = await self.config_repository.get_by_id(config_id)
        if not config:
            return None
            
        # Get the values to use for validation (either new or existing)
        start = start_date if start_date is not None else config.startDate
        end = end_date if end_date is not None else config.endDate
        
        # Validate date range
        if start >= end:
            raise HTTPException(
                status_code=400, 
                detail="End date must be after start date"
            )
            
        # Update the config
        updated_config = await self.config_repository.update(
            config_id=config_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return ConfigResponse.model_validate(updated_config)

    async def delete_config(self, config_id: int) -> bool:
        """Delete a configuration"""
        return await self.config_repository.delete(config_id)
