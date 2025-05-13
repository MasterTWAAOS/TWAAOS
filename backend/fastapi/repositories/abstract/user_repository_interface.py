from abc import ABC, abstractmethod
from typing import List, Optional
from models.user import User

class IUserRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
        
    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass

    @abstractmethod
    async def delete_all(self) -> int:
        """Delete all users from the database.
        
        Returns:
            int: The number of users deleted
        """
        pass