from typing import List, Optional
from uuid import UUID
import math

from ..config.supabase import supabase_client
from ..models.requests import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse


class NoteService:
    def __init__(self):
        self.supabase = supabase_client
        self.table_name = "user_notes"

    async def create_note(self, note_data: NoteCreate, user_id: UUID) -> NoteResponse:
        """Create a new note for the user"""
        try:
            note_dict = note_data.model_dump()
            note_dict['user_id'] = str(user_id)
            
            response = self.supabase.table(self.table_name).insert(note_dict).execute()
            
            if response.data:
                return NoteResponse(**response.data[0])
            else:
                raise Exception("Failed to create note")
                
        except Exception as e:
            raise Exception(f"Error creating note: {str(e)}")

    async def get_note(self, note_id: UUID, user_id: UUID) -> Optional[NoteResponse]:
        """Get a specific note by ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq(
                "id", str(note_id)
            ).eq("user_id", str(user_id)).execute()
            
            if response.data:
                return NoteResponse(**response.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching note: {str(e)}")

    async def update_note(self, note_id: UUID, note_data: NoteUpdate, user_id: UUID) -> Optional[NoteResponse]:
        """Update an existing note"""
        try:
            # Only update fields that are provided
            update_dict = {k: v for k, v in note_data.model_dump().items() if v is not None}
            
            if not update_dict:
                # If no updates, return current note
                return await self.get_note(note_id, user_id)
            
            response = self.supabase.table(self.table_name).update(update_dict).eq(
                "id", str(note_id)
            ).eq("user_id", str(user_id)).execute()
            
            if response.data:
                return NoteResponse(**response.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Error updating note: {str(e)}")

    async def delete_note(self, note_id: UUID, user_id: UUID) -> bool:
        """Delete a note"""
        try:
            response = self.supabase.table(self.table_name).delete().eq(
                "id", str(note_id)
            ).eq("user_id", str(user_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Error deleting note: {str(e)}")

    async def list_notes(
        self, 
        user_id: UUID, 
        page: int = 1, 
        per_page: int = 20,
        is_favorite: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> NoteListResponse:
        """List user's notes with pagination and filtering"""
        try:
            # Build query
            query = self.supabase.table(self.table_name).select("*").eq("user_id", str(user_id))
            
            # Add filters
            if is_favorite is not None:
                query = query.eq("is_favorite", is_favorite)
            
            if tags:
                query = query.contains("tags", tags)
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.range(offset, offset + per_page - 1)
            
            # Order by updated_at desc
            query = query.order("updated_at", desc=True)
            
            response = query.execute()
            
            # Get total count with a separate query
            count_query = self.supabase.table(self.table_name).select("id").eq("user_id", str(user_id))
            if is_favorite is not None:
                count_query = count_query.eq("is_favorite", is_favorite)
            if tags:
                count_query = count_query.contains("tags", tags)
            count_response = count_query.execute()
            
            total = len(count_response.data) if count_response.data else 0
            pages = math.ceil(total / per_page)
            
            notes = [NoteResponse(**note) for note in response.data]
            
            return NoteListResponse(
                notes=notes,
                total=total,
                page=page,
                per_page=per_page,
                pages=pages
            )
            
        except Exception as e:
            raise Exception(f"Error listing notes: {str(e)}")

    async def search_notes(
        self,
        user_id: UUID,
        query: str,
        page: int = 1,
        per_page: int = 20,
        tags: Optional[List[str]] = None,
        is_favorite: Optional[bool] = None
    ) -> NoteListResponse:
        """Search notes using PostgreSQL full-text search"""
        try:
            # Build base query with full-text search
            search_query = self.supabase.table(self.table_name).select("*").eq("user_id", str(user_id))
            
            # Add full-text search on title and content
            search_query = search_query.or_(f"title.ilike.%{query}%,content.ilike.%{query}%")
            
            # Add filters
            if is_favorite is not None:
                search_query = search_query.eq("is_favorite", is_favorite)
            
            if tags:
                search_query = search_query.contains("tags", tags)
            
            # Add pagination
            offset = (page - 1) * per_page
            search_query = search_query.range(offset, offset + per_page - 1)
            
            # Order by updated_at desc
            search_query = search_query.order("updated_at", desc=True)
            
            response = search_query.execute()
            
            # Get total count with a separate query
            count_query = self.supabase.table(self.table_name).select("id").eq("user_id", str(user_id))
            count_query = count_query.or_(f"title.ilike.%{query}%,content.ilike.%{query}%")
            if is_favorite is not None:
                count_query = count_query.eq("is_favorite", is_favorite)
            if tags:
                count_query = count_query.contains("tags", tags)
            count_response = count_query.execute()
            
            total = len(count_response.data) if count_response.data else 0
            pages = math.ceil(total / per_page)
            
            notes = [NoteResponse(**note) for note in response.data]
            
            return NoteListResponse(
                notes=notes,
                total=total,
                page=page,
                per_page=per_page,
                pages=pages
            )
            
        except Exception as e:
            raise Exception(f"Error searching notes: {str(e)}")

    async def get_notes_by_tags(self, user_id: UUID, tags: List[str]) -> List[NoteResponse]:
        """Get notes that contain any of the specified tags"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq(
                "user_id", str(user_id)
            ).overlaps("tags", tags).execute()
            
            return [NoteResponse(**note) for note in response.data]
            
        except Exception as e:
            raise Exception(f"Error fetching notes by tags: {str(e)}")

    async def get_favorite_notes(self, user_id: UUID) -> List[NoteResponse]:
        """Get all favorite notes for a user"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq(
                "user_id", str(user_id)
            ).eq("is_favorite", True).order("updated_at", desc=True).execute()
            
            return [NoteResponse(**note) for note in response.data]
            
        except Exception as e:
            raise Exception(f"Error fetching favorite notes: {str(e)}")

    async def get_user_tags(self, user_id: UUID) -> List[str]:
        """Get all unique tags used by a user"""
        try:
            response = self.supabase.table(self.table_name).select("tags").eq(
                "user_id", str(user_id)
            ).execute()
            
            # Flatten and deduplicate tags
            all_tags = set()
            for note in response.data:
                if note.get("tags"):
                    all_tags.update(note["tags"])
            
            return sorted(list(all_tags))
            
        except Exception as e:
            raise Exception(f"Error fetching user tags: {str(e)}")


# Singleton instance
note_service = NoteService()