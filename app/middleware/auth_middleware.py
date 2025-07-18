from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from ..services.auth_service import auth_service

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.auth_service = auth_service
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Get current authenticated user"""
        token = credentials.credentials
        user_data = await self.auth_service.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_data
    
    async def get_optional_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        """Get current user if token is provided (optional auth)"""
        if not credentials:
            return None
        
        token = credentials.credentials
        return await self.auth_service.verify_token(token)

# Global instance
auth_middleware = AuthMiddleware()

# Helper functions for dependency injection
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    return await auth_middleware.get_current_user(credentials)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Dependency to get current user (optional)"""
    return await auth_middleware.get_optional_user(credentials)