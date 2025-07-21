from typing import List, BinaryIO
from uuid import UUID
import io
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from ..models.requests import NoteResponse
from .note_service import note_service


class ExportService:
    def __init__(self):
        self.note_service = note_service

    async def export_note_markdown(self, note_id: UUID, user_id: UUID) -> str:
        """Export a note as Markdown format"""
        note = await self.note_service.get_note(note_id, user_id)
        if not note:
            raise ValueError("Note not found")

        markdown_content = f"# {note.title}\n\n"
        
        if note.tags:
            markdown_content += f"**Tags:** {', '.join(note.tags)}\n\n"
        
        if note.content:
            markdown_content += f"{note.content}\n\n"
        
        markdown_content += f"---\n"
        markdown_content += f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return markdown_content

    async def export_note_txt(self, note_id: UUID, user_id: UUID) -> str:
        """Export a note as plain text format"""
        note = await self.note_service.get_note(note_id, user_id)
        if not note:
            raise ValueError("Note not found")

        txt_content = f"{note.title}\n"
        txt_content += "=" * len(note.title) + "\n\n"
        
        if note.tags:
            txt_content += f"Tags: {', '.join(note.tags)}\n\n"
        
        if note.content:
            txt_content += f"{note.content}\n\n"
        
        txt_content += "-" * 50 + "\n"
        txt_content += f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return txt_content

    async def export_note_pdf(self, note_id: UUID, user_id: UUID) -> bytes:
        """Export a note as PDF format"""
        note = await self.note_service.get_note(note_id, user_id)
        if not note:
            raise ValueError("Note not found")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = styles['Title']
        title_style.alignment = TA_CENTER
        title = Paragraph(note.title, title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Tags
        if note.tags:
            tags_text = f"<b>Tags:</b> {', '.join(note.tags)}"
            tags_para = Paragraph(tags_text, styles['Normal'])
            story.append(tags_para)
            story.append(Spacer(1, 10))
        
        # Content
        if note.content:
            # Replace newlines with <br/> for proper PDF formatting
            content_formatted = note.content.replace('\n', '<br/>')
            content_para = Paragraph(content_formatted, styles['Normal'])
            story.append(content_para)
            story.append(Spacer(1, 20))
        
        # Metadata
        story.append(Spacer(1, 30))
        divider = Paragraph("-" * 50, styles['Normal'])
        story.append(divider)
        story.append(Spacer(1, 10))
        
        created_text = f"<b>Created:</b> {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        created_para = Paragraph(created_text, styles['Normal'])
        story.append(created_para)
        
        updated_text = f"<b>Updated:</b> {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        updated_para = Paragraph(updated_text, styles['Normal'])
        story.append(updated_para)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    async def export_notes_bulk_markdown(self, note_ids: List[UUID], user_id: UUID) -> str:
        """Export multiple notes as a single Markdown file"""
        markdown_content = f"# Exported Notes\n\n"
        markdown_content += f"Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += "---\n\n"
        
        for note_id in note_ids:
            try:
                note = await self.note_service.get_note(note_id, user_id)
                if note:
                    markdown_content += f"## {note.title}\n\n"
                    
                    if note.tags:
                        markdown_content += f"**Tags:** {', '.join(note.tags)}\n\n"
                    
                    if note.content:
                        markdown_content += f"{note.content}\n\n"
                    
                    markdown_content += f"*Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')} | "
                    markdown_content += f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                    markdown_content += "---\n\n"
            except Exception as e:
                markdown_content += f"## Error exporting note {note_id}\n\n"
                markdown_content += f"Error: {str(e)}\n\n---\n\n"
        
        return markdown_content

    async def export_notes_bulk_txt(self, note_ids: List[UUID], user_id: UUID) -> str:
        """Export multiple notes as a single text file"""
        txt_content = f"EXPORTED NOTES\n"
        txt_content += "=" * 50 + "\n\n"
        txt_content += f"Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, note_id in enumerate(note_ids, 1):
            try:
                note = await self.note_service.get_note(note_id, user_id)
                if note:
                    txt_content += f"{i}. {note.title}\n"
                    txt_content += "-" * (len(f"{i}. {note.title}")) + "\n\n"
                    
                    if note.tags:
                        txt_content += f"Tags: {', '.join(note.tags)}\n\n"
                    
                    if note.content:
                        txt_content += f"{note.content}\n\n"
                    
                    txt_content += f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    txt_content += f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    txt_content += "=" * 50 + "\n\n"
            except Exception as e:
                txt_content += f"{i}. Error exporting note {note_id}\n"
                txt_content += f"Error: {str(e)}\n\n"
                txt_content += "=" * 50 + "\n\n"
        
        return txt_content

    async def get_export_filename(self, note_id: UUID, user_id: UUID, format: str) -> str:
        """Generate appropriate filename for export"""
        note = await self.note_service.get_note(note_id, user_id)
        if not note:
            return f"note_{note_id}.{format}"
        
        # Sanitize title for filename
        safe_title = "".join(c for c in note.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{safe_title}_{timestamp}.{format}"

    async def get_bulk_export_filename(self, format: str, count: int) -> str:
        """Generate filename for bulk export"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"notes_export_{count}_items_{timestamp}.{format}"


# Singleton instance
export_service = ExportService()