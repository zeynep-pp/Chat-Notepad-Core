from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.middleware.auth_middleware import get_current_user
from app.services.version_service import VersionService
from app.models.requests import (
    NoteVersionResponse,
    NoteVersionCreate,
    NoteVersionsListResponse,
    NoteDiffResponse
)

router = APIRouter(prefix="/api/v1/notes", tags=["versions"])
version_service = VersionService()

@router.get("/{note_id}/versions", response_model=NoteVersionsListResponse)
async def get_note_versions(
    note_id: UUID,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get all versions for a note."""
    try:
        user_id = UUID(current_user["id"])
        return await version_service.get_note_versions(
            user_id=user_id,
            note_id=note_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{note_id}/versions", response_model=NoteVersionResponse)
async def create_note_version(
    note_id: UUID,
    version_data: NoteVersionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new version of a note."""
    try:
        user_id = UUID(current_user["id"])
        
        # Get current note content
        from app.services.note_service import NoteService
        note_service = NoteService()
        note = await note_service.get_note(user_id, note_id)
        
        return await version_service.create_version(
            user_id=user_id,
            note_id=note_id,
            content=note.content,
            change_description=version_data.change_description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{note_id}/versions/{version_id}", response_model=NoteVersionResponse)
async def get_note_version(
    note_id: UUID,
    version_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific version of a note."""
    try:
        user_id = UUID(current_user["id"])
        return await version_service.get_version(
            user_id=user_id,
            note_id=note_id,
            version_id=version_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{note_id}/restore/{version_id}")
async def restore_note_version(
    note_id: UUID,
    version_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Restore a note to a specific version."""
    try:
        user_id = UUID(current_user["id"])
        success = await version_service.restore_version(
            user_id=user_id,
            note_id=note_id,
            version_id=version_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to restore version"
            )
        
        return {"message": "Version restored successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{note_id}/diff/{version1}/{version2}", response_model=NoteDiffResponse)
async def get_version_diff(
    note_id: UUID,
    version1: int,
    version2: int,
    current_user: dict = Depends(get_current_user)
):
    """Get diff between two versions of a note."""
    try:
        user_id = UUID(current_user["id"])
        return await version_service.get_diff(
            user_id=user_id,
            note_id=note_id,
            version1_num=version1,
            version2_num=version2
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )