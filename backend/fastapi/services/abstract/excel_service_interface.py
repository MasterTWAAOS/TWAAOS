"""Abstract interface for Excel service."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class IExcelService(ABC):
    """Interface for Excel service."""
    
    @abstractmethod
    async def parse_group_leaders_excel(self, file_content: bytes) -> List[Dict[str, str]]:
        """Parse an Excel file containing group leaders information.
        
        Args:
            file_content (bytes): The content of the Excel file
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed data
        """
        pass
    
    @abstractmethod
    async def process_group_leaders(self, file_content: bytes) -> Dict[str, Any]:
        """Process an Excel file containing group leaders and create users.
        
        Args:
            file_content (bytes): The content of the Excel file
            
        Returns:
            Dict[str, Any]: The result of the processing
        """
        pass
