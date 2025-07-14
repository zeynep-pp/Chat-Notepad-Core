from pydantic import BaseModel
from typing import Optional

class TextRequest(BaseModel):
    text: str
    command: str

class AgentInfo(BaseModel):
    model: str
    processing_time_ms: int
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    timestamp: str

class TextResponse(BaseModel):
    result: str
    success: bool = True
    agent_used: str = ""
    diff: str = ""
    agent_info: Optional[AgentInfo] = None