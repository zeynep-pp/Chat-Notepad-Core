from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from ..models.auth import (
    UserSignUpRequest,
    UserSignInRequest,
    AuthResponse,
    UserResponse,
    UserUpdateRequest,
    UserPreferences,
    UserSettingsRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordUpdateRequest,
    EmailConfirmationRequest,
    EmailConfirmationResponse
)
from ..services.auth_service import auth_service, AuthError
from ..middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
async def sign_up(request: UserSignUpRequest):
    """Register a new user"""
    logger.info(f"🔐 Signup request received for email: {request.email}")
    try:
        result = await auth_service.sign_up(request)
        logger.info(f"✅ Signup successful for email: {request.email}")
        return result
    except AuthError as e:
        logger.error(f"❌ Signup failed for email: {request.email} - Error: {e.message}")
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Signup failed for email: {request.email} - Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: UserSignInRequest):
    """Sign in existing user"""
    try:
        return await auth_service.sign_in(request)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        return await auth_service.refresh_token(refresh_token)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/signout")
async def sign_out(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Sign out current user"""
    # In a real implementation, you might want to blacklist the token
    return {"message": "Successfully signed out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user.get("created_at") or datetime.now(timezone.utc),
        updated_at=current_user.get("updated_at") or datetime.now(timezone.utc),
        email_verified=current_user.get("email_verified", False)
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        return await auth_service.update_user(current_user["id"], request)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user preferences"""
    try:
        return await auth_service.get_user_preferences(current_user["id"])
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    request: UserSettingsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        return await auth_service.update_user_preferences(current_user["id"], request.preferences)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.delete("/me")
async def delete_user_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete current user account"""
    try:
        return await auth_service.delete_user(current_user["id"])
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    """Send password reset email"""
    try:
        return await auth_service.reset_password(request)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/update-password", response_model=PasswordResetResponse)
async def update_password(request: PasswordUpdateRequest):
    """Update password with reset token"""
    try:
        return await auth_service.update_password(request)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )

@router.post("/confirm-email", response_model=EmailConfirmationResponse)
async def confirm_email(request: EmailConfirmationRequest):
    """Confirm user email with token"""
    try:
        return await auth_service.confirm_email(request)
    except AuthError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"}
        )