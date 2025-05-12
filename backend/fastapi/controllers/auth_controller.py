from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from dependency_injector.wiring import inject, Provide
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import re
# For now, we'll use a mock verification for development

from models.DTOs.auth_dto import TokenResponse, GoogleLoginRequest, ChangePasswordRequest, LoginRequest
from services.abstract.auth_service_interface import IAuthService
from config.containers import Container
from services.token_service import create_access_token
from config.settings import get_settings

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
settings = get_settings()

@router.post("/login", response_model=TokenResponse, summary="Login with username and password", 
             description="Authenticate admin user with username (email) and password")
@inject
async def login(
    login_data: LoginRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """Login with username and password for admin users.
    
    Args:
        login_data (LoginRequest): The login credentials with username and password
        
    Returns:
        TokenResponse: JWT access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Only allow admin users to login with username/password
    if user.role != "ADM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can use password login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "role": user.role,
            "groupId": user.groupId
        },
        expires_delta=access_token_expires
    )
    
    # Return format matches the frontend's expected structure
    return {
        "token": access_token,  # Changed from access_token to token to match frontend
        "user": {
            "id": user.id,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "role": user.role,
            "groupId": user.groupId
        }
    }

@router.post("/google", response_model=TokenResponse, summary="Login with Google", 
             description="Authenticate user with Google ID token")
@inject
async def google_login(
    request: GoogleLoginRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """Login with Google token.
    
    Args:
        request (GoogleLoginRequest): The Google ID token
        
    Returns:
        TokenResponse: JWT access token and user information
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    try:
        # Check if we have a Google Client ID configured
        if settings.GOOGLE_CLIENT_ID:
            # Production mode - Verify the Google ID token
            try:
                idinfo = id_token.verify_oauth2_token(
                    request.token, 
                    google_requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
                
                # Extract user information from the verified token
                google_id = idinfo['sub']
                email = idinfo['email']
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
            except Exception as e:
                # Log the error for debugging
                print(f"Google token verification failed: {str(e)}")
                raise ValueError("Invalid token or client ID")
        else:
            # Development mode - Mock verification 
            print("DEVELOPMENT MODE: Using mock Google verification")
            
            # Check if we're using the special token format: email|role
            if '|' in request.token:
                # Parse the token as email|role format
                parts = request.token.split('|')
                email = parts[0]
                
                # Extract role and optional groupId if available
                if len(parts) >= 2:
                    role_code = parts[1]
                else:
                    role_code = None
                    
                # Extract groupId if available (format: email|role|groupId)
                group_id = None
                if len(parts) >= 3 and parts[2] != 'null':
                    try:
                        group_id = int(parts[2])
                    except ValueError:
                        # If not a valid integer, ignore
                        pass
                
                # Create a deterministic google_id from the email
                google_id = f"dev-{email.split('@')[0]}"
                first_name = "Test"
                last_name = email.split('@')[0].capitalize()
            else:
                # Fallback to legacy token handling
                google_id = f"dev-{request.token[:12]}"
                email = f"{request.token[:8]}@student.usv.ro"  
                first_name = "Dev"
                last_name = "User"
                role_code = None  # Will be determined from email domain later
        
        # In development mode with our special token format, we already have the role
        if not settings.GOOGLE_CLIENT_ID and '|' in request.token:
            # Use the role that was specified in the token
            user_role = role_code
            print(f"DEVELOPMENT MODE: Using role from token: {user_role}")
        else:
            # Production mode or fallback: Check if the email is from USV domains
            email_domain = email.split('@')[-1].lower()
            if email_domain not in settings.USV_EMAIL_DOMAINS:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only USV email addresses are allowed for authentication"
                )
            
            # Determine user role based on email domain
            user_role = None
            if email_domain == "student.usv.ro":
                user_role = "SG"  # Student
            elif email_domain in ["usv.ro", "staff.usv.ro", "fim.usv.ro", "fiesc.usv.ro"]:
                user_role = "CD"  # Professor
            
        # Get or create the user with the verified Google information
        user = auth_service.get_or_create_google_user(
            google_id=google_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=user_role,
            group_id=group_id
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found and could not be created"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "role": user.role,
                "groupId": user.groupId
            },
            expires_delta=access_token_expires
        )
        
        # Return format matches the frontend's expected structure
        return {
            "token": access_token,  # Changed from access_token to token to match frontend
            "user": {
                "id": user.id,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "role": user.role,
                "groupId": user.groupId
            }
        }
    
    except ValueError:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

@router.post("/change-password", response_model=dict, summary="Change password", 
             description="Change the password for the current admin user")
@inject
async def change_password(
    request: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """Change password for admin user.
    
    Args:
        request (ChangePasswordRequest): Current and new password
        token (str): JWT access token
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    # Get user from token
    user_id = auth_service.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Get user
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify role
    if user.role != "ADM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can change password"
        )
    
    # Verify current password
    if not auth_service.verify_password(request.currentPassword, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Change password
    auth_service.change_password(user_id, request.newPassword)
    
    return {"message": "Password changed successfully"}
