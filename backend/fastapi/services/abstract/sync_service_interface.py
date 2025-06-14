from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ISyncService(ABC):
    """
    Interface for synchronization operations between systems.
    """
    
    @abstractmethod
    async def delete_all_data(self) -> Dict[str, int]:
        """
        Delete all data from the database in the correct order (rooms, groups, users)
        to avoid foreign key constraint violations.
        
        Returns:
            Dict[str, int]: A dictionary with counts of deleted entities
        """
        pass
    
    @abstractmethod
    async def fetch_data_from_flask(self) -> Dict[str, Any]:
        """
        Call the Flask backend to fetch and sync data from USV API.
        
        Returns:
            Dict[str, Any]: Synchronization result with counts of created entities
        """
        pass
    
    @abstractmethod
    async def find_valid_group_id(self) -> Optional[int]:
        """
        Find a valid group ID for test users.
        
        Returns:
            Optional[int]: A valid group ID if found, otherwise None
        """
        pass
    
    @abstractmethod
    async def create_test_users(self, valid_group_id: Optional[int] = None) -> Tuple[List[Any], int]:
        """
        Create test users for all roles.
        
        Args:
            valid_group_id (Optional[int], optional): A valid group ID to assign to student users.
                                                     Defaults to None.
        
        Returns:
            Tuple[List[Any], int]: A tuple containing a list of created users and the count of created users
        """
        pass
        
    @abstractmethod
    async def update_subjects_for_test_users(self, test_users: List[Any]) -> Dict[str, Any]:
        """
        Updates subjects assigned to the SG test user's group to use the CD test user as teacher.
        
        Args:
            test_users (List[Any]): List of test user objects created during synchronization
            
        Returns:
            Dict[str, Any]: Results of the subject update operation
        """
        pass
    
    @abstractmethod
    async def sync_all_data(self) -> Dict[str, Any]:
        """
        Orchestrates the entire synchronization process:
        1. Delete all existing data
        2. Fetch new data from Flask backend
        3. Create test users
        
        Returns:
            Dict[str, Any]: Detailed results of the synchronization process
        """
        pass
