from passlib.context import CryptContext
from typing import Optional, Dict
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from services.abstract.auth_service_interface import IAuthService
from models.user import User
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from services.token_service import decode_access_token
from config.settings import get_settings

class AuthService(IAuthService):
    """
    Implementation of authentication service
    """
    
    def __init__(self, user_repository: IUserRepository, group_repository: IGroupRepository):
        """
        Initialize the auth service with a user repository and group repository
        
        Args:
            user_repository: Repository for user operations
            group_repository: Repository for group operations
        """
        self.user_repository = user_repository
        self.group_repository = group_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.settings = get_settings()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Optional[User]: The authenticated user if successful, None otherwise
        """
        user = await self.user_repository.get_by_email(email)
        
        if not user or not user.passwordHash:
            return None
        
        if not await self.verify_password(password, user.passwordHash):
            return None
        
        return user
    
    async def verify_google_token(self, token: str) -> Dict:
        """
        Verify a Google ID token and extract user information
        
        Args:
            token: The Google ID token to verify
            
        Returns:
            dict: User information extracted from the token
            
        Raises:
            HTTPException: If token verification fails
        """
        try:
            print(f"Attempting to verify Google token")
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.settings.GOOGLE_CLIENT_ID
            )
            
            # Extract user information from the verified token
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', '')
            }
            
            print(f"Successfully verified Google token for email: {user_info['email']}")
            return user_info
        except Exception as e:
            # Log the error for debugging
            print(f"Google token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
    
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
        print(f"Looking up user with email: {email} and google_id: {google_id}")
        
        # First priority: Try to find user by email (most reliable way to identify users)
        user = await self.user_repository.get_by_email(email)
        
        if user:
            print(f"Found existing user by email: {email}, id: {user.id}, role: {user.role}")
            # Update user with google_id if not already set or different
            if user.googleId != google_id:
                # Update user's Google ID in repository
                user.googleId = google_id
                
                # Also update first/last name if they were empty
                if not user.firstName and first_name:
                    user.firstName = first_name
                if not user.lastName and last_name:
                    user.lastName = last_name
                
                print(f"Updated user with Google ID: {google_id}")
                await self.user_repository.update(user)
            return user
        
        return None
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the provided password matches the hashed password
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password from the database
            
        Returns:
            bool: True if the passwords match, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def get_password_hash(self, password: str) -> str:
        """
        Generate a password hash
        
        Args:
            password: The plain text password
            
        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)
    
    async def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change a user's password
        
        Args:
            user_id: The user's ID
            new_password: The new plain text password
            
        Returns:
            bool: True if the password was changed successfully, False otherwise
        """
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            return False
        
        hashed_password = await self.get_password_hash(new_password)
        user.passwordHash = hashed_password
        
        await self.db.commit()
        return True
    
    async def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token
        
        Args:
            token: The JWT token
            
        Returns:
            Optional[int]: The user ID if the token is valid, None otherwise
        """
        payload = await decode_access_token(token)
        
        if not payload or "sub" not in payload:
            return None
        
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user's ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return await self.user_repository.get_by_id(user_id)
