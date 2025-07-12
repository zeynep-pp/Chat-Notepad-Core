from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_command
from diff_utils import get_diff

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    text: str
    command: str

class PromptResponse(BaseModel):
    result: str
    diff: str

@app.get("/")
async def root():
    return {"message": "Chat Notepad Core AI API", "status": "running"}

@app.post("/prompt", response_model=PromptResponse)
async def prompt_endpoint(req: PromptRequest):
    result = process_command(req.text, req.command)
    diff = get_diff(req.text, result)
    return {"result": result, "diff": diff}
