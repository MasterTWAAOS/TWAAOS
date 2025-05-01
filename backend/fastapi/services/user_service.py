from typing import List, Optional
from passlib.context import CryptContext

from models.user import User
from models.DTOs.user_dto import UserCreate, UserUpdate, UserResponse
from repositories.abstract.user_repository_interface import IUserRepository
from services.abstract.user_service_interface import IUserService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def get_all_users(self) -> List[UserResponse]:
        users = self.user_repository.get_all()
        return [UserResponse.from_orm(user) for user in users]

    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        user = self.user_repository.get_by_id(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = self.user_repository.get_by_email(email)
        if user:
            return UserResponse.from_orm(user)
        return None

    def create_user(self, user_data: UserCreate) -> UserResponse:
        # Hash the password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create new user object
        user = User(
            firstName=user_data.firstName,
            lastName=user_data.lastName,
            email=user_data.email,
            role=user_data.role,
            passwordHash=hashed_password
        )
        
        # Save to database
        created_user = self.user_repository.create(user)
        return UserResponse.from_orm(created_user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
            
        # Update user fields if provided
        if user_data.firstName is not None:
            user.firstName = user_data.firstName
        if user_data.lastName is not None:
            user.lastName = user_data.lastName
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.password is not None:
            user.passwordHash = pwd_context.hash(user_data.password)
            
        # Save changes
        updated_user = self.user_repository.update(user)
        return UserResponse.from_orm(updated_user)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repository.delete(user_id)