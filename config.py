import os
from typing import Optional

class Config:
    """Configuration settings for the Chat-Notepad-Core.AI application"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    # Application Settings
    ENABLE_LLM: bool = os.getenv("ENABLE_LLM", "true").lower() == "true"
    FALLBACK_TO_RULES: bool = os.getenv("FALLBACK_TO_RULES", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if cls.ENABLE_LLM and not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set but LLM is enabled")
            return False
        return True