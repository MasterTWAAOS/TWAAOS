from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
import requests
import logging
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
def delete_all_groups(group_service: IGroupService = Depends(Provide[Container.group_service])):
    """
    Deletes all groups from the database.
    
    Args:
        group_service: The group service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = group_service.delete_all_groups()
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
def delete_all_rooms(room_service: IRoomService = Depends(Provide[Container.room_service])):
    """
    Deletes all rooms from the database.
    
    Args:
        room_service: The room service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = room_service.delete_all_rooms()
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
def delete_all_users(user_service: IUserService = Depends(Provide[Container.user_service])):
    """
    Deletes all users from the database.
    
    Args:
        user_service: The user service
        
    Returns:
        DeleteResponse: The deletion result
    """
    try:
        deleted_count = user_service.delete_all_users()
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
def sync_data(
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
        # First, delete all existing data
        deleted_users = user_service.delete_all_users()
        deleted_groups = group_service.delete_all_groups()
        deleted_rooms = room_service.delete_all_rooms()
        
        logger.info(f"Deleted {deleted_groups} groups, {deleted_rooms} rooms, and {deleted_users} users before synchronization")
        
        # Call the Flask service to fetch and sync new data
        response = requests.post("http://flask:5000/fetch-and-sync-data")
        response.raise_for_status()
        
        result = response.json()
        
        # Extract summary counts from the response
        groups_count = result.get('groups', {}).get('count', 0)
        rooms_count = result.get('rooms', {}).get('count', 0)
        users_count = result.get('users', {}).get('count', 0)
        
        # After syncing real data, add test users for development
        try:
            # Create a test group manually rather than calling create_test_users
            # This avoids dependency injection conflicts
            test_group = Group(
                name="Test FIESC Group",
                studyYear=3,
                specializationShortName="CALC",
                groupIds=[9999]  # Mock ID for the test group
            )
            created_group = group_service.create_group(test_group)
            group_id = created_group.id
            
            # Hash password for admin user
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("admin123")
            
            # Create test users directly using the service (same as in create_test_users)
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
            
            # Create each user
            created_users = []
            for user in test_users:
                try:
                    created_user = user_service.create_user(user)
                    created_users.append(created_user)
                except Exception as user_error:
                    logger.warning(f"Failed to create test user {user.email}: {str(user_error)}")
            
            # Add test users count
            test_users_count = len(created_users)
            users_count += test_users_count
            
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
def create_test_users(
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
        created_group = group_service.create_group(test_group)
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
            created_user = user_service.create_user(user)
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
