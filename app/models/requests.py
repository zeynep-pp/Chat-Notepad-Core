from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class TextRequest(BaseModel):
    text: str
    command: str

class AgentInfo(BaseModel):
    model: str
    processing_time_ms: int
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    timestamp: str
    transformation_type: Optional[str] = None

class TextResponse(BaseModel):
    result: str
    success: bool = True
    agent_used: str = ""
    diff: str = ""
    agent_info: Optional[AgentInfo] = None

# Note Management Models
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")
    is_favorite: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None

class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: str
    is_favorite: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    user_id: UUID

class NoteListResponse(BaseModel):
    notes: List[NoteResponse]
    total: int
    page: int
    per_page: int
    pages: int

class NoteSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class TagsResponse(BaseModel):
    tags: List[str]
    total: int

# Version History Models
class NoteVersionResponse(BaseModel):
    id: UUID
    note_id: UUID
    version_number: int
    content: str
    change_description: Optional[str] = None
    created_at: datetime
    user_id: UUID

class NoteVersionCreate(BaseModel):
    change_description: Optional[str] = None

class NoteVersionsListResponse(BaseModel):
    versions: List[NoteVersionResponse]
    total: int
    note_id: UUID

class NoteDiffResponse(BaseModel):
    note_id: UUID
    version1: int
    version2: int
    diff_html: str
    diff_text: str

# Command History Models
class CommandHistoryResponse(BaseModel):
    id: UUID
    command: str
    input_text: str
    output_text: Optional[str] = None
    agent_used: Optional[str] = None
    success: bool
    processing_time_ms: Optional[int] = None
    created_at: datetime

class CommandHistoryListResponse(BaseModel):
    commands: List[CommandHistoryResponse]
    total: int
    page: int
    per_page: int
    pages: int

class CommandStatsResponse(BaseModel):
    total_commands: int
    success_rate: float
    most_used_commands: List[dict]
    avg_processing_time: Optional[float] = None

# AI Suggestions Models
class SuggestionRequest(BaseModel):
    context: str
    text: str
    cursor_position: int
    context_type: str = Field(default="content", pattern="^(content|command|style)$")

class SuggestionResponse(BaseModel):
    suggestions: List[str]
    context_type: str
    confidence: float

# Translation Models
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

# Style Improvement Models
class StyleImprovementRequest(BaseModel):
    text: str
    context: str
    cursor_position: int

class StyleImprovementResponse(BaseModel):
    improved_text: str
    original_text: str
    suggestions: List[str]
    confidence: float

# Quick Summary Models
class QuickSummaryRequest(BaseModel):
    text: str
    max_length: int = Field(default=100, ge=10, le=500)

class QuickSummaryResponse(BaseModel):
    summary: str
    original_text: str
    original_length: int
    summary_length: int
    compression_ratio: float

# Text Expansion Models
class TextExpansionRequest(BaseModel):
    text: str
    context: str

class TextExpansionResponse(BaseModel):
    expanded_text: str
    original_text: str
    context: str
    expansion_ratio: float