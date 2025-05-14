from typing import List, Optional, Tuple
import logging

from models.subject import Subject
from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse
from repositories.abstract.subject_repository_interface import ISubjectRepository
from repositories.abstract.group_repository_interface import IGroupRepository
from repositories.abstract.user_repository_interface import IUserRepository
from services.abstract.subject_service_interface import ISubjectService

logger = logging.getLogger(__name__)

class SubjectService(ISubjectService):
    def __init__(self, subject_repository: ISubjectRepository, 
                 group_repository: IGroupRepository,
                 user_repository: IUserRepository):
        self.subject_repository = subject_repository
        self.group_repository = group_repository
        self.user_repository = user_repository

    async def get_all_subjects(self) -> List[SubjectResponse]:
        subjects = await self.subject_repository.get_all()
        return [SubjectResponse.model_validate(subject) for subject in subjects]

    async def get_subject_by_id(self, subject_id: int) -> Optional[SubjectResponse]:
        subject = await self.subject_repository.get_by_id(subject_id)
        if subject:
            return SubjectResponse.model_validate(subject)
        return None
    
    async def get_subjects_by_group_id(self, group_id: int) -> List[SubjectResponse]:
        subjects = await self.subject_repository.get_by_group_id(group_id)
        return [SubjectResponse.model_validate(subject) for subject in subjects]
    
    async def get_subjects_by_teacher_id(self, teacher_id: int) -> List[SubjectResponse]:
        subjects = await self.subject_repository.get_by_teacher_id(teacher_id)
        return [SubjectResponse.model_validate(subject) for subject in subjects]
        
    async def get_subjects_by_assistant_id(self, assistant_id: int) -> List[SubjectResponse]:
        subjects = await self.subject_repository.get_by_assistant_id(assistant_id)
        return [SubjectResponse.model_validate(subject) for subject in subjects]
        
    async def validate_group_id(self, group_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the group_id exists.
        
        Args:
            group_id: The group ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if group exists
        if not await self.group_repository.exists_by_id(group_id):
            return False, f"Group with ID {group_id} does not exist"
        
        # All checks passed
        return True, None
        
    async def validate_teacher_id(self, teacher_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the teacher_id exists and belongs to a user with role 'CD'.
        
        Args:
            teacher_id: The teacher ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if teacher exists
        teacher = await self.user_repository.get_by_id(teacher_id)
        if not teacher:
            return False, f"User with ID {teacher_id} does not exist"
            
        # Check if user is a teacher (CD role)
        if teacher.role != 'CD':
            return False, f"User with ID {teacher_id} is not a teacher (role 'CD')"
        
        # All checks passed
        return True, None
        
    async def validate_assistant_id(self, assistant_id: int) -> Tuple[bool, Optional[str]]:
        """Validates if the assistant_id exists and belongs to a user with role 'CD'.
        
        Args:
            assistant_id: The assistant ID to validate
            
        Returns:
            Tuple containing (is_valid, error_message)
            is_valid: True if validation passes, False otherwise
            error_message: Description of the error if validation fails, None otherwise
        """
        # Check if assistant exists
        assistant = await self.user_repository.get_by_id(assistant_id)
        if not assistant:
            return False, f"User with ID {assistant_id} does not exist"
            
        # Check if user is a teacher/assistant (CD role)
        if assistant.role != 'CD':
            return False, f"User with ID {assistant_id} is not a valid assistant (requires role 'CD')"
        
        # All checks passed
        return True, None
        
    async def validate_assistant_ids(self, assistant_ids: List[int]) -> Tuple[bool, Optional[str]]:
        """Validate that all assistant users exist and have role CD (professor).
        
        Args:
            assistant_ids: List of user IDs to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not assistant_ids:
            return True, None  # Empty list is valid
            
        for assistant_id in assistant_ids:
            assistant = await self.user_repository.get_by_id(assistant_id)
            
            if not assistant:
                return False, f"Assistant user with ID {assistant_id} does not exist"
                
            if assistant.role != "CD":
                return False, f"Assistant with ID {assistant_id} must have role CD (professor), but has {assistant.role}"
                
        # All checks passed
        return True, None

    async def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        # Validate groupId
        is_valid, error_message = await self.validate_group_id(subject_data.groupId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Validate teacherId
        is_valid, error_message = await self.validate_teacher_id(subject_data.teacherId)
        if not is_valid:
            raise ValueError(error_message)
            
        # Validate assistantIds list
        is_valid, error_message = await self.validate_assistant_ids(subject_data.assistantIds)
        if not is_valid:
            raise ValueError(error_message)
        
        # Create new subject object with direct assistantIds
        subject = Subject(
            name=subject_data.name,
            shortName=subject_data.shortName,
            groupId=subject_data.groupId,
            teacherId=subject_data.teacherId,
            assistantIds=subject_data.assistantIds or []
        )
        
        # Save to database
        created_subject = await self.subject_repository.create(subject)
        
        # No need to update assistants separately - they're stored directly now
        
        return SubjectResponse.model_validate(created_subject)

    async def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[SubjectResponse]:
        subject = await self.subject_repository.get_by_id(subject_id)
        if not subject:
            return None
            
        # Validate groupId if provided
        if subject_data.groupId is not None:
            is_valid, error_message = await self.validate_group_id(subject_data.groupId)
            if not is_valid:
                raise ValueError(error_message)
                
        # Validate teacherId if provided
        if subject_data.teacherId is not None:
            is_valid, error_message = await self.validate_teacher_id(subject_data.teacherId)
            if not is_valid:
                raise ValueError(error_message)
                
        # Validate assistantIds if provided
        if subject_data.assistantIds is not None:
            is_valid, error_message = await self.validate_assistant_ids(subject_data.assistantIds)
            if not is_valid:
                raise ValueError(error_message)
            
        # Update subject fields if provided
        if subject_data.name is not None:
            subject.name = subject_data.name
        if subject_data.shortName is not None:
            subject.shortName = subject_data.shortName
        if subject_data.groupId is not None:
            subject.groupId = subject_data.groupId
        if subject_data.teacherId is not None:
            subject.teacherId = subject_data.teacherId
        
        # Set assistantIds directly if provided
        if subject_data.assistantIds is not None:
            subject.assistantIds = subject_data.assistantIds
            
        # Save changes
        updated_subject = await self.subject_repository.update(subject)
        return SubjectResponse.model_validate(updated_subject)

    async def delete_subject(self, subject_id: int) -> bool:
        return await self.subject_repository.delete(subject_id)
        
    async def delete_all_subjects(self) -> int:
        """Delete all subjects from the database.
        
        This method uses the repository's delete_all method which handles foreign key constraints
        and clears relationships before executing the deletion.
        
        Returns:
            int: Number of subjects deleted
        """
        logger.info("Deleting all subjects...")
        return await self.subject_repository.delete_all()
