from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from models.config import Config
from repositories.abstract.config_repository_interface import IConfigRepository

class ConfigRepository(IConfigRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_config(self) -> Optional[Config]:
        """Get the latest configuration based on modified_at timestamp"""
        result = await self.db.execute(
            select(Config)
            .order_by(Config.modified_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
        
    async def get_by_id(self, config_id: int) -> Optional[Config]:
        """Get config by ID"""
        result = await self.db.execute(
            select(Config)
            .filter(Config.id == config_id)
        )
        return result.scalar_one_or_none()
        
    async def get_all(self) -> List[Config]:
        """Get all configuration records"""
        result = await self.db.execute(
            select(Config)
            .order_by(Config.modified_at.desc())
        )
        return result.scalars().all()

    async def create(self, start_date: datetime, end_date: datetime) -> Config:
        """Create a new configuration"""
        config = Config(
            startDate=start_date,
            endDate=end_date
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config
        
    async def update(self, 
                   config_id: int,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> Config:
        """Update an existing configuration"""
        config = await self.get_by_id(config_id)
        if not config:
            raise ValueError(f"Config with id {config_id} not found")
            
        # Update fields if provided
        if start_date is not None:
            config.startDate = start_date
        if end_date is not None:
            config.endDate = end_date
            
        # modified_at will be automatically updated by the database
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete(self, config_id: int) -> bool:
        """Delete a configuration"""
        config = await self.get_by_id(config_id)
        if config:
            await self.db.delete(config)
            await self.db.commit()
            return True
        return False
