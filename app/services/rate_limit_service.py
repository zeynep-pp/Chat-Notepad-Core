import redis
import time
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import asyncio
from app.config.config import settings

class RateLimitService:
    def __init__(self):
        # Try to connect to Redis, fallback to database
        self.use_redis = False
        self.redis_client = None
        
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print("✅ Redis connected for rate limiting")
            else:
                print("⚠️ No Redis URL configured, using database fallback")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}, using database fallback")
            self.redis_client = None
            self.use_redis = False

    async def check_rate_limit(
        self,
        user_id: UUID,
        endpoint: str,
        max_requests: int = 100,
        window_seconds: int = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """
        Check if user has exceeded rate limit.
        Returns dict with allowed, remaining, reset_time.
        """
        if self.use_redis:
            return await self._check_rate_limit_redis(
                user_id, endpoint, max_requests, window_seconds
            )
        else:
            return await self._check_rate_limit_database(
                user_id, endpoint, max_requests, window_seconds
            )

    async def _check_rate_limit_redis(
        self,
        user_id: UUID,
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """Redis-based rate limiting using sliding window."""
        try:
            key = f"rate_limit:{user_id}:{endpoint}"
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_seconds)
            
            # Execute pipeline
            results = pipe.execute()
            current_requests = results[1] + 1  # +1 for the current request
            
            allowed = current_requests <= max_requests
            remaining = max(0, max_requests - current_requests)
            reset_time = current_time + window_seconds
            
            return {
                "allowed": allowed,
                "remaining": remaining,
                "reset_time": int(reset_time),
                "total_requests": current_requests,
                "max_requests": max_requests
            }
            
        except Exception as e:
            print(f"Redis rate limit error: {e}")
            # Fallback to database
            return await self._check_rate_limit_database(
                user_id, endpoint, max_requests, window_seconds
            )

    async def _check_rate_limit_database(
        self,
        user_id: UUID,
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """Database-based rate limiting."""
        try:
            from app.config.supabase import get_supabase_client
            supabase = get_supabase_client()
            
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window_seconds)
            
            # Check existing rate limit record
            result = supabase.table("rate_limits") \
                .select("*") \
                .eq("user_id", str(user_id)) \
                .eq("endpoint", endpoint) \
                .single() \
                .execute()
            
            if result.data:
                rate_limit = result.data
                
                # Check if window has expired
                window_start_time = datetime.fromisoformat(
                    rate_limit["window_start"].replace('Z', '+00:00')
                )
                
                if current_time - window_start_time > timedelta(seconds=window_seconds):
                    # Reset window
                    supabase.table("rate_limits") \
                        .update({
                            "requests_count": 1,
                            "window_start": current_time.isoformat(),
                            "max_requests": max_requests,
                            "window_duration": window_seconds
                        }) \
                        .eq("id", rate_limit["id"]) \
                        .execute()
                    
                    return {
                        "allowed": True,
                        "remaining": max_requests - 1,
                        "reset_time": int((current_time + timedelta(seconds=window_seconds)).timestamp()),
                        "total_requests": 1,
                        "max_requests": max_requests
                    }
                else:
                    # Check current count
                    current_requests = rate_limit["requests_count"] + 1
                    allowed = current_requests <= max_requests
                    
                    if allowed:
                        # Update count
                        supabase.table("rate_limits") \
                            .update({"requests_count": current_requests}) \
                            .eq("id", rate_limit["id"]) \
                            .execute()
                    
                    remaining = max(0, max_requests - current_requests)
                    reset_time = int((window_start_time + timedelta(seconds=window_seconds)).timestamp())
                    
                    return {
                        "allowed": allowed,
                        "remaining": remaining,
                        "reset_time": reset_time,
                        "total_requests": current_requests,
                        "max_requests": max_requests
                    }
            else:
                # Create new rate limit record
                supabase.table("rate_limits") \
                    .insert({
                        "user_id": str(user_id),
                        "endpoint": endpoint,
                        "requests_count": 1,
                        "window_start": current_time.isoformat(),
                        "window_duration": window_seconds,
                        "max_requests": max_requests
                    }) \
                    .execute()
                
                return {
                    "allowed": True,
                    "remaining": max_requests - 1,
                    "reset_time": int((current_time + timedelta(seconds=window_seconds)).timestamp()),
                    "total_requests": 1,
                    "max_requests": max_requests
                }
                
        except Exception as e:
            print(f"Database rate limit error: {e}")
            # If all fails, allow the request
            return {
                "allowed": True,
                "remaining": max_requests,
                "reset_time": int((datetime.now() + timedelta(seconds=window_seconds)).timestamp()),
                "total_requests": 0,
                "max_requests": max_requests
            }

    async def get_user_rate_limits(self, user_id: UUID) -> Dict[str, Any]:
        """Get current rate limit status for all endpoints for a user."""
        try:
            if self.use_redis:
                # Get all rate limit keys for this user
                pattern = f"rate_limit:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                
                limits = {}
                for key in keys:
                    endpoint = key.split(':')[-1]
                    count = self.redis_client.zcard(key)
                    ttl = self.redis_client.ttl(key)
                    
                    limits[endpoint] = {
                        "current_requests": count,
                        "ttl_seconds": ttl
                    }
                
                return limits
            else:
                from app.config.supabase import get_supabase_client
                supabase = get_supabase_client()
                
                result = supabase.table("rate_limits") \
                    .select("*") \
                    .eq("user_id", str(user_id)) \
                    .execute()
                
                limits = {}
                for rate_limit in result.data:
                    endpoint = rate_limit["endpoint"]
                    window_start = datetime.fromisoformat(
                        rate_limit["window_start"].replace('Z', '+00:00')
                    )
                    window_end = window_start + timedelta(seconds=rate_limit["window_duration"])
                    ttl_seconds = max(0, int((window_end - datetime.now()).total_seconds()))
                    
                    limits[endpoint] = {
                        "current_requests": rate_limit["requests_count"],
                        "max_requests": rate_limit["max_requests"],
                        "ttl_seconds": ttl_seconds,
                        "window_start": rate_limit["window_start"]
                    }
                
                return limits
                
        except Exception as e:
            print(f"Error getting user rate limits: {e}")
            return {}

    async def reset_user_limits(self, user_id: UUID, endpoint: Optional[str] = None):
        """Reset rate limits for a user (admin function)."""
        try:
            if self.use_redis:
                if endpoint:
                    key = f"rate_limit:{user_id}:{endpoint}"
                    self.redis_client.delete(key)
                else:
                    pattern = f"rate_limit:{user_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            else:
                from app.config.supabase import get_supabase_client
                supabase = get_supabase_client()
                
                query = supabase.table("rate_limits") \
                    .delete() \
                    .eq("user_id", str(user_id))
                
                if endpoint:
                    query = query.eq("endpoint", endpoint)
                
                query.execute()
                
        except Exception as e:
            print(f"Error resetting rate limits: {e}")

# Rate limiting decorator
def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from function parameters
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            current_user = bound_args.arguments.get('current_user')
            if not current_user:
                return await func(*args, **kwargs)
            
            user_id = UUID(current_user["id"])
            endpoint = func.__name__
            
            rate_service = RateLimitService()
            rate_check = await rate_service.check_rate_limit(
                user_id=user_id,
                endpoint=endpoint,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            if not rate_check["allowed"]:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Rate limit exceeded",
                        "reset_time": rate_check["reset_time"],
                        "remaining": rate_check["remaining"]
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator