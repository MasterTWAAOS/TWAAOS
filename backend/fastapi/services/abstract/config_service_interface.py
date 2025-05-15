from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from models.DTOs.config_dto import ConfigCreate, ConfigUpdate, ConfigResponse

class IConfigService(ABC):
    @abstractmethod
    async def get_current_config(self) -> Optional[ConfigResponse]:
        """Get the current/latest configuration"""
        pass
        
    @abstractmethod
    async def get_config_by_id(self, config_id: int) -> Optional[ConfigResponse]:
        """Get configuration by ID"""
        pass
        
    @abstractmethod
    async def get_all_configs(self) -> List[ConfigResponse]:
        """Get all configuration records"""
        pass

    @abstractmethod
    async def create_config(self, 
                          start_date: datetime,
                          end_date: datetime) -> ConfigResponse:
        """Create a new configuration"""
        pass
        
    @abstractmethod
    async def update_config(self, 
                          config_id: int,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Optional[ConfigResponse]:
        """Update an existing configuration"""
        pass

    @abstractmethod
    async def delete_config(self, config_id: int) -> bool:
        """Delete a configuration"""
        pass
