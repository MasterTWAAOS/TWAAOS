from dependency_injector import containers, providers
from sqlalchemy.orm import Session

# Repository imports
from repositories.user_repository import UserRepository
from repositories.group_repository import GroupRepository
from repositories.subject_repository import SubjectRepository
from repositories.room_repository import RoomRepository
from repositories.schedule_repository import ScheduleRepository
from repositories.notification_repository import NotificationRepository
from repositories.excel_template_repository import ExcelTemplateRepository

# Repository interface imports
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from repositories.abstract.subject_repository_interface import ISubjectRepository
from repositories.abstract.room_repository_interface import IRoomRepository
from repositories.abstract.schedule_repository_interface import IScheduleRepository
from repositories.abstract.notification_repository_interface import INotificationRepository
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository

# Service imports
from services.user_service import UserService
from services.group_service import GroupService
from services.subject_service import SubjectService
from services.room_service import RoomService
from services.schedule_service import ScheduleService
from services.notification_service import NotificationService
from services.excel_template_service import ExcelTemplateService

# Service interface imports
from services.abstract.user_service_interface import IUserService
from services.abstract.group_service_interface import IGroupService
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.room_service_interface import IRoomService
from services.abstract.schedule_service_interface import IScheduleService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.excel_template_service_interface import IExcelTemplateService

from config.database_provider import get_db_session


class Container(containers.DeclarativeContainer):
    """Application container for dependency injection."""
    
    # Configuration
    wiring_config = containers.WiringConfiguration(
        packages=["controllers"]
    )
    
    # Database
    db = providers.Factory(
        get_db_session
    )
    
    # Repositories
    user_repository = providers.Singleton(
        UserRepository,
        db=db
    )
    
    group_repository = providers.Singleton(
        GroupRepository,
        db=db
    )
    
    subject_repository = providers.Singleton(
        SubjectRepository,
        db=db
    )
    
    room_repository = providers.Singleton(
        RoomRepository,
        db=db
    )
    
    schedule_repository = providers.Singleton(
        ScheduleRepository,
        db=db
    )
    
    notification_repository = providers.Singleton(
        NotificationRepository,
        db=db
    )
    
    excel_template_repository = providers.Singleton(
        ExcelTemplateRepository,
        db=db
    )
    
    # Services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        group_repository=group_repository
    )
    
    group_service = providers.Factory(
        GroupService,
        group_repository=group_repository
    )
    
    subject_service = providers.Factory(
        SubjectService,
        subject_repository=subject_repository
    )
    
    room_service = providers.Factory(
        RoomService,
        room_repository=room_repository
    )
    
    schedule_service = providers.Factory(
        ScheduleService,
        schedule_repository=schedule_repository
    )
    
    notification_service = providers.Factory(
        NotificationService,
        notification_repository=notification_repository
    )
    
    excel_template_service = providers.Factory(
        ExcelTemplateService,
        template_repository=excel_template_repository
    )
