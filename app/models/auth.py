from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserSignInRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    email_verified: bool = False

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
    message: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserPreferences(BaseModel):
    theme: str = "light"  # light, dark
    language: str = "en"  # en, tr, etc.
    editor_settings: Dict[str, Any] = {}
    command_history_enabled: bool = True
    auto_save_enabled: bool = True

class UserSettingsRequest(BaseModel):
    preferences: UserPreferences

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetResponse(BaseModel):
    message: str

class PasswordUpdateRequest(BaseModel):
    token: str
    new_password: str

class EmailConfirmationRequest(BaseModel):
    token: str

class EmailConfirmationResponse(BaseModel):
    message: str
    user: UserResponse