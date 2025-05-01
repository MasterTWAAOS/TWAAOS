from abc import ABC, abstractmethod
from typing import List, Optional
from models.user import User
from models.DTOs.user_dto import UserCreate, UserUpdate, UserResponse

class IUserService(ABC):
    @abstractmethod
    def get_all_users(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def create_user(self, user_data: UserCreate) -> UserResponse:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        pass