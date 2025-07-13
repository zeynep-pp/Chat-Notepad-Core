from fastapi import APIRouter, HTTPException, Depends
from ..models.requests import TextRequest, TextResponse
from ..core.agent_manager import AgentManager
from diff_utils import get_diff

router = APIRouter(prefix="/api/v1", tags=["text"])

async def get_agent_manager() -> AgentManager:
    return AgentManager()

@router.post("/prompt", response_model=TextResponse)
async def process_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    try:
        result = await agent_manager.execute("editor", request.text, request.command)
        diff = get_diff(request.text, result["result"])
        return TextResponse(
            result=result["result"],
            success=result["success"],
            agent_used=result["agent_used"],
            diff=diff
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize", response_model=TextResponse)
async def summarize_text(
    request: TextRequest,
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    try:
        result = await agent_manager.execute("summarizer", request.text, request.command)
        diff = get_diff(request.text, result["result"])
        return TextResponse(
            result=result["result"],
            success=result["success"],
            agent_used=result["agent_used"],
            diff=diff
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def list_agents(agent_manager: AgentManager = Depends(get_agent_manager)):
    return {"agents": agent_manager.get_available_agents()}