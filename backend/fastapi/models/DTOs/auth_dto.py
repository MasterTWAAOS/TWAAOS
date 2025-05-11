from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class TokenResponse(BaseModel):
    """Response model for authentication token and user data."""
    token: str
    user: dict

class LoginRequest(BaseModel):
    """Request model for username/password login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=6, description="Password")

class GoogleLoginRequest(BaseModel):
    """Request model for Google login."""
    token: str = Field(..., description="Google ID token")

class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    currentPassword: str = Field(..., min_length=6, description="Current password")
    newPassword: str = Field(..., min_length=6, description="New password")
