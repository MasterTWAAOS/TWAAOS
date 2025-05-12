from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.orm import Session

from services.abstract.auth_service_interface import IAuthService
from models.user import User
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from services.token_service import decode_access_token

class AuthService(IAuthService):
    """
    Implementation of authentication service
    """
    
    def __init__(self, user_repository: IUserRepository, group_repository: IGroupRepository, db: Session):
        """
        Initialize the auth service with a user repository, group repository and database session
        
        Args:
            user_repository: Repository for user operations
            group_repository: Repository for group operations
            db: SQLAlchemy database session
        """
        self.user_repository = user_repository
        self.group_repository = group_repository
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Optional[User]: The authenticated user if successful, None otherwise
        """
        user = self.user_repository.get_by_email(email)
        
        if not user or not user.passwordHash:
            return None
        
        if not self.verify_password(password, user.passwordHash):
            return None
        
        return user
    
    def get_or_create_google_user(self, google_id: str, email: str, first_name: str, last_name: str, role: Optional[str] = None, group_id: Optional[int] = None) -> Optional[User]:
        """
        Get or create a user with Google authentication data
        
        Args:
            google_id: Google ID from JWT token
            email: User's email address
            first_name: User's first name
            last_name: User's last name
            role: User's role (SG for student, CD for professor)
            group_id: Optional group ID for students
            
        Returns:
            Optional[User]: The user object if found or created, None otherwise
        """
        # Try to find user by google_id first
        user = self.user_repository.get_by_google_id(google_id)
        
        if user:
            return user
        
        # Try to find user by email
        user = self.user_repository.get_by_email(email)
        
        if user:
            # Update user with google_id if not already set
            if not user.googleId:
                user.googleId = google_id
                self.db.commit()
            return user
        
        # If we have a valid role from the controller (based on email domain validation),
        # we can create a new user automatically
        # Note: ADM (admin) users should only be created through traditional registration,
        # not through Google authentication for security reasons
        if role in ["SG", "CD", "SEC"]:
            # For student role, verify if the group exists before assigning
            assigned_group_id = None
            if role == "SG" and group_id is not None:
                # Use the repository to check if the group exists
                if self.group_repository.exists_by_id(group_id):
                    assigned_group_id = group_id
                else:
                    print(f"Group ID {group_id} does not exist in the database. Creating user without group assignment.")
            
            # Create a new user with the role provided from the controller
            new_user = User(
                firstName=first_name,
                lastName=last_name,
                email=email,
                googleId=google_id,
                role=role,
                groupId=assigned_group_id  # Only assign if we confirmed it exists
            )
            
            created_user = self.user_repository.create(new_user)
            return created_user
        
        # If email domain doesn't match any of our criteria, we don't create a user
        return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if the provided password matches the hashed password
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password from the database
            
        Returns:
            bool: True if the passwords match, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Generate a password hash
        
        Args:
            password: The plain text password
            
        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change a user's password
        
        Args:
            user_id: The user's ID
            new_password: The new plain text password
            
        Returns:
            bool: True if the password was changed successfully, False otherwise
        """
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return False
        
        hashed_password = self.get_password_hash(new_password)
        user.passwordHash = hashed_password
        
        self.db.commit()
        return True
    
    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token
        
        Args:
            token: The JWT token
            
        Returns:
            Optional[int]: The user ID if the token is valid, None otherwise
        """
        payload = decode_access_token(token)
        
        if not payload or "sub" not in payload:
            return None
        
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user's ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)
