from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str
    command: str

class TextResponse(BaseModel):
    result: str
    success: bool = True
    agent_used: str = ""
    diff: str = ""