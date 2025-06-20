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
from repositories.config_repository import ConfigRepository
from repositories.exam_repository import ExamRepository

# Repository interface imports
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from repositories.abstract.subject_repository_interface import ISubjectRepository
from repositories.abstract.room_repository_interface import IRoomRepository
from repositories.abstract.schedule_repository_interface import IScheduleRepository
from repositories.abstract.notification_repository_interface import INotificationRepository
from repositories.abstract.excel_template_repository_interface import IExcelTemplateRepository
from repositories.abstract.config_repository_interface import IConfigRepository
from repositories.abstract.exam_repository_interface import IExamRepository

# Service imports
from services.user_service import UserService
from services.group_service import GroupService
from services.subject_service import SubjectService
from services.room_service import RoomService
from services.schedule_service import ScheduleService
from services.notification_service import NotificationService
from services.excel_template_service import ExcelTemplateService
from services.auth_service import AuthService
from services.sync_service import SyncService
from services.config_service import ConfigService
from services.excel_service import ExcelService
from services.exam_service import ExamService
from services.email_service import EmailService

# Service interface imports
from services.abstract.user_service_interface import IUserService
from services.abstract.group_service_interface import IGroupService
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.room_service_interface import IRoomService
from services.abstract.schedule_service_interface import IScheduleService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.excel_template_service_interface import IExcelTemplateService
from services.abstract.auth_service_interface import IAuthService
from services.abstract.sync_service_interface import ISyncService
from services.abstract.config_service_interface import IConfigService
from services.abstract.excel_service_interface import IExcelService
from services.abstract.exam_service_interface import IExamService
from services.abstract.email_service_interface import IEmailService

from config.database_provider import get_db_session


class Container(containers.DeclarativeContainer):
    """Application container for dependency injection."""
    
    # Configuration
    wiring_config = containers.WiringConfiguration(
        packages=["controllers"]
    )
    
    # Database - use Resource to properly handle async generator
    db = providers.Resource(
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
    
    config_repository = providers.Singleton(
        ConfigRepository,
        db=db
    )

    exam_repository = providers.Singleton(
        ExamRepository,
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
        subject_repository=subject_repository,
        group_repository=group_repository,
        user_repository=user_repository
    )
    
    room_service = providers.Factory(
        RoomService,
        room_repository=room_repository
    )
    
    email_service = providers.Factory(
        EmailService,
        user_service=user_service
    )
    
    schedule_service = providers.Factory(
        ScheduleService,
        schedule_repository=schedule_repository,
        subject_repository=subject_repository,
        user_repository=user_repository,
        room_repository=room_repository,
        group_repository=group_repository,
        email_service=email_service
    )
    
    notification_service = providers.Factory(
        NotificationService,
        notification_repository=notification_repository,
        user_repository=user_repository
    )
    
    excel_template_service = providers.Factory(
        ExcelTemplateService,
        template_repository=excel_template_repository
    )
    
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        group_repository=group_repository
    )
    
    sync_service = providers.Factory(
        SyncService,
        group_service=group_service,
        room_service=room_service,
        user_service=user_service,
        subject_service=subject_service,
        schedule_service=schedule_service,
        notification_service=notification_service,
        excel_template_service=excel_template_service
    )
    
    config_service = providers.Factory(
        ConfigService,
        config_repository=config_repository,
        email_service=email_service,
        notification_service=notification_service,
        user_service=user_service,
        exam_repository=exam_repository
    )
    
    excel_service = providers.Factory(
        ExcelService,
        user_service=user_service,
        group_service=group_service
    )
    
    exam_service = providers.Factory(
        ExamService,
        exam_repository=exam_repository,
        schedule_service=schedule_service,
        email_service=email_service,
        notification_service=notification_service,
        user_service=user_service,
        subject_service=subject_service,
        config_service=config_service,
        room_service=room_service
    )
