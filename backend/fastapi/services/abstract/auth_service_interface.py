from abc import ABC, abstractmethod
from typing import Optional
from models.user import User

class IAuthService(ABC):
    """
    Abstract interface for authentication-related services
    """
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Optional[User]: The authenticated user if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_google_user(self, google_id: str, email: str, first_name: str, last_name: str) -> Optional[User]:
        """
        Get or create a user with Google authentication data
        
        Args:
            google_id: Google ID from JWT token
            email: User's email address
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Optional[User]: The user object if found or created, None otherwise
        """
        pass
        
    @abstractmethod
    async def verify_google_token(self, token: str) -> dict:
        """
        Verify a Google ID token and extract user information
        
        Args:
            token: The Google ID token to verify
            
        Returns:
            dict: User information extracted from the token
            
        Raises:
            HTTPException: If token verification fails
        """
        pass
    
    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the provided password matches the hashed password
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password from the database
            
        Returns:
            bool: True if the passwords match, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        """
        Generate a password hash
        
        Args:
            password: The plain text password
            
        Returns:
            str: The hashed password
        """
        pass
    
    @abstractmethod
    async def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change a user's password
        
        Args:
            user_id: The user's ID
            new_password: The new plain text password
            
        Returns:
            bool: True if the password was changed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token
        
        Args:
            token: The JWT token
            
        Returns:
            Optional[int]: The user ID if the token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user's ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        pass
