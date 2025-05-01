from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository
from repositories.abstract.user_repository_interface import IUserRepository
from services.user_service import UserService
from services.abstract.user_service_interface import IUserService
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
    
    # Services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )
