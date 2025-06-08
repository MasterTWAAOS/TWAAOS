from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.user import User
from models.DTOs.user_dto import UserCreate, UserUpdate, UserResponse

class IUserService(ABC):
    @abstractmethod
    async def get_all_users(self) -> List[UserResponse]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        pass
        
    @abstractmethod
    async def validate_group_id(self, group_id: Optional[int], role: str) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        pass
        
    @abstractmethod
    async def delete_all_users(self) -> int:
        """Delete all users from the database.
        
        Returns:
            int: The number of users deleted
        """
        pass
        
    @abstractmethod
    async def search_users(self, first_name: Optional[str] = None, last_name: Optional[str] = None, role: Optional[str] = None) -> List[UserResponse]:
        """Search for users by name and role.
        
        Args:
            first_name (Optional[str]): First name to search for
            last_name (Optional[str]): Last name to search for
            role (Optional[str]): Role to filter by
            
        Returns:
            List[UserResponse]: List of matching users
        """
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get all users with a specific role.
        
        Args:
            role (str): The role to filter users by (e.g., 'SG', 'CD', 'SEC', 'ADM')
            
        Returns:
            List[UserResponse]: List of users with the specified role
        """
        pass