from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from uuid import UUID
from app.middleware.auth_middleware import get_current_user
from app.services.history_service import HistoryService
from app.models.requests import (
    CommandHistoryResponse,
    CommandHistoryListResponse,
    CommandStatsResponse
)

router = APIRouter(prefix="/api/v1/history", tags=["history"])
history_service = HistoryService()

@router.get("/commands", response_model=CommandHistoryListResponse)
async def get_command_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    command_filter: Optional[str] = Query(None),
    success_filter: Optional[bool] = Query(None),
    days_back: Optional[int] = Query(None, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get user's command history with filtering and pagination."""
    try:
        user_id = UUID(current_user["id"])
        return await history_service.get_command_history(
            user_id=user_id,
            page=page,
            per_page=per_page,
            command_filter=command_filter,
            success_filter=success_filter,
            days_back=days_back
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", response_model=CommandStatsResponse)
async def get_command_stats(
    days_back: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get command usage statistics."""
    try:
        user_id = UUID(current_user["id"])
        return await history_service.get_command_stats(
            user_id=user_id,
            days_back=days_back
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/search", response_model=List[CommandHistoryResponse])
async def search_command_history(
    q: str = Query(..., min_length=1),
    search_in: str = Query("both", regex="^(command|input|output|both)$"),
    current_user: dict = Depends(get_current_user)
):
    """Search through command history."""
    try:
        user_id = UUID(current_user["id"])
        return await history_service.search_commands(
            user_id=user_id,
            search_term=q,
            search_in=search_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/popular", response_model=List[dict])
async def get_popular_commands(
    limit: int = Query(10, ge=1, le=50),
    days_back: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Get most popular commands for suggestions."""
    try:
        user_id = UUID(current_user["id"])
        return await history_service.get_popular_commands(
            user_id=user_id,
            limit=limit,
            days_back=days_back
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/cleanup")
async def cleanup_old_history(
    days_to_keep: int = Query(90, ge=30, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Delete old command history entries."""
    try:
        user_id = UUID(current_user["id"])
        deleted_count = await history_service.delete_old_history(
            user_id=user_id,
            days_to_keep=days_to_keep
        )
        
        return {
            "message": f"Successfully deleted {deleted_count} old history entries",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )