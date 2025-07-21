from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import Response, JSONResponse
from typing import List, Optional
from uuid import UUID

from ..services.export_service import export_service
from ..services.import_service import import_service
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1", tags=["export-import"])


# Export endpoints
@router.get("/export/markdown/{note_id}")
async def export_note_markdown(
    note_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export a single note as Markdown"""
    try:
        user_id = UUID(current_user["sub"])
        content = await export_service.export_note_markdown(note_id, user_id)
        filename = await export_service.get_export_filename(note_id, user_id, "md")
        
        return Response(
            content=content.encode('utf-8'),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/txt/{note_id}")
async def export_note_txt(
    note_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export a single note as plain text"""
    try:
        user_id = UUID(current_user["sub"])
        content = await export_service.export_note_txt(note_id, user_id)
        filename = await export_service.get_export_filename(note_id, user_id, "txt")
        
        return Response(
            content=content.encode('utf-8'),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/pdf/{note_id}")
async def export_note_pdf(
    note_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export a single note as PDF"""
    try:
        user_id = UUID(current_user["sub"])
        content = await export_service.export_note_pdf(note_id, user_id)
        filename = await export_service.get_export_filename(note_id, user_id, "pdf")
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/bulk")
async def export_notes_bulk(
    note_ids: List[UUID],
    format: str = Query(..., regex="^(markdown|txt)$"),
    current_user: dict = Depends(get_current_user)
):
    """Export multiple notes as a single file"""
    try:
        user_id = UUID(current_user["sub"])
        
        if format == "markdown":
            content = await export_service.export_notes_bulk_markdown(note_ids, user_id)
            media_type = "text/markdown"
            extension = "md"
        elif format == "txt":
            content = await export_service.export_notes_bulk_txt(note_ids, user_id)
            media_type = "text/plain"
            extension = "txt"
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        filename = await export_service.get_bulk_export_filename(extension, len(note_ids))
        
        return Response(
            content=content.encode('utf-8'),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import endpoints
@router.post("/import/file")
async def import_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Import notes from a file"""
    try:
        user_id = UUID(current_user["sub"])
        
        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        result = await import_service.import_file(file, user_id)
        
        if result["success"]:
            return JSONResponse(
                content={
                    "message": f"Successfully imported {result['imported_count']} out of {result['total_count']} notes",
                    "imported_count": result["imported_count"],
                    "total_count": result["total_count"],
                    "notes": [note.model_dump() for note in result["notes"]],
                    "errors": result["errors"]
                },
                status_code=200 if not result["errors"] else 207  # 207 = Multi-Status
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/import/formats")
async def get_supported_formats():
    """Get list of supported import formats"""
    try:
        formats = await import_service.get_supported_formats()
        return {"supported_formats": formats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/validate")
async def validate_import_data(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Validate import file without actually importing"""
    try:
        user_id = UUID(current_user["sub"])
        
        # Validate file size
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        # Get the import data without creating notes
        result = await import_service.import_file(file, user_id)
        
        if result["success"]:
            return {
                "valid": True,
                "total_notes": result["total_count"],
                "preview": result["notes"][:5],  # Show first 5 notes as preview
                "errors": result["errors"]
            }
        else:
            return {
                "valid": False,
                "error": result["error"],
                "total_notes": 0,
                "preview": [],
                "errors": result["errors"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@router.get("/export/formats")
async def get_export_formats():
    """Get list of supported export formats"""
    return {
        "single_note_formats": ["markdown", "txt", "pdf"],
        "bulk_formats": ["markdown", "txt"],
        "descriptions": {
            "markdown": "Markdown format (.md) - preserves formatting",
            "txt": "Plain text format (.txt) - simple text only",
            "pdf": "PDF format (.pdf) - formatted document (single notes only)"
        }
    }