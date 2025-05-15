from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from models.config import Config

class IConfigRepository(ABC):
    @abstractmethod
    async def get_current_config(self) -> Optional[Config]:
        """Get the latest configuration"""
        pass
        
    @abstractmethod
    async def get_by_id(self, config_id: int) -> Optional[Config]:
        """Get config by ID"""
        pass
        
    @abstractmethod
    async def get_all(self) -> List[Config]:
        """Get all configuration records"""
        pass

    @abstractmethod
    async def create(self, start_date: datetime, end_date: datetime) -> Config:
        """Create a new configuration"""
        pass
        
    @abstractmethod
    async def update(self, 
                   config_id: int,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> Config:
        """Update an existing configuration"""
        pass

    @abstractmethod
    async def delete(self, config_id: int) -> bool:
        """Delete a configuration"""
        pass
