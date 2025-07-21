from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import re
from io import StringIO
from fastapi import UploadFile

# Try to import magic, fallback to extension-based detection if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

from ..models.requests import NoteCreate, NoteResponse
from .note_service import note_service


class ImportService:
    def __init__(self):
        self.note_service = note_service
        self.supported_formats = {
            'text/plain': self._import_text,
            'text/markdown': self._import_markdown,
            'application/json': self._import_json,
            'text/x-markdown': self._import_markdown,
            'application/x-markdown': self._import_markdown,
        }

    async def import_file(self, file: UploadFile, user_id: UUID) -> Dict[str, Any]:
        """Import a file and create notes"""
        try:
            # Read file content
            content = await file.read()
            
            # Detect file type
            if MAGIC_AVAILABLE:
                try:
                    mime_type = magic.from_buffer(content, mime=True)
                except Exception:
                    mime_type = self._get_mime_from_extension(file.filename)
            else:
                mime_type = self._get_mime_from_extension(file.filename)
            
            # Fallback to filename extension if magic fails or returns unknown
            if mime_type == 'application/octet-stream' or mime_type not in self.supported_formats:
                mime_type = self._get_mime_from_extension(file.filename)
            
            if mime_type not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {mime_type}")
            
            # Decode content
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except UnicodeDecodeError:
                    raise ValueError("Unable to decode file content")
            
            # Import using appropriate handler
            import_handler = self.supported_formats[mime_type]
            notes_data = await import_handler(text_content, file.filename)
            
            # Create notes in database
            created_notes = []
            errors = []
            
            for note_data in notes_data:
                try:
                    note_create = NoteCreate(**note_data)
                    note = await self.note_service.create_note(note_create, user_id)
                    created_notes.append(note)
                except Exception as e:
                    errors.append(f"Error creating note '{note_data.get('title', 'Unknown')}': {str(e)}")
            
            return {
                "success": True,
                "imported_count": len(created_notes),
                "total_count": len(notes_data),
                "notes": created_notes,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "imported_count": 0,
                "total_count": 0,
                "notes": [],
                "errors": [str(e)]
            }

    def _get_mime_from_extension(self, filename: str) -> str:
        """Get MIME type from file extension"""
        if not filename:
            return 'text/plain'
        
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        extension_map = {
            'txt': 'text/plain',
            'md': 'text/markdown',
            'markdown': 'text/markdown',
            'json': 'application/json',
        }
        
        return extension_map.get(extension, 'text/plain')

    async def _import_text(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Import plain text file"""
        # Extract title from filename (without extension)
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        return [{
            "title": title,
            "content": content.strip(),
            "tags": ["imported", "text"],
            "is_favorite": False
        }]

    async def _import_markdown(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Import Markdown file(s) - can contain multiple notes"""
        notes = []
        
        # Split by H1 headers to handle multiple notes in one file
        sections = re.split(r'^# (.+)$', content, flags=re.MULTILINE)
        
        if len(sections) == 1:
            # Single note without H1 header
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            notes.append({
                "title": title,
                "content": content.strip(),
                "tags": ["imported", "markdown"],
                "is_favorite": False
            })
        else:
            # Multiple notes or single note with H1 header
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    title = sections[i].strip()
                    note_content = sections[i + 1].strip()
                    
                    # Extract tags from content if present
                    tags = ["imported", "markdown"]
                    tag_match = re.search(r'\*\*Tags:\*\*\s*(.+)', note_content)
                    if tag_match:
                        extracted_tags = [tag.strip() for tag in tag_match.group(1).split(',')]
                        tags.extend(extracted_tags)
                        # Remove tags line from content
                        note_content = re.sub(r'\*\*Tags:\*\*\s*.+\n?', '', note_content).strip()
                    
                    # Remove metadata section if present
                    note_content = re.sub(r'---\s*\nCreated:.*?\nUpdated:.*?\n', '', note_content, flags=re.DOTALL).strip()
                    
                    notes.append({
                        "title": title,
                        "content": note_content,
                        "tags": list(set(tags)),  # Remove duplicates
                        "is_favorite": False
                    })
        
        return notes

    async def _import_json(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Import JSON file - can be single note or array of notes"""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        notes = []
        
        if isinstance(data, dict):
            # Single note
            note = self._process_json_note(data, filename)
            if note:
                notes.append(note)
        elif isinstance(data, list):
            # Multiple notes
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    note = self._process_json_note(item, f"{filename}_note_{i+1}")
                    if note:
                        notes.append(note)
        else:
            raise ValueError("JSON must contain an object or array of objects")
        
        return notes

    def _process_json_note(self, data: dict, fallback_title: str) -> Optional[Dict[str, Any]]:
        """Process a single JSON note object"""
        # Extract title
        title = data.get('title') or data.get('name') or fallback_title
        
        # Extract content
        content = data.get('content') or data.get('text') or data.get('body') or ""
        
        # Extract tags
        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]
        elif not isinstance(tags, list):
            tags = []
        
        # Add imported tag
        tags = list(set(tags + ["imported", "json"]))
        
        # Extract favorite status
        is_favorite = data.get('is_favorite', False) or data.get('favorite', False)
        
        # Validate required fields
        if not title and not content:
            return None
        
        return {
            "title": title or "Untitled",
            "content": content,
            "tags": tags,
            "is_favorite": bool(is_favorite)
        }

    async def import_from_url(self, url: str, user_id: UUID) -> Dict[str, Any]:
        """Import content from a URL (future enhancement)"""
        # This is a placeholder for future URL import functionality
        raise NotImplementedError("URL import functionality not yet implemented")

    async def get_supported_formats(self) -> Dict[str, str]:
        """Get list of supported import formats"""
        return {
            "text/plain": "Plain Text (.txt)",
            "text/markdown": "Markdown (.md, .markdown)",
            "application/json": "JSON (.json)",
        }

    async def validate_import_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate import data before creating notes"""
        valid_notes = []
        errors = []
        
        for i, note_data in enumerate(data):
            try:
                # Validate required fields
                if not note_data.get('title') and not note_data.get('content'):
                    errors.append(f"Note {i+1}: Must have either title or content")
                    continue
                
                # Validate title length
                title = note_data.get('title', '')
                if len(title) > 200:
                    errors.append(f"Note {i+1}: Title too long (max 200 characters)")
                    continue
                
                # Validate content length
                content = note_data.get('content', '')
                if len(content) > 50000:  # 50KB limit
                    errors.append(f"Note {i+1}: Content too long (max 50KB)")
                    continue
                
                # Validate tags
                tags = note_data.get('tags', [])
                if not isinstance(tags, list):
                    errors.append(f"Note {i+1}: Tags must be an array")
                    continue
                
                if len(tags) > 20:
                    errors.append(f"Note {i+1}: Too many tags (max 20)")
                    continue
                
                # Validate tag names
                for tag in tags:
                    if not isinstance(tag, str) or len(tag) > 50:
                        errors.append(f"Note {i+1}: Invalid tag '{tag}' (max 50 characters)")
                        break
                else:
                    valid_notes.append(note_data)
                    
            except Exception as e:
                errors.append(f"Note {i+1}: Validation error - {str(e)}")
        
        return {
            "valid_notes": valid_notes,
            "errors": errors,
            "valid_count": len(valid_notes),
            "total_count": len(data)
        }


# Singleton instance
import_service = ImportService()