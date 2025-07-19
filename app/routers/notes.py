from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from ..models.requests import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse, NoteSearchRequest
from ..services.note_service import note_service
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new note"""
    try:
        user_id = UUID(current_user["sub"])
        note = await note_service.create_note(note_data, user_id)
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=NoteListResponse)
async def list_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_favorite: Optional[bool] = Query(None),
    tags: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List user's notes with pagination and filtering"""
    try:
        user_id = UUID(current_user["sub"])
        notes = await note_service.list_notes(
            user_id=user_id,
            page=page,
            per_page=per_page,
            is_favorite=is_favorite,
            tags=tags
        )
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=NoteListResponse)
async def search_notes(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_favorite: Optional[bool] = Query(None),
    tags: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Search notes using full-text search"""
    try:
        user_id = UUID(current_user["sub"])
        notes = await note_service.search_notes(
            user_id=user_id,
            query=query,
            page=page,
            per_page=per_page,
            is_favorite=is_favorite,
            tags=tags
        )
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites", response_model=List[NoteResponse])
async def get_favorite_notes(
    current_user: dict = Depends(get_current_user)
):
    """Get all favorite notes"""
    try:
        user_id = UUID(current_user["sub"])
        notes = await note_service.get_favorite_notes(user_id)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags", response_model=List[str])
async def get_user_tags(
    current_user: dict = Depends(get_current_user)
):
    """Get all unique tags used by the user"""
    try:
        user_id = UUID(current_user["sub"])
        tags = await note_service.get_user_tags(user_id)
        return tags
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific note by ID"""
    try:
        user_id = UUID(current_user["sub"])
        note = await note_service.get_note(note_id, user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing note"""
    try:
        user_id = UUID(current_user["sub"])
        note = await note_service.update_note(note_id, note_data, user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{note_id}")
async def delete_note(
    note_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a note"""
    try:
        user_id = UUID(current_user["sub"])
        success = await note_service.delete_note(note_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))