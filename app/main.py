from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import text_operations
from .models.requests import TextRequest, TextResponse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import process_command
from .utils.diff_utils import get_diff

app = FastAPI(
    title="ChatNotePad.Ai Backend",
    description="Multi-agent text processing API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(text_operations.router)

@app.post("/prompt", response_model=TextResponse)
async def legacy_prompt(request: TextRequest):
    """Legacy endpoint for backward compatibility"""
    try:
        result = process_command(request.text, request.command)
        diff = get_diff(request.text, result)
        return TextResponse(
            result=result,
            success=True,
            agent_used="legacy",
            diff=diff
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize", response_model=TextResponse)
async def legacy_summarize(request: TextRequest):
    """Legacy endpoint that redirects to new summarizer agent"""
    from .core.agent_manager import AgentManager
    try:
        agent_manager = AgentManager()
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

@app.get("/")
async def root():
    return {"message": "ChatNotePad.Ai Backend API", "version": "2.0.0"}