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