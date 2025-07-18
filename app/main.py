from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import text_operations, auth
from .models.requests import TextRequest, TextResponse, AgentInfo
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Successfully loaded .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"Error loading .env file: {e}")

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

# Add error handling for auth router
try:
    app.include_router(auth.router)
    logger.info("✅ Auth router loaded successfully")
    logger.info(f"🔧 Auth router prefix: {auth.router.prefix}")
    logger.info(f"🔧 Auth router routes: {len(auth.router.routes)}")
except Exception as e:
    logger.error(f"❌ Failed to load auth router: {e}")
    import traceback
    logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    raise

@app.post("/prompt", response_model=TextResponse)
async def legacy_prompt(request: TextRequest):
    """Legacy endpoint for backward compatibility"""
    try:
        print(f"Processing request: text='{request.text}', command='{request.command}'")
        command_result = process_command(request.text, request.command)
        result = command_result["result"]
        agent_info = command_result["agent_info"]
        
        diff = get_diff(request.text, result)
        return TextResponse(
            result=result,
            success=True,
            agent_used="legacy",
            diff=diff,
            agent_info=AgentInfo(**agent_info)
        )
    except Exception as e:
        import traceback
        error_msg = f"Error processing command: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

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
            diff=diff,
            agent_info=AgentInfo(**result["agent_info"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "ChatNotePad.Ai Backend API", "version": "2.0.0"}