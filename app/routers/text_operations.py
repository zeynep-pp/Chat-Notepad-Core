from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from ..models.requests import TextRequest, TextResponse, AgentInfo
from ..core.agent_manager import AgentManager
from ..utils.diff_utils import get_diff
from ..middleware.auth_middleware import get_current_user, get_optional_user

router = APIRouter(prefix="/api/v1", tags=["text"])

async def get_agent_manager() -> AgentManager:
    return AgentManager()

@router.post("/prompt", response_model=TextResponse)
async def process_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        result = await agent_manager.execute("editor", request.text, request.command)
        diff = get_diff(request.text, result["result"])
        return TextResponse(
            result=result["result"],
            success=result["success"],
            agent_used=result["agent_used"],
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize", response_model=TextResponse)
async def summarize_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        result = await agent_manager.execute("summarizer", request.text, request.command)
        diff = get_diff(request.text, result["result"])
        return TextResponse(
            result=result["result"],
            success=result["success"],
            agent_used=result["agent_used"],
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    except Exception as e:
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
        
        # Generate diff for comparison
        diff = get_diff(request.text, result["result"])
        
        return TextResponse(
            result=result["result"],
            success=result["success"],
            agent_used=result["agent_used"],
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/agents")
async def list_agents(
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    # Public endpoint, authentication optional
    return {"agents": agent_manager.get_available_agents()}