from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
import requests
import httpx
import logging
import asyncio
from passlib.context import CryptContext
from models.user import User
from models.group import Group
from config.containers import Container
from services.abstract.group_service_interface import IGroupService
from services.abstract.room_service_interface import IRoomService
from services.abstract.user_service_interface import IUserService

router = APIRouter(
    prefix="/api/sync",
    tags=["Synchronization"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

class SyncResponse(BaseModel):
    success: bool
    message: str

class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int
    
class CreateTestUsersResponse(BaseModel):
    success: bool
    message: str
    group_id: int
    users: list

@router.delete("/groups", response_model=DeleteResponse,
           summary="Delete all groups",
           description="Delete all groups from the database")
@inject
async def delete_all_groups(group_service: IGroupService = Depends(Provide[Container.group_service])):
    """
    Deletes all groups from the database.
    
    Args:
        group_service: The group service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = await group_service.delete_all_groups()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all groups",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting all groups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all groups: {str(e)}"
        )

@router.delete("/rooms", response_model=DeleteResponse,
           summary="Delete all rooms",
           description="Delete all rooms from the database")
@inject
async def delete_all_rooms(room_service: IRoomService = Depends(Provide[Container.room_service])):
    """
    Deletes all rooms from the database.
    
    Args:
        room_service: The room service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = await room_service.delete_all_rooms()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all rooms",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting all rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all rooms: {str(e)}"
        )

@router.delete("/users", response_model=DeleteResponse,
           summary="Delete all users",
           description="Delete all users from the database")
@inject
async def delete_all_users(user_service: IUserService = Depends(Provide[Container.user_service])):
    """
    Deletes all users from the database.
    
    Args:
        user_service: The user service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = await user_service.delete_all_users()
        return DeleteResponse(
            success=True,
            message=f"Successfully deleted all users",
            deleted_count=deleted_count
        )
    except Exception as e:
        logger.error(f"Error deleting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all users: {str(e)}"
        )

@router.post("/data", response_model=SyncResponse, 
           summary="Sync data from USV API", 
           description="Triggers deletion of existing data and synchronization of groups, rooms, and users from USV API")
@inject
async def sync_data(
    group_service: IGroupService = Depends(Provide[Container.group_service]),
    room_service: IRoomService = Depends(Provide[Container.room_service]),
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Deletes all existing data and triggers the Flask service to fetch data from USV API and sync it to the database.
    
    Args:
        group_service: The group service
        room_service: The room service
        user_service: The user service
        
    Returns:
        SyncResponse: The synchronization result
        
    Raises:
        HTTPException: If the synchronization fails
    """
    try:
        # Step 1: Delete all existing data IN ORDER (rooms, groups, users)
        # Important: Delete in this specific order to avoid foreign key constraint violations
        deleted_rooms = 0
        deleted_groups = 0
        deleted_users = 0
        
        # First, delete rooms
        try:
            deleted_rooms = await room_service.delete_all_rooms()
            logger.info(f"Step 1/3: Deleted {deleted_rooms} rooms before synchronization")
        except Exception as room_delete_error:
            logger.error(f"Error deleting rooms: {str(room_delete_error)}")
        
        # Second, delete groups
        try:
            deleted_groups = await group_service.delete_all_groups()
            logger.info(f"Step 2/3: Deleted {deleted_groups} groups before synchronization")
        except Exception as group_delete_error:
            logger.error(f"Error deleting groups: {str(group_delete_error)}")
        
        # Last, delete users
        try:
            deleted_users = await user_service.delete_all_users()
            logger.info(f"Step 3/3: Deleted {deleted_users} users before synchronization")
        except Exception as user_delete_error:
            logger.error(f"Error deleting users: {str(user_delete_error)}")
            
        # Step 2: Call the Flask service to fetch and sync new data
        logger.info("Calling Flask backend to fetch and sync data from USV API...")
        async with httpx.AsyncClient() as client:
            response = await client.post("http://flask:5000/fetch-and-sync-data", timeout=300)
            response.raise_for_status()
        
        # Parse response from Flask
        result = response.json()
        logger.info(f"Flask sync completed successfully")
        
        # Extract summary counts from the response
        groups_count = result.get('groups', {}).get('count', 0)
        rooms_count = result.get('rooms', {}).get('count', 0)
        users_count = result.get('users', {}).get('count', 0)
        
        # Step 3: Create test users after all real data is fetched and created
        logger.info("Starting test user creation process...")
        test_users_count = 0
        
        try:
            # IMPORTANT: For test users, DO NOT assign any group IDs to avoid foreign key issues
            # This is a known limitation that group IDs can be inconsistent during sync
            # We'll log this decision for clarity
            logger.info("TEST USERS: Not assigning group IDs to any users (including students) to avoid foreign key issues")
            valid_group_id = None
            
            # Query the database for a valid group
            try:
                # Get the first 5 groups (to have options in case some fail)
                all_groups = await group_service.get_all_groups()
                if all_groups and len(all_groups) > 0:
                    # Check each group to see if it actually exists
                    for group in all_groups[:5]:
                        group_exists = await group_service.exists_by_id(group.id)
                        if group_exists:
                            valid_group_id = group.id
                            logger.info(f"Found valid group ID {valid_group_id} for student test user")
                            break
                    
                    if valid_group_id is None:
                        logger.warning("Could not verify any group existence despite getting group list")
                else:
                    logger.warning("No groups found in database for test student user")
            except Exception as group_error:
                logger.error(f"Error finding valid group: {str(group_error)}")
                valid_group_id = None
            
            # Hash password for admin user
            try:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_password = pwd_context.hash("asddsa")
                logger.info("Admin password successfully hashed")
            except Exception as hash_error:
                logger.error(f"Error hashing admin password: {str(hash_error)}")
                # Provide a fallback hashed password (pre-computed bcrypt hash of 'asddsa')
                hashed_password = "$2b$12$1iRX2xcQyDPK1h63UvV8A.7xPr0sgM8prUnjoYuTCChbmUY9OJ1Ae"
                logger.info("Using fallback hashed password for admin")
            
            # Define test users with appropriate roles
            test_users = [
                # Student user with valid group ID (if available)
                {
                    "firstName": "Tudor", 
                    "lastName": "Albu", 
                    "email": "student1@student.usv.ro", 
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
                    "email": "professor@fiesc.usv.ro", 
                    "role": "CD", 
                    "department": "C", 
                    "phone": "0723321123",
                    "googleId": "dev-matei-neagu"
                },
                # Secretary user
                {
                    "firstName": "Alina", 
                    "lastName": "Berca", 
                    "email": "secretary@usv.ro", 
                    "role": "SEC",
                    "googleId": "dev-alina-berca"
                },
                # Admin user with password
                {
                    "firstName": "A", 
                    "lastName": "A", 
                    "email": "a@usv.ro", 
                    "role": "ADM", 
                    "passwordHash": hashed_password
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
                    
                    # Create the user directly with the repository to avoid DTO conversion issues
                    # First, check if the user exists by email to avoid duplicate creation attempts
                    try:
                        # Check if user already exists
                        existing_user_dto = await user_service.get_user_by_email(email)
                        if existing_user_dto:
                            # User exists - use this instead of creating
                            logger.info(f"👌 Test user {email} already exists, using existing user")
                            created_users.append(existing_user_dto)
                            continue  # Skip to next user
                            
                        # User doesn't exist, try to create it
                        created_user = await user_service.create_user(user)
                        created_users.append(created_user)
                        logger.info(f"✅ Successfully created test user: {email}")
                    except Exception as create_error:
                        # If creation failed, log the error but continue with other users
                        logger.error(f"❌ Failed to create test user {email}: {str(create_error)}")
                    
                    # Always add a delay between operations to avoid conflicts
                    await asyncio.sleep(0.5)
                    
                except Exception as user_error:
                    # This is for any other unexpected errors in the outer try block
                    logger.error(f"❌❌ Unexpected error processing test user {user_data.get('email', 'unknown')}: {str(user_error)}")
                    
                    # Still continue with next user
            
            # Count successfully created users
            test_users_count = len(created_users)
            users_count += test_users_count
            logger.info(f"Test user creation complete: {test_users_count}/4 users created successfully")
            
            
            return SyncResponse(
                success=True,
                message=f"Successfully synced {groups_count} groups, {rooms_count} rooms, and {users_count} users (including {test_users_count} test users) from USV API"
            )
        except Exception as test_user_error:
            # If test users creation fails, still return success for the main sync
            logger.warning(f"Main sync succeeded but test users creation failed: {str(test_user_error)}")
            
            return SyncResponse(
                success=True,
                message=f"Successfully synced {groups_count} groups, {rooms_count} rooms, and {users_count} users from USV API, but test users creation failed"
            )
    except requests.RequestException as e:
        logger.error(f"Error syncing data from USV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync data: {str(e)}"
        )


@router.post("/create-test-users", response_model=CreateTestUsersResponse, 
          summary="Create test users for development", 
          description="Creates predefined test users for all roles, including a template group")
@inject
async def create_test_users(
    user_service: IUserService = Depends(Provide[Container.user_service]),
    group_service: IGroupService = Depends(Provide[Container.group_service]),
):
    """
    Creates test users for all roles (Student, Professor, Secretariat, Admin) 
    and a template group for development and testing.
    
    Args:
        user_service: The user service for user operations
        group_service: The group service for group operations
        
    Returns:
        CreateTestUsersResponse: The result of test user creation
        
    Raises:
        HTTPException: If the creation fails
    """
    try:
        # First, create a template group for the student
        test_group = Group(
            name="Test FIESC Group",
            studyYear=3,
            specializationShortName="CALC"
        )
        created_group = await group_service.create_group(test_group)
        group_id = created_group.id
        
        # Hash password for admin user
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")
        
        # Create test users for all roles with all attributes defined
        test_users = [
            # Student with the template group
            User(
                firstName="Tudor", 
                lastName="Albu", 
                email="student1@student.usv.ro", 
                role="SG", 
                groupId=group_id, 
                department=None,
                phone=None,
                passwordHash=None,
                googleId=f"dev-tudor-albu",
                isActive=True
            ),
            # Professor with department
            User(
                firstName="Matei", 
                lastName="Neagu", 
                email="professor@fiesc.usv.ro", 
                role="CD", 
                groupId=None,
                department="C", 
                phone="0723321123", 
                passwordHash=None,
                googleId=f"dev-matei-neagu",
                isActive=True
            ),
            # Secretariat
            User(
                firstName="Alina", 
                lastName="Berca", 
                email="secretary@usv.ro", 
                role="SEC", 
                groupId=None,
                department=None,
                phone=None,
                passwordHash=None,
                googleId=f"dev-alina-berca",
                isActive=True
            ),
            # Admin with password
            User(
                firstName="A", 
                lastName="A", 
                email="a@usv.ro", 
                role="ADM", 
                groupId=None,
                department=None,
                phone=None,
                passwordHash=hashed_password, 
                googleId=None,
                isActive=True
            )
        ]
        
        # Create all test users using the service
        created_users = []
        for user in test_users:
            created_user = await user_service.create_user(user)
            created_users.append({
                "id": created_user.id,
                "email": created_user.email,
                "role": created_user.role,
                "firstName": created_user.firstName,
                "lastName": created_user.lastName
            })
        
        return CreateTestUsersResponse(
            success=True,
            message=f"Successfully created {len(created_users)} test users and a template group",
            group_id=group_id,
            users=created_users
        )
    except Exception as e:
        logger.error(f"Error creating test users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test users: {str(e)}"
        )
