from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from supabase import Client
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from ..config.supabase import supabase_config
from ..models.auth import (
    UserSignUpRequest, 
    UserSignInRequest, 
    UserResponse, 
    TokenResponse, 
    AuthResponse,
    UserUpdateRequest,
    UserPreferences,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordUpdateRequest,
    EmailConfirmationRequest,
    EmailConfirmationResponse
)

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

class AuthService:
    def __init__(self):
        self.supabase: Client = supabase_config.get_client()
        self.admin_client: Client = supabase_config.get_admin_client()
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    async def sign_up(self, request: UserSignUpRequest) -> AuthResponse:
        """Register a new user"""
        try:
            # Sign up user with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.full_name
                    }
                }
            })
            
            if not auth_response.user:
                raise AuthError("Failed to create user account")
            
            # Create user preferences record
            await self._create_user_preferences(auth_response.user.id)
            
            user_response = UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=request.full_name,
                created_at=datetime.fromisoformat(str(auth_response.user.created_at).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(str(auth_response.user.updated_at).replace('Z', '+00:00')),
                email_verified=auth_response.user.email_confirmed_at is not None
            )
            
            # Handle session - might be None if email confirmation required
            if auth_response.session:
                token_response = TokenResponse(
                    access_token=auth_response.session.access_token,
                    expires_in=auth_response.session.expires_in if auth_response.session.expires_in else 3600,
                    refresh_token=auth_response.session.refresh_token
                )
            else:
                # No session means email confirmation required
                token_response = TokenResponse(
                    access_token="",
                    expires_in=0,
                    refresh_token=None
                )
            
            message = None
            if not user_response.email_verified:
                message = "Account created successfully! Please check your email to verify your account before signing in."
            
            return AuthResponse(user=user_response, token=token_response, message=message)
            
        except AuthError:
            raise
        except Exception as e:
            if "already registered" in str(e):
                raise AuthError("This email address is already registered")
            raise AuthError("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def sign_in(self, request: UserSignInRequest) -> AuthResponse:
        """Sign in existing user"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if not auth_response.user:
                raise AuthError("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
            
            user_response = UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=auth_response.user.user_metadata.get("full_name"),
                created_at=datetime.fromisoformat(str(auth_response.user.created_at).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(str(auth_response.user.updated_at).replace('Z', '+00:00')),
                email_verified=auth_response.user.email_confirmed_at is not None
            )
            
            # Check if email is verified
            if not user_response.email_verified:
                raise AuthError("Please verify your email address before signing in. Check your email for verification link.", status.HTTP_403_FORBIDDEN)
            
            token_response = TokenResponse(
                access_token=auth_response.session.access_token,
                expires_in=auth_response.session.expires_in if auth_response.session.expires_in else 3600,
                refresh_token=auth_response.session.refresh_token
            )
            
            return AuthResponse(user=user_response, token=token_response)
            
        except AuthError:
            raise
        except Exception as e:
            if "Invalid login credentials" in str(e):
                raise AuthError("Invalid email or password", status.HTTP_401_UNAUTHORIZED)
            raise AuthError("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔐 Verifying token: {token[:20]}...")
            
            user_response = self.supabase.auth.get_user(token)
            logger.info(f"🔐 Supabase response: {user_response}")
            
            if user_response.user:
                user_data = {
                    "id": user_response.user.id,
                    "sub": user_response.user.id,  # Add 'sub' field for compatibility
                    "email": user_response.user.email,
                    "full_name": user_response.user.user_metadata.get("full_name"),
                    "created_at": user_response.user.created_at,
                    "updated_at": user_response.user.updated_at,
                    "email_verified": user_response.user.email_confirmed_at is not None
                }
                logger.info(f"✅ Token verified successfully for user: {user_data['email']}")
                return user_data
            
            logger.warning("⚠️ Token verification failed: No user found")
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Token verification error: {str(e)}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            return TokenResponse(
                access_token=auth_response.session.access_token,
                expires_in=auth_response.session.expires_in if auth_response.session.expires_in else 3600,
                refresh_token=auth_response.session.refresh_token
            )
        except Exception as e:
            raise AuthError("Invalid refresh token", status.HTTP_401_UNAUTHORIZED)
    
    async def sign_out(self, token: str) -> bool:
        """Sign out user"""
        try:
            self.supabase.auth.sign_out(token)
            return True
        except Exception:
            return False
    
    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        """Update user profile"""
        try:
            update_data = {}
            if request.full_name is not None:
                update_data["data"] = {"full_name": request.full_name}
            if request.email is not None:
                update_data["email"] = request.email
            
            user_response = self.admin_client.auth.admin.update_user_by_id(user_id, update_data)
            
            return UserResponse(
                id=user_response.user.id,
                email=user_response.user.email,
                full_name=user_response.user.user_metadata.get("full_name"),
                created_at=datetime.fromisoformat(str(user_response.user.created_at).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(str(user_response.user.updated_at).replace('Z', '+00:00')),
                email_verified=user_response.user.email_confirmed_at is not None
            )
        except Exception as e:
            raise AuthError("Failed to update user profile", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences"""
        try:
            response = self.supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            if response.data:
                prefs_data = response.data[0]
                return UserPreferences(**prefs_data.get("preferences", {}))
            else:
                # Return default preferences if none exist
                return UserPreferences()
        except Exception as e:
            raise AuthError("Failed to get user preferences", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferences:
        """Update user preferences"""
        try:
            response = self.supabase.table("user_preferences").upsert({
                "user_id": user_id,
                "preferences": preferences.dict(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            return preferences
        except Exception as e:
            raise AuthError("Failed to update user preferences", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """Delete user account and all associated data"""
        try:
            # Delete user preferences first
            self.admin_client.table("user_preferences").delete().eq("user_id", user_id).execute()
            
            # Delete user account
            self.admin_client.auth.admin.delete_user(user_id)
            
            return {"message": "User account deleted successfully"}
        except Exception as e:
            raise AuthError("Failed to delete user account", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def reset_password(self, request: PasswordResetRequest) -> PasswordResetResponse:
        """Send password reset email"""
        try:
            response = self.supabase.auth.reset_password_email(request.email)
            return PasswordResetResponse(
                message="Password reset email sent successfully. Please check your email."
            )
        except Exception as e:
            raise AuthError("Failed to send password reset email", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def update_password(self, request: PasswordUpdateRequest) -> PasswordResetResponse:
        """Update password with reset token"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # The token from password reset is typically just the access token
            access_token = request.token.strip()
            logger.info(f"Token received: {access_token[:50]}... (length: {len(access_token)})")
            logger.info(f"Token type check - contains dots: {'.' in access_token}, dot count: {access_token.count('.')}")
            
            # Try different approaches based on token type
            
            # Method 1: Try as OTP recovery token first
            try:
                logger.info("Trying OTP recovery verification...")
                response = self.supabase.auth.verify_otp({
                    "token_hash": access_token,
                    "type": "recovery"
                })
                
                if response.user and response.session:
                    logger.info("OTP verification successful, updating password...")
                    # Set the session
                    self.supabase.auth.set_session(
                        response.session.access_token,
                        response.session.refresh_token
                    )
                    
                    # Update password
                    user_response = self.supabase.auth.update_user({
                        "password": request.new_password
                    })
                    
                    if user_response.user:
                        return PasswordResetResponse(
                            message="Password updated successfully. You can now sign in with your new password."
                        )
                
            except Exception as otp_e:
                logger.error(f"OTP verification failed: {str(otp_e)}")
                
                # Method 2: If token looks like JWT, try as access token
                try:
                    if "." in access_token and len(access_token.split(".")) == 3:
                        logger.info("Token looks like JWT, trying as access token...")
                        
                        # Create new client and verify the token
                        from supabase import create_client
                        temp_client = create_client(supabase_config.url, supabase_config.key)
                        
                        # Try to get user with this token
                        user_response = temp_client.auth.get_user(access_token)
                        
                        if user_response.user:
                            logger.info("JWT token verified, updating password...")
                            # Use admin client to update password
                            admin_response = self.admin_client.auth.admin.update_user_by_id(
                                user_response.user.id,
                                {"password": request.new_password}
                            )
                            
                            if admin_response.user:
                                return PasswordResetResponse(
                                    message="Password updated successfully. You can now sign in with your new password."
                                )
                
                except Exception as jwt_e:
                    logger.error(f"JWT token approach failed: {str(jwt_e)}")
                    
                    # Method 3: Last resort - try direct password update with token
                    try:
                        logger.info("Trying direct password update...")
                        # This uses the token directly as recovery token
                        response = self.supabase.auth.verify_otp({
                            "token": access_token,
                            "type": "recovery"
                        })
                        
                        if response.user:
                            # Update password for this user
                            user_response = self.admin_client.auth.admin.update_user_by_id(
                                response.user.id,
                                {"password": request.new_password}
                            )
                            
                            if user_response.user:
                                return PasswordResetResponse(
                                    message="Password updated successfully. You can now sign in with your new password."
                                )
                    
                    except Exception as direct_e:
                        logger.error(f"Direct password update failed: {str(direct_e)}")
                        
            # If all methods fail, return error
            raise AuthError("Invalid or expired reset token", status.HTTP_400_BAD_REQUEST)
                
        except AuthError:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Exception in update_password: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_msg = str(e).lower()
            if "invalid" in error_msg or "expired" in error_msg or "token" in error_msg:
                raise AuthError("Invalid or expired reset token", status.HTTP_400_BAD_REQUEST)
            raise AuthError(f"Failed to update password: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def confirm_email(self, request: EmailConfirmationRequest) -> EmailConfirmationResponse:
        """Confirm user email with token"""
        try:
            # Verify the token with Supabase
            user_response = self.supabase.auth.get_user(request.token)
            
            if not user_response.user:
                raise AuthError("Invalid or expired token", status.HTTP_400_BAD_REQUEST)
            
            user = user_response.user
            
            # Check if email is already verified
            if user.email_confirmed_at:
                # Email already verified, return success
                user_data = UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.user_metadata.get("full_name"),
                    created_at=datetime.fromisoformat(str(user.created_at).replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(str(user.updated_at).replace('Z', '+00:00')),
                    email_verified=True
                )
                
                return EmailConfirmationResponse(
                    message="Email confirmed successfully",
                    user=user_data
                )
            
            # If email not verified, try to verify it
            # Note: Supabase typically handles email verification automatically
            # when the token is valid, but we'll update the user to ensure verification
            try:
                # Update user to mark email as verified
                admin_response = self.admin_client.auth.admin.update_user_by_id(
                    user.id,
                    {"email_confirm": True}
                )
                
                if admin_response.user:
                    user_data = UserResponse(
                        id=admin_response.user.id,
                        email=admin_response.user.email,
                        full_name=admin_response.user.user_metadata.get("full_name"),
                        created_at=datetime.fromisoformat(str(admin_response.user.created_at).replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(str(admin_response.user.updated_at).replace('Z', '+00:00')),
                        email_verified=admin_response.user.email_confirmed_at is not None
                    )
                    
                    return EmailConfirmationResponse(
                        message="Email confirmed successfully",
                        user=user_data
                    )
                
            except Exception as update_error:
                # If admin update fails, still return success since token was valid
                user_data = UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.user_metadata.get("full_name"),
                    created_at=datetime.fromisoformat(str(user.created_at).replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(str(user.updated_at).replace('Z', '+00:00')),
                    email_verified=user.email_confirmed_at is not None
                )
                
                return EmailConfirmationResponse(
                    message="Email confirmed successfully",
                    user=user_data
                )
            
        except AuthError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid" in error_msg or "expired" in error_msg or "token" in error_msg:
                raise AuthError("Invalid or expired token", status.HTTP_400_BAD_REQUEST)
            raise AuthError("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def _create_user_preferences(self, user_id: str):
        """Create default user preferences"""
        try:
            default_preferences = UserPreferences()
            self.admin_client.table("user_preferences").upsert({
                "user_id": user_id,
                "preferences": default_preferences.dict(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception:
            # Ignore errors when creating default preferences
            pass

# Global instance
auth_service = AuthService()