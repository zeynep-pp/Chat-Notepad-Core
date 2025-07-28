from typing import Optional, List
from uuid import UUID
import diff_match_patch
from supabase import Client
from app.config.supabase import get_supabase_client
from app.models.requests import (
    NoteVersionResponse,
    NoteVersionsListResponse,
    NoteDiffResponse
)

class VersionService:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self.dmp = diff_match_patch.diff_match_patch()

    async def create_version(
        self, 
        user_id: UUID, 
        note_id: UUID, 
        content: str,
        change_description: Optional[str] = None
    ) -> NoteVersionResponse:
        """Create a new version of a note."""
        try:
            # Get the current highest version number
            version_result = self.supabase.table("note_versions") \
                .select("version_number") \
                .eq("note_id", str(note_id)) \
                .order("version_number", desc=True) \
                .limit(1) \
                .execute()
            
            next_version = 1
            if version_result.data:
                next_version = version_result.data[0]["version_number"] + 1
            
            # Create the new version
            version_data = {
                "note_id": str(note_id),
                "user_id": str(user_id),
                "content": content,
                "version_number": next_version,
                "change_description": change_description
            }
            
            result = self.supabase.table("note_versions") \
                .insert(version_data) \
                .execute()
            
            if not result.data:
                raise Exception("Failed to create version")
            
            return NoteVersionResponse(**result.data[0])
            
        except Exception as e:
            raise Exception(f"Failed to create version: {str(e)}")

    async def get_note_versions(
        self, 
        user_id: UUID, 
        note_id: UUID,
        limit: int = 50
    ) -> NoteVersionsListResponse:
        """Get all versions for a note."""
        try:
            # Verify user owns the note
            note_result = self.supabase.table("user_notes") \
                .select("id") \
                .eq("id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .single() \
                .execute()
            
            if not note_result.data:
                raise Exception("Note not found or access denied")
            
            # Get versions
            result = self.supabase.table("note_versions") \
                .select("*") \
                .eq("note_id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .order("version_number", desc=True) \
                .limit(limit) \
                .execute()
            
            versions = [NoteVersionResponse(**version) for version in result.data]
            
            return NoteVersionsListResponse(
                versions=versions,
                total=len(versions),
                note_id=note_id
            )
            
        except Exception as e:
            raise Exception(f"Failed to get versions: {str(e)}")

    async def get_version(
        self, 
        user_id: UUID, 
        note_id: UUID, 
        version_id: UUID
    ) -> NoteVersionResponse:
        """Get a specific version."""
        try:
            result = self.supabase.table("note_versions") \
                .select("*") \
                .eq("id", str(version_id)) \
                .eq("note_id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .single() \
                .execute()
            
            if not result.data:
                raise Exception("Version not found or access denied")
            
            return NoteVersionResponse(**result.data)
            
        except Exception as e:
            raise Exception(f"Failed to get version: {str(e)}")

    async def restore_version(
        self, 
        user_id: UUID, 
        note_id: UUID, 
        version_id: UUID
    ) -> bool:
        """Restore a note to a specific version."""
        try:
            # Get the version content
            version_result = self.supabase.table("note_versions") \
                .select("content") \
                .eq("id", str(version_id)) \
                .eq("note_id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .single() \
                .execute()
            
            if not version_result.data:
                raise Exception("Version not found or access denied")
            
            # Update the note with the version content
            update_result = self.supabase.table("user_notes") \
                .update({"content": version_result.data["content"]}) \
                .eq("id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .execute()
            
            if not update_result.data:
                raise Exception("Failed to restore note")
            
            # Create a new version for the restore action
            await self.create_version(
                user_id=user_id,
                note_id=note_id,
                content=version_result.data["content"],
                change_description=f"Restored from version {version_id}"
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to restore version: {str(e)}")

    async def get_diff(
        self, 
        user_id: UUID, 
        note_id: UUID, 
        version1_num: int, 
        version2_num: int
    ) -> NoteDiffResponse:
        """Get diff between two versions."""
        try:
            # Get both versions
            versions_result = self.supabase.table("note_versions") \
                .select("version_number, content") \
                .eq("note_id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .in_("version_number", [version1_num, version2_num]) \
                .execute()
            
            if len(versions_result.data) != 2:
                raise Exception("One or both versions not found")
            
            # Sort versions by version number
            versions = sorted(versions_result.data, key=lambda x: x["version_number"])
            content1 = versions[0]["content"]
            content2 = versions[1]["content"]
            
            # Generate diff
            diffs = self.dmp.diff_main(content1, content2)
            self.dmp.diff_cleanupSemantic(diffs)
            
            # Generate HTML diff
            diff_html = self.dmp.diff_prettyHtml(diffs)
            
            # Generate text diff
            diff_text = self._generate_text_diff(diffs)
            
            return NoteDiffResponse(
                note_id=note_id,
                version1=version1_num,
                version2=version2_num,
                diff_html=diff_html,
                diff_text=diff_text
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate diff: {str(e)}")

    def _generate_text_diff(self, diffs: List) -> str:
        """Generate a text-based diff representation."""
        result = []
        for op, text in diffs:
            if op == diff_match_patch.diff_match_patch.DIFF_INSERT:
                result.append(f"+ {text}")
            elif op == diff_match_patch.diff_match_patch.DIFF_DELETE:
                result.append(f"- {text}")
            elif op == diff_match_patch.diff_match_patch.DIFF_EQUAL:
                # Only show a snippet for context
                if len(text) > 60:
                    result.append(f"  {text[:30]}...{text[-30:]}")
                else:
                    result.append(f"  {text}")
        
        return "\n".join(result)

    async def auto_save_version(
        self, 
        user_id: UUID, 
        note_id: UUID, 
        content: str
    ) -> Optional[NoteVersionResponse]:
        """Automatically save a version if content has changed significantly."""
        try:
            # Get the last version
            last_version_result = self.supabase.table("note_versions") \
                .select("content") \
                .eq("note_id", str(note_id)) \
                .eq("user_id", str(user_id)) \
                .order("version_number", desc=True) \
                .limit(1) \
                .execute()
            
            # If no previous version or content is significantly different
            should_save = True
            if last_version_result.data:
                last_content = last_version_result.data[0]["content"]
                
                # Calculate similarity
                diffs = self.dmp.diff_main(last_content, content)
                similarity = self._calculate_similarity(diffs, len(content))
                
                # Only save if less than 95% similar (significant change)
                should_save = similarity < 0.95
            
            if should_save:
                return await self.create_version(
                    user_id=user_id,
                    note_id=note_id,
                    content=content,
                    change_description="Auto-saved version"
                )
            
            return None
            
        except Exception as e:
            # Don't fail the main operation if auto-save fails
            print(f"Auto-save version failed: {str(e)}")
            return None

    def _calculate_similarity(self, diffs: List, total_length: int) -> float:
        """Calculate similarity percentage between two texts."""
        if total_length == 0:
            return 1.0
        
        equal_chars = 0
        for op, text in diffs:
            if op == diff_match_patch.diff_match_patch.DIFF_EQUAL:
                equal_chars += len(text)
        
        return equal_chars / total_length