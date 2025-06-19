from typing import Dict, List, Optional, Tuple, Any
import httpx
import asyncio
import logging
import os
from passlib.context import CryptContext

from models.user import User
from models.DTOs.excel_template_dto import TemplateType
from services.abstract.sync_service_interface import ISyncService
from services.abstract.group_service_interface import IGroupService
from services.abstract.room_service_interface import IRoomService
from services.abstract.user_service_interface import IUserService
from services.abstract.subject_service_interface import ISubjectService
from services.abstract.schedule_service_interface import IScheduleService
from services.abstract.notification_service_interface import INotificationService
from services.abstract.excel_template_service_interface import IExcelTemplateService

logger = logging.getLogger(__name__)

class SyncService(ISyncService):
    """
    Service for handling synchronization operations between systems.
    """
    
    def __init__(
        self, 
        group_service: IGroupService,
        room_service: IRoomService,
        user_service: IUserService,
        subject_service: ISubjectService,
        schedule_service: IScheduleService,
        notification_service: INotificationService = None,
        excel_template_service: IExcelTemplateService = None
    ):
        self.group_service = group_service
        self.room_service = room_service
        self.user_service = user_service
        self.subject_service = subject_service
        self.schedule_service = schedule_service
        self.notification_service = notification_service
        self.excel_template_service = excel_template_service
        
    async def delete_all_data(self) -> Dict[str, int]:
        """
        Delete all data from the database in the correct order to avoid foreign key constraint violations.
        Order: schedules → subjects → notifications → users → rooms → groups
        
        Returns:
            Dict[str, int]: A dictionary with counts of deleted entities
        """
        deleted_counts = {
            "schedules": 0,
            "subjects": 0,
            "notifications": 0,
            "users": 0,
            "rooms": 0,
            "groups": 0
        }
        
        # First, delete schedules (they reference subjects)
        try:
            deleted_counts["schedules"] = await self.schedule_service.delete_all_schedules()
            logger.info(f"Step 1/5: Deleted {deleted_counts['schedules']} schedules before synchronization")
        except Exception as schedule_delete_error:
            logger.error(f"Error deleting schedules: {str(schedule_delete_error)}")
        
        # Second, delete subjects (they have foreign keys to users and groups)
        try:
            deleted_counts["subjects"] = await self.subject_service.delete_all_subjects()
            logger.info(f"Step 2/6: Deleted {deleted_counts['subjects']} subjects before synchronization")
        except Exception as subject_delete_error:
            logger.error(f"Error deleting subjects: {str(subject_delete_error)}")
        
        # Third, delete notifications (they have foreign keys to users)
        try:
            if self.notification_service:
                deleted_counts["notifications"] = await self.notification_service.delete_all_notifications()
                logger.info(f"Step 3/6: Deleted {deleted_counts['notifications']} notifications before synchronization")
            else:
                logger.warning("Notification service not available, skipping notification deletion")
        except Exception as notification_delete_error:
            logger.error(f"Error deleting notifications: {str(notification_delete_error)}")
            
        # Fourth, delete users
        try:
            deleted_counts["users"] = await self.user_service.delete_all_users()
            logger.info(f"Step 4/6: Deleted {deleted_counts['users']} users before synchronization")
        except Exception as user_delete_error:
            logger.error(f"Error deleting users: {str(user_delete_error)}")

        # Fifth, delete rooms
        try:
            deleted_counts["rooms"] = await self.room_service.delete_all_rooms()
            logger.info(f"Step 5/6: Deleted {deleted_counts['rooms']} rooms before synchronization")
        except Exception as room_delete_error:
            logger.error(f"Error deleting rooms: {str(room_delete_error)}")
        
        # Last, delete groups
        try:
            deleted_counts["groups"] = await self.group_service.delete_all_groups()
            logger.info(f"Step 6/6: Deleted {deleted_counts['groups']} groups before synchronization")
        except Exception as group_delete_error:
            logger.error(f"Error deleting groups: {str(group_delete_error)}")


            
        return deleted_counts
    
    async def fetch_data_from_flask(self) -> Dict[str, Any]:
        """
        Call the Flask backend to fetch and sync data from USV API.
        
        Returns:
            Dict[str, Any]: Synchronization result with counts of created entities
        """
        logger.info("Calling Flask backend to fetch and sync data from USV API...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://flask:5000/fetch-and-sync-data", timeout=300)
                response.raise_for_status()
            
            # Parse response from Flask
            result = response.json()
            logger.info(f"Flask sync completed successfully")
            
            return result
        except Exception as e:
            logger.error(f"Error calling Flask backend: {str(e)}")
            raise
    
    async def find_valid_group_id(self) -> Optional[int]:
        """
        Find a valid group ID for test users.
        
        Returns:
            Optional[int]: A valid group ID if found, otherwise None
        """
        try:
            # Get the first 5 groups (to have options in case some fail)
            all_groups = await self.group_service.get_all_groups()
            if all_groups and len(all_groups) > 0:
                # Check each group to see if it actually exists
                for group in all_groups[:5]:
                    group_exists = await self.group_service.exists_by_id(group.id)
                    if group_exists:
                        valid_group_id = group.id
                        logger.info(f"Found valid group ID {valid_group_id} for student test user")
                        return valid_group_id
                
                logger.warning("Could not verify any group existence despite getting group list")
            else:
                logger.warning("No groups found in database for test student user")
        except Exception as group_error:
            logger.error(f"Error finding valid group: {str(group_error)}")
        
        return None
    
    async def create_test_users(self, valid_group_id: Optional[int] = None) -> Tuple[List[Any], int]:
        """
        Create test users for all roles.
        
        Args:
            valid_group_id (Optional[int], optional): A valid group ID to assign to student users. 
                                                     Defaults to None.
        
        Returns:
            Tuple[List[Any], int]: A tuple containing a list of created users and the count of created users
        """
        
        # Define test users with appropriate roles
        test_users = [
            # Student user with valid group ID (if available)
            {
                "firstName": "Tudor", 
                "lastName": "Albu", 
                "email": "niculai.crainiciuc@student.usv.ro", 
                "role": "SG", 
                # Only include groupId if we found a valid one
                **({
                    "groupId": valid_group_id,
                    "googleId": "dev-tudor-albu"
                } if valid_group_id is not None else {
                    "googleId": "dev-tudor-albu"
                })
            },
            # Professor user - no group ID for non-student roles
            {
                "firstName": "Matei", 
                "lastName": "Neagu", 
                "email": "filaret.crainiciuc@student.usv.ro", 
                "role": "CD", 
                "department": "C", 
                "phone": "0723321123",
                "googleId": "dev-matei-neagu"
            },
            # Secretary user
            {
                "firstName": "Alina", 
                "lastName": "Berca", 
                "email": "c.filaret200@gmail.com", 
                "role": "SEC",
                "googleId": "dev-alina-berca"
            },
            # Admin user with password
            {
                "firstName": "Admin", 
                "lastName": "Admin", 
                "email": "admin@usv.ro", 
                "role": "ADM", 
                "passwordHash": "asddsa"
            }
        ]
        
        # Create each test user with a direct database approach to avoid transaction conflicts
        created_users = []
        for index, user_data in enumerate(test_users):
            try:
                # Use a completely independent execution for each user creation
                email = user_data.get("email", "")
                role = user_data.get("role", "")
                logger.info(f"Creating test user {index+1}/4: {email} (role: {role})")
                
                # Build parameters for User object
                user_params = {
                    "firstName": user_data.get("firstName", ""),
                    "lastName": user_data.get("lastName", ""),
                    "email": email,
                    "role": role,
                    "department": user_data.get("department", ""),
                    "phone": user_data.get("phone", ""),
                    "passwordHash": user_data.get("passwordHash", ""),
                    "googleId": user_data.get("googleId", ""),
                    "isActive": True
                }
                
                # Only add groupId for student (SG) users
                if role == "SG" and valid_group_id is not None:
                    user_params["groupId"] = valid_group_id
                    logger.info(f"Assigning student user {email} to group {valid_group_id}")
                
                # Create the user model object
                user = User(**user_params)
                
                # Check if user already exists
                existing_user_dto = await self.user_service.get_user_by_email(email)
                if existing_user_dto:
                    # User exists - use this instead of creating
                    logger.info(f"👌 Test user {email} already exists, using existing user")
                    created_users.append(existing_user_dto)
                    continue  # Skip to next user
                    
                # User doesn't exist, try to create it
                created_user = await self.user_service.create_user(user)
                created_users.append(created_user)
                logger.info(f"✅ Successfully created test user: {email}")
            except Exception as create_error:
                # If creation failed, log the error but continue with other users
                logger.error(f"❌ Failed to create test user {email}: {str(create_error)}")
            
            # Always add a delay between operations to avoid conflicts
            await asyncio.sleep(0.5)
        
        test_users_count = len(created_users)
        logger.info(f"Test user creation complete: {test_users_count}/4 users created successfully")
        
        return created_users, test_users_count
    
    async def update_subjects_for_test_users(self, test_users: List[Any]) -> Dict[str, Any]:
        """
        Updates subjects assigned to the SG test user's group to use the CD test user as teacher.
        
        Args:
            test_users (List[Any]): List of test user objects created during synchronization
            
        Returns:
            Dict[str, Any]: Results of the subject update operation
        """
        result = {
            "updated_subjects": 0,
            "success": False,
            "message": ""
        }
        
        try:
            # Find the SG and CD test users from the created users
            sg_user = None
            cd_user = None
            
            for user in test_users:
                if user.email == "niculai.crainiciuc@student.usv.ro" and user.role == "SG":
                    sg_user = user
                elif user.email == "filaret.crainiciuc@student.usv.ro" and user.role == "CD":
                    cd_user = user
            
            # If both users were found, update the subjects
            if sg_user and cd_user and sg_user.groupId:
                logger.info(f"Updating subjects for SG test user's group {sg_user.groupId} to use CD test user {cd_user.id} as teacher")
                updated_subjects = await self.subject_service.update_teacher_for_group_subjects(
                    group_id=sg_user.groupId,
                    teacher_id=cd_user.id
                )
                
                result["updated_subjects"] = updated_subjects
                result["success"] = True
                result["message"] = f"Successfully updated {updated_subjects} subjects to use test CD user as teacher"
                logger.info(result["message"])
            else:
                missing = []
                if not sg_user:
                    missing.append("SG test user")
                if not cd_user:
                    missing.append("CD test user")
                if sg_user and not sg_user.groupId:
                    missing.append("SG test user's group ID")
                
                result["message"] = f"Unable to update subjects: Missing {', '.join(missing)}"
                logger.warning(f"Could not update subjects for test users. {result['message']}")
        except Exception as e:
            result["message"] = f"Error updating subjects for test users: {str(e)}"
            result["error"] = str(e)
            logger.error(result["message"])
            
        return result
    
    async def sync_all_data(self) -> Dict[str, Any]:
        """
        Orchestrates the entire synchronization process:
        1. Delete all existing data
        2. Fetch new data from Flask backend
        3. Create test users
        
        Returns:
            Dict[str, Any]: Detailed results of the synchronization process
        """
        result = {
            "success": True,
            "deleted": {},
            "synced": {},
            "test_users": {
                "count": 0,
                "created": []
            },
            "schedules": {
                "created": 0,
                "errors": 0
            }
        }
        
        try:
            # Step 1: Delete all existing data IN ORDER (rooms, groups, users)
            deleted_counts = await self.delete_all_data()
            result["deleted"] = deleted_counts
            
            # Step 2: Call the Flask service to fetch and sync new data
            flask_result = await self.fetch_data_from_flask()
            
            # Extract summary counts from the response
            result["synced"] = {
                "groups": flask_result.get('groups', {}).get('count', 0),
                "rooms": flask_result.get('rooms', {}).get('count', 0),
                "users": flask_result.get('users', {}).get('count', 0),
            }
            
            # Step 3: Create test users after all real data is fetched and created
            try:
                # Find valid group ID for student user
                valid_group_id = await self.find_valid_group_id()
                
                # Create test users
                created_users, test_users_count = await self.create_test_users(valid_group_id)
                result["test_users"]["count"] = test_users_count
                result["test_users"]["created"] = [user.email for user in created_users]
                
                # Update total users count
                result["synced"]["users"] += test_users_count
                
                # NEW FEATURE: Update subjects for SG test user's group to use CD test user as teacher
                # Call the dedicated method for better code organization
                logger.info("Step 3.1: Updating subjects for test users")
                subject_update_result = await self.update_subjects_for_test_users(created_users)
                
                # Add the results to the sync response
                if "updated_subjects" in subject_update_result:
                    result["test_users"]["updated_subjects"] = subject_update_result["updated_subjects"]
                
                if "message" in subject_update_result:
                    if subject_update_result["success"]:
                        result["test_users"]["subject_update_message"] = subject_update_result["message"]
                    else:
                        result["test_users"]["subject_update_warning"] = subject_update_result["message"]
                        
                if "error" in subject_update_result:
                    result["test_users"]["subject_update_error"] = subject_update_result["error"]
                
            except Exception as test_user_error:
                # If test users creation fails, still return success for the main sync
                logger.warning(f"Main sync succeeded but test users creation failed: {str(test_user_error)}")
                result["test_users"]["error"] = str(test_user_error)
            
            # Step 4: Populate schedules table from subjects
            try:
                logger.info("Step 4: Populating schedules from subjects")
                
                # First delete any existing schedules
                deleted_count = await self.schedule_service.delete_all_schedules()
                logger.info(f"Deleted {deleted_count} existing schedules before populating")
                
                # Then populate with fresh data from subjects
                schedule_stats = await self.schedule_service.populate_schedules_from_subjects()
                
                # Update result with schedule stats
                result["schedules"]["created"] = schedule_stats.get("created", 0)
                result["schedules"]["errors"] = schedule_stats.get("errors", 0)
                
                # Add details if there were errors
                if schedule_stats.get("errors", 0) > 0:
                    result["schedules"]["error_details"] = schedule_stats.get("error_details", [])
                    
                logger.info(f"Successfully created {schedule_stats.get('created', 0)} schedules from subjects")
                
            except Exception as schedule_error:
                # If schedule creation fails, still return success for the main sync
                logger.warning(f"Main sync succeeded but schedule population failed: {str(schedule_error)}")
                result["schedules"]["error"] = str(schedule_error)
            
            # Step 5: Upload the template_SG.xlsx file for SG data
            try:
                if self.excel_template_service:
                    logger.info("Step 5: Uploading template_SG.xlsx for student group leaders")
                    
                    # Check if the file exists
                    template_path = os.path.join(os.getcwd(), "template_SG.xlsx")
                    if os.path.exists(template_path):
                        # Create a FastAPI compatible UploadFile object
                        from fastapi import UploadFile
                        import shutil
                        
                        class CustomUploadFile(UploadFile):
                            def __init__(self, file_path: str):
                                self.file_name = os.path.basename(file_path)
                                self._file = open(file_path, "rb")
                                self.file = self._file
                            
                            async def read(self):
                                return self._file.read()
                                
                            def seek(self, offset: int):
                                self._file.seek(offset)
                        
                        # Create file object
                        file = CustomUploadFile(template_path)
                        
                        # Upload template with required parameters
                        template = await self.excel_template_service.create_template(
                            name="template_SG",
                            file=file,
                            template_type=TemplateType.sg,
                            group_id=None,
                            description="Template pentru încărcarea datelor despre șefii de grupă"
                        )
                        
                        # Close the file
                        file._file.close()
                        
                        if template:
                            result["template_sg"] = {
                                "success": True,
                                "id": template.id,
                                "message": "Template SG uploaded successfully"
                            }
                            logger.info(f"✅ Successfully uploaded template_SG.xlsx with ID {template.id}")
                        else:
                            result["template_sg"] = {
                                "success": False,
                                "message": "Failed to upload template_SG.xlsx: No template returned from service"
                            }
                            logger.warning("❌ Failed to upload template_SG.xlsx: No template returned from service")
                    else:
                        result["template_sg"] = {
                            "success": False,
                            "message": f"Template file not found at {template_path}"
                        }
                        logger.warning(f"❌ Template file not found at {template_path}")
                else:
                    result["template_sg"] = {
                        "success": False,
                        "message": "Excel template service not available"
                    }
                    logger.warning("❌ Excel template service not available for template upload")
            except Exception as template_error:
                # If template upload fails, still return success for the main sync
                logger.warning(f"Main sync succeeded but template upload failed: {str(template_error)}")
                result["template_sg"] = {
                    "success": False,
                    "message": f"Error uploading template: {str(template_error)}"
                }
                
            return result
        except Exception as e:
            logger.error(f"Error in sync process: {str(e)}")
            raise
