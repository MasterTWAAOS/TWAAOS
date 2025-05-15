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
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
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
    user = await auth_service.authenticate_user(login_data.username, login_data.password)
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
    
    access_token_expires = timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = await create_access_token(
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
        # Use the service to verify the token and extract user info
        # This will raise an HTTPException if verification fails
        user_info = await auth_service.verify_google_token(request.token)
        
        # Extract user information from the response
        google_id = user_info['google_id']
        email = user_info['email']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
            
        # Get or create the user with the verified Google information
        user = await auth_service.get_google_user(
            google_id=google_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        access_token_expires = timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = await create_access_token(
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
             description="Change password for authenticated admin user")
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
