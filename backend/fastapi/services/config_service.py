from typing import List, Optional
from datetime import datetime
import logging
from fastapi import HTTPException

from repositories.abstract.exam_repository_interface import IExamRepository

from models.config import Config
from models.DTOs.config_dto import ConfigResponse
from models.DTOs.notification_dto import NotificationCreate
from repositories.abstract.config_repository_interface import IConfigRepository
from services.abstract.config_service_interface import IConfigService
from services.abstract.email_service_interface import IEmailService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.user_service_interface import IUserService
from models.user import UserRole
from models.config import Config
from models.DTOs.config_dto import ConfigResponse
from models.DTOs.notification_dto import NotificationCreate

logger = logging.getLogger(__name__)

class ConfigService(IConfigService):
    def __init__(self, 
                 config_repository: IConfigRepository, 
                 email_service: Optional[IEmailService] = None,
                 notification_service: Optional[INotificationService] = None,
                 user_service: Optional[IUserService] = None,
                 exam_repository: Optional[IExamRepository] = None):
        self.config_repository = config_repository
        self.email_service = email_service
        self.notification_service = notification_service
        self.user_service = user_service
        self.exam_repository = exam_repository

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
        
        # Format dates for display in email
        start_date_formatted = start_date.strftime("%d-%m-%Y")
        end_date_formatted = end_date.strftime("%d-%m-%Y")
        
        # If exam repository is available, update SG exam statuses to pending
        if self.exam_repository:
            try:
                updated_count = await self.exam_repository.update_sg_exam_statuses_to_pending()
                logger.info(f"Updated {updated_count} SG user exams to 'pending' status")
            except Exception as e:
                logger.error(f"Failed to update SG exam statuses: {e}")
                # Don't fail the operation if exam status update fails
        
        # Send email notification to all SG users about the new exam period
        if self.email_service and self.notification_service and self.user_service:
            try:
                # Get all SG users to send notifications
                sg_users = await self.user_service.get_users_by_role(UserRole.SG)
                if not sg_users:
                    logger.warning("No SG users found to notify about exam period")
                else:
                    # Send email notifications
                    email_results = await self.email_service.notify_sg_users_about_new_exam_period(
                        start_date=start_date_formatted,
                        end_date=end_date_formatted
                    )
                    
                    # Log notifications in database for each successful email
                    for user in sg_users:
                        if user.email and email_results.get(user.email, False):
                            notification_data = NotificationCreate(
                                userId=user.id,
                                message=f"Perioada de examene a fost configurată: {start_date_formatted} - {end_date_formatted}",
                                status="trimis"
                            )
                            
                            await self.notification_service.create_notification(notification_data)
                    
                    logger.info(f"Sent and logged exam period notification emails for period {start_date_formatted} to {end_date_formatted}")
            except Exception as e:
                logger.error(f"Failed to send or log exam period notification emails: {e}")
                # Don't fail the operation if email/notification process fails
        else:
            logger.warning("Required services not available - no notifications sent for new exam period")
        
        # The repository now returns a dictionary with all necessary fields
        # So we can pass it directly to model_validate
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
        
        # If dates changed, send email notification to all SG users about the updated exam period
        if (start_date is not None or end_date is not None) and self.email_service and self.notification_service and self.user_service:
            try:
                # Format dates for display in email
                start_date_formatted = start.strftime("%d-%m-%Y")
                end_date_formatted = end.strftime("%d-%m-%Y")
                
                # Get all SG users to send notifications
                sg_users = await self.user_service.get_users_by_role(UserRole.SG)
                if not sg_users:
                    logger.warning("No SG users found to notify about updated exam period")
                else:
                    # Send email notifications
                    email_results = await self.email_service.notify_sg_users_about_new_exam_period(
                        start_date=start_date_formatted,
                        end_date=end_date_formatted
                    )
                    
                    # Log notifications in database for each successful email
                    for user in sg_users:
                        if user.email and email_results.get(user.email, False):
                            notification_data = NotificationCreate(
                                userId=user.id,
                                message=f"Perioada de examene a fost actualizată: {start_date_formatted} - {end_date_formatted}",
                                status="trimis"
                            )
                            
                            await self.notification_service.create_notification(notification_data)
                    
                    logger.info(f"Sent and logged update exam period notification emails for period {start_date_formatted} to {end_date_formatted}")
            except Exception as e:
                logger.error(f"Failed to send or log updated exam period notification emails: {e}")
                # Don't fail the operation if email/notification process fails
        
        # The repository now returns a dictionary with all necessary fields
        # So we can pass it directly to model_validate
        return ConfigResponse.model_validate(updated_config)

    async def delete_config(self, config_id: int) -> bool:
        """Delete a configuration"""
        return await self.config_repository.delete(config_id)
