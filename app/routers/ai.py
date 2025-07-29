from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.middleware.auth_middleware import get_current_user
from app.services.suggestion_service import SuggestionService
from app.services.translation_service import TranslationService
from app.services.rate_limit_service import rate_limit
from app.models.requests import (
    SuggestionRequest,
    SuggestionResponse,
    TranslationRequest,
    TranslationResponse,
    StyleImprovementRequest,
    StyleImprovementResponse,
    QuickSummaryRequest,
    QuickSummaryResponse
)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])
suggestion_service = SuggestionService()
translation_service = TranslationService()

@router.post("/suggest", response_model=SuggestionResponse)
@rate_limit(max_requests=50, window_seconds=3600)  # 50 requests per hour
async def get_suggestions(
    request: SuggestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered suggestions based on context."""
    try:
        user_id = UUID(current_user["id"])
        return await suggestion_service.get_suggestions(user_id, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/suggest/stats")
async def get_suggestion_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get user's suggestion usage statistics."""
    try:
        user_id = UUID(current_user["id"])
        return await suggestion_service.get_user_suggestion_stats(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/translate", response_model=TranslationResponse)
@rate_limit(max_requests=200, window_seconds=3600)  # 200 requests per hour
async def translate_text(
    request: TranslationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Translate text to target language."""
    try:
        # Check if target language is supported
        if not translation_service.is_language_supported(request.target_language):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{request.target_language}' is not supported"
            )
        
        return await translation_service.translate_text(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/translate/batch", response_model=List[TranslationResponse])
@rate_limit(max_requests=20, window_seconds=3600)  # 20 batch requests per hour
async def translate_multiple_texts(
    texts: List[str],
    target_language: str,
    source_language: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Translate multiple texts at once."""
    try:
        if len(texts) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 texts can be translated in one batch"
            )
        
        if not translation_service.is_language_supported(target_language):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{target_language}' is not supported"
            )
        
        return await translation_service.translate_multiple(
            texts=texts,
            target_language=target_language,
            source_language=source_language
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/detect-language")
async def detect_language(
    text: str,
    current_user: dict = Depends(get_current_user)
):
    """Detect the language of the given text."""
    try:
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        return await translation_service.detect_language(text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation."""
    try:
        languages = translation_service.get_supported_languages()
        return {
            "languages": languages,
            "total": len(languages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/improve-style", response_model=StyleImprovementResponse)
@rate_limit(max_requests=100, window_seconds=3600)  # 100 requests per hour
async def improve_style(
    request: StyleImprovementRequest,
    current_user: dict = Depends(get_current_user)
):
    """Improve the style and quality of the given text."""
    try:
        user_id = UUID(current_user["id"])
        
        # Create a basic style improvement response
        # This is a placeholder implementation - you would integrate with an AI service
        improved_text = request.text  # Placeholder - should be improved by AI
        suggestions = [
            "Consider using more active voice",
            "Break long sentences into shorter ones",
            "Use more specific vocabulary"
        ]
        
        return StyleImprovementResponse(
            improved_text=improved_text,
            original_text=request.text,
            suggestions=suggestions,
            confidence=0.85
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/quick-summary", response_model=QuickSummaryResponse)
@rate_limit(max_requests=150, window_seconds=3600)  # 150 requests per hour
async def quick_summary(
    request: QuickSummaryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a quick summary of the given text."""
    try:
        user_id = UUID(current_user["id"])
        
        # Basic text truncation for now - should be replaced with AI summarization
        original_length = len(request.text)
        words = request.text.split()
        
        # Simple summary by taking first portion of text up to max_length
        if len(request.text) <= request.max_length:
            summary = request.text
        else:
            # Find a good cutoff point near max_length
            summary = request.text[:request.max_length]
            # Try to end at a sentence boundary
            last_period = summary.rfind('.')
            last_exclamation = summary.rfind('!')
            last_question = summary.rfind('?')
            last_sentence_end = max(last_period, last_exclamation, last_question)
            
            if last_sentence_end > request.max_length * 0.7:  # If we found a good ending point
                summary = summary[:last_sentence_end + 1]
            else:
                summary = summary.rstrip() + "..."
        
        summary_length = len(summary)
        compression_ratio = summary_length / original_length if original_length > 0 else 1.0
        
        return QuickSummaryResponse(
            summary=summary,
            original_text=request.text,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/translate/note/{note_id}")
@rate_limit(max_requests=20, window_seconds=3600)
async def translate_note_content(
    note_id: UUID,
    target_language: str,
    preserve_formatting: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Translate entire note content to target language."""
    try:
        user_id = UUID(current_user["id"])
        
        # Get the note first
        from app.services.note_service import NoteService
        note_service = NoteService()
        note = await note_service.get_note(user_id, note_id)
        
        if not translation_service.is_language_supported(target_language):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{target_language}' is not supported"
            )
        
        # Translate the content
        translated_content = await translation_service.auto_translate_note_content(
            content=note.content,
            target_language=target_language,
            preserve_formatting=preserve_formatting
        )
        
        # Optionally save as a new note or return the translation
        return {
            "note_id": note_id,
            "original_title": note.title,
            "original_content": note.content,
            "translated_content": translated_content,
            "target_language": target_language,
            "language_name": translation_service.get_language_name(target_language)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )