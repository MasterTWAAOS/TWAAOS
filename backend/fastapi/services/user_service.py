from typing import List, Optional, Tuple
from passlib.context import CryptContext

from models.user import User
from models.DTOs.user_dto import UserCreate, UserUpdate, UserResponse
from repositories.abstract.user_repository_interface import IUserRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from services.abstract.user_service_interface import IUserService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository, group_repository: IGroupRepository):
        self.user_repository = user_repository
        self.group_repository = group_repository

    async def get_all_users(self) -> List[UserResponse]:
        users = await self.user_repository.get_all()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_email(email)
        if user:
            return UserResponse.model_validate(user)
        return None
        
    async def validate_group_id(self, group_id: Optional[int], role: str) -> Tuple[bool, Optional[str]]:
        """Validates if the group_id is valid for the given role.
        
        Args:
            group_id: The group ID to validate or None
            role: The user role ('SG', 'CD', 'SEC', 'ADM')
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # For SG users, groupId is required and must exist
        if role == 'SG':
            if group_id is None:
                return False, "Group ID is required for students (SG)"
            
            # Check if group exists
            if not await self.group_repository.exists_by_id(group_id):
                return False, f"Group with ID {group_id} does not exist"
                
        # For non-SG users, groupId should be None
        elif group_id is not None:
            return False, f"Group ID should not be set for non-student roles (current role: {role})"
            
        # All checks passed
        return True, None

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Validate group ID based on role
        is_valid, error_message = await self.validate_group_id(user_data.groupId, user_data.role)
        if not is_valid:
            raise ValueError(error_message)
        
        # Create new user object with all fields from user_data
        # For non-SG roles, we explicitly set groupId to None
        user = User(
            firstName=user_data.firstName,
            lastName=user_data.lastName,
            email=user_data.email,
            role=user_data.role,
            groupId=user_data.groupId if user_data.role == 'SG' else None,
            department=user_data.department,
            phone=user_data.phone,
            googleId=user_data.googleId,
            isActive=user_data.isActive,
            passwordHash=user_data.passwordHash
        )
        
        # Hash the password if provided
        if user_data.passwordHash:
            user.passwordHash = pwd_context.hash(user_data.passwordHash)
        
        # Save to database
        created_user = await self.user_repository.create(user)
        return UserResponse.model_validate(created_user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        # If role is changing, we need to handle groupId appropriately
        role = user_data.role if user_data.role is not None else user.role
        group_id = user_data.groupId if user_data.groupId is not None else user.groupId
        
        # Validate the group_id if either role or groupId is changing
        if user_data.role is not None or user_data.groupId is not None:
            is_valid, error_message = await self.validate_group_id(group_id, role)
            if not is_valid:
                raise ValueError(error_message)
            
        # Update user fields if provided
        if user_data.firstName is not None:
            user.firstName = user_data.firstName
        if user_data.lastName is not None:
            user.lastName = user_data.lastName
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.role is not None:
            user.role = user_data.role
            # If changing to non-SG role, clear the groupId
            if user_data.role != 'SG':
                user.groupId = None
        if user_data.groupId is not None:
            # Only set groupId if role is SG
            if role == 'SG':
                user.groupId = user_data.groupId
        if user_data.department is not None:
            user.department = user_data.department
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.googleId is not None:
            user.googleId = user_data.googleId
        if user_data.isActive is not None:
            user.isActive = user_data.isActive
        if user_data.passwordHash is not None:
            user.passwordHash = pwd_context.hash(user_data.passwordHash)
            
        # Save changes
        updated_user = await self.user_repository.update(user)
        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repository.delete(user_id)
        
    async def delete_all_users(self) -> int:
        """Delete all users from the database.
        
        Returns:
            int: The number of users deleted
        """
        return await self.user_repository.delete_all()
        
    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get all users with a specific role.
        
        Args:
            role (str): The role to filter users by (e.g., 'SG', 'CD', 'SEC', 'ADM')
            
        Returns:
            List[UserResponse]: List of users with the specified role
        """
        users = await self.user_repository.get_by_role(role)
        return [UserResponse.model_validate(user) for user in users]
        
    async def get_professor_count(self) -> int:
        """Get the total count of users with CD role (professors).
        
        Returns:
            int: The total number of professors
        """
        professors = await self.user_repository.get_by_role('CD')
        return len(professors)
    
    async def search_users(self, first_name: Optional[str] = None, last_name: Optional[str] = None, role: Optional[str] = None) -> List[UserResponse]:
        """Search for users by name and role.
        
        Args:
            first_name (Optional[str]): First name to search for
            last_name (Optional[str]): Last name to search for
            role (Optional[str]): Role to filter by
            
        Returns:
            List[UserResponse]: List of matching users
        """
        # Start with basic filter criteria
        filter_criteria = {}
        
        # Add filters for non-None parameters
        if first_name is not None:
            filter_criteria["firstName"] = first_name
            
        if last_name is not None:
            filter_criteria["lastName"] = last_name
            
        if role is not None:
            filter_criteria["role"] = role
            
        # If no filters provided, return empty list to avoid returning all users unintentionally
        if not filter_criteria:
            return []
            
        # Get matching users
        users = await self.user_repository.find_by_filters(filter_criteria)
        return [UserResponse.model_validate(user) for user in users]