"""Service for processing Excel files."""
import pandas as pd
import io
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, status

from models.user import UserRole, User
from services.abstract.user_service_interface import IUserService
from services.abstract.group_service_interface import IGroupService
from services.abstract.excel_service_interface import IExcelService

# Create a logger for this module
logger = logging.getLogger(__name__)

class ExcelService(IExcelService):
    """Service for processing Excel files."""
    
    def __init__(self, user_service: IUserService, group_service: IGroupService):
        """Initialize the Excel service.
        
        Args:
            user_service: The service for user operations
            group_service: The service for group operations
        """
        self.user_service = user_service
        self.group_service = group_service
    
    async def parse_group_leaders_excel(self, file_content: bytes) -> List[Dict[str, str]]:
        """Parse an Excel file containing group leaders information.
        
        The Excel file should have columns for Nume, Prenume, Email, and Grupa.
        The first row is treated as headers and skipped during processing.
        
        Args:
            file_content (bytes): The content of the Excel file
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the parsed data
            
        Raises:
            HTTPException: If the file cannot be parsed or has invalid format
        """
        try:
            # Parse the Excel file using pandas
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            
            # Check required columns
            required_columns = ['Nume', 'Prenume', 'Email', 'Grupa']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            # Convert DataFrame to list of dictionaries
            group_leaders = []
            for _, row in df.iterrows():
                # Skip rows with empty values in important fields
                if pd.isna(row['Nume']) or pd.isna(row['Prenume']) or pd.isna(row['Email']) or pd.isna(row['Grupa']):
                    continue
                    
                leader = {
                    'lastName': str(row['Nume']).strip(),
                    'firstName': str(row['Prenume']).strip(),
                    'email': str(row['Email']).strip(),
                    'groupName': str(row['Grupa']).strip()
                }
                
                group_leaders.append(leader)
                
            return group_leaders
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not parse Excel file: {str(e)}"
                )
    
    async def process_group_leaders(self, file_content: bytes) -> Dict[str, Any]:
        """Process an Excel file containing group leaders and create users.
        
        Args:
            file_content (bytes): The content of the Excel file
            
        Returns:
            Dict[str, Any]: The result of the processing
        """
        try:
            # Parse the Excel file
            leaders = await self.parse_group_leaders_excel(file_content)
            
            # Prepare result object
            result = {
                "success": True,
                "message": "Group leaders processed successfully",
                "created_count": 0,
                "failed_count": 0,
                "errors": []
            }
            
            # Process each leader
            for leader in leaders:
                try:
                    # Fetch the group by name
                    group = await self.group_service.get_group_by_name(leader['groupName'])
                    
                    if not group:
                        # Group not found, add error and continue with next leader
                        error_message = f"Group '{leader['groupName']}' not found for {leader['firstName']} {leader['lastName']}"
                        result["errors"].append(error_message)
                        result["failed_count"] += 1
                        continue
                    
                    # Check if user already exists by email
                    existing_user = await self.user_service.get_user_by_email(leader['email'])
                    
                    if existing_user:
                        # User already exists, log and skip (don't count as error)
                        logger.info(f"User with email {leader['email']} already exists. Skipping.")
                        # Track skipped users separately
                        if "skipped_count" not in result:
                            result["skipped_count"] = 0
                        result["skipped_count"] += 1
                        continue
                    
                    # Create user object
                    user_data = {
                        "firstName": leader['firstName'],
                        "lastName": leader['lastName'],
                        "email": leader['email'],
                        "role": UserRole.SG.value,  # SG role for "Sef de Grupa"
                        "groupId": group.id,
                        "department": "",
                        "phone": "",
                        "passwordHash": "",
                        "googleId": "{}{}".format(leader['firstName'], leader['lastName']),
                        "isActive": True
                    }

                    user_dto = User(**user_data)

                    # Create user
                    await self.user_service.create_user(user_dto)
                    
                    # Increment success counter
                    result["created_count"] += 1
                    
                except Exception as e:
                    # Handle individual user creation errors
                    error_message = f"Failed to create user for {leader['firstName']} {leader['lastName']}: {str(e)}"
                    result["errors"].append(error_message)
                    result["failed_count"] += 1
                    logger.error(error_message)
            
            # Update success status based on results
            skipped_count = result.get("skipped_count", 0)
            
            if result["failed_count"] > 0 and result["created_count"] == 0 and skipped_count == 0:
                result["success"] = False
                result["message"] = "Failed to process any group leaders"
            elif result["created_count"] > 0 or skipped_count > 0:
                # Create a message that includes created and skipped counts
                message_parts = []
                if result["created_count"] > 0:
                    message_parts.append(f"Created {result['created_count']} group leaders")
                if skipped_count > 0:
                    message_parts.append(f"Skipped {skipped_count} already existing users")
                if result["failed_count"] > 0:
                    message_parts.append(f"Encountered {result['failed_count']} errors")
                
                result["message"] = ". ".join(message_parts)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing group leaders: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process group leaders: {str(e)}"
                )
