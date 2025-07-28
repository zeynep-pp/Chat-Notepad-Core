from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from uuid import UUID
import time
from ..models.requests import TextRequest, TextResponse, AgentInfo
from ..core.agent_manager import AgentManager
from ..utils.diff_utils import get_diff
from ..middleware.auth_middleware import get_current_user, get_optional_user
from ..services.history_service import HistoryService

router = APIRouter(prefix="/api/v1", tags=["text"])

async def get_agent_manager() -> AgentManager:
    return AgentManager()

async def log_command_execution(
    user_id: UUID,
    command: str,
    input_text: str,
    output_text: str,
    agent_used: str,
    success: bool,
    processing_time_ms: int
):
    """Log command execution to history"""
    try:
        history_service = HistoryService()
        await history_service.log_command(
            user_id=user_id,
            command=command,
            input_text=input_text,
            output_text=output_text,
            agent_used=agent_used,
            success=success,
            processing_time_ms=processing_time_ms
        )
    except Exception as e:
        # Don't fail the operation if logging fails
        print(f"Warning: Failed to log command execution: {str(e)}")

@router.post("/prompt", response_model=TextResponse)
async def process_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    start_time = time.time()
    success = False
    result_text = ""
    agent_used = "editor"
    
    try:
        result = await agent_manager.execute("editor", request.text, request.command)
        success = result["success"]
        result_text = result["result"]
        agent_used = result["agent_used"]
        
        diff = get_diff(request.text, result_text)
        
        # Log command execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=result_text,
            agent_used=agent_used,
            success=success,
            processing_time_ms=processing_time_ms
        )
        
        return TextResponse(
            result=result_text,
            success=success,
            agent_used=agent_used,
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    except Exception as e:
        # Log failed execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=str(e),
            agent_used=agent_used,
            success=False,
            processing_time_ms=processing_time_ms
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize", response_model=TextResponse)
async def summarize_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    start_time = time.time()
    success = False
    result_text = ""
    agent_used = "summarizer"
    
    try:
        result = await agent_manager.execute("summarizer", request.text, request.command)
        success = result["success"]
        result_text = result["result"]
        agent_used = result["agent_used"]
        
        diff = get_diff(request.text, result_text)
        
        # Log command execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=result_text,
            agent_used=agent_used,
            success=success,
            processing_time_ms=processing_time_ms
        )
        
        return TextResponse(
            result=result_text,
            success=success,
            agent_used=agent_used,
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    except Exception as e:
        # Log failed execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=str(e),
            agent_used=agent_used,
            success=False,
            processing_time_ms=processing_time_ms
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transform", response_model=TextResponse)
async def transform_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Advanced text transformation endpoint supporting:
    - Tone shift (formal ↔ casual, professional ↔ friendly)
    - Simplification (complex → simple, technical → layman)
    - Formalization (casual → formal, informal → professional)
    """
    start_time = time.time()
    success = False
    result_text = ""
    agent_used = "transformer"
    
    try:
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if not request.command or not request.command.strip():
            raise HTTPException(status_code=400, detail="Command cannot be empty")
        
        # Check text length limits
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long (max 10,000 characters)")
        
        if len(request.command) > 500:
            raise HTTPException(status_code=400, detail="Command too long (max 500 characters)")
        
        # Execute transformation using the transformer agent
        result = await agent_manager.execute("transformer", request.text, request.command)
        success = result["success"]
        result_text = result["result"]
        agent_used = result["agent_used"]
        
        # Generate diff for comparison
        diff = get_diff(request.text, result_text)
        
        # Log command execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=result_text,
            agent_used=agent_used,
            success=success,
            processing_time_ms=processing_time_ms
        )
        
        return TextResponse(
            result=result_text,
            success=success,
            agent_used=agent_used,
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    
    except HTTPException as he:
        # Log failed execution for HTTP exceptions
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=str(he.detail),
            agent_used=agent_used,
            success=False,
            processing_time_ms=processing_time_ms
        )
        raise
    except Exception as e:
        # Log failed execution
        processing_time_ms = int((time.time() - start_time) * 1000)
        await log_command_execution(
            user_id=UUID(current_user["id"]),
            command=request.command,
            input_text=request.text,
            output_text=str(e),
            agent_used=agent_used,
            success=False,
            processing_time_ms=processing_time_ms
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/agents")
async def list_agents(
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    # Public endpoint, authentication optional
    return {"agents": agent_manager.get_available_agents()}