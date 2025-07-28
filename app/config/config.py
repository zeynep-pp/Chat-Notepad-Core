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
    
    # Redis Configuration
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Google Services
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    
    # Dropbox Configuration
    DROPBOX_APP_KEY: Optional[str] = os.getenv("DROPBOX_APP_KEY")
    DROPBOX_APP_SECRET: Optional[str] = os.getenv("DROPBOX_APP_SECRET")
    
    # Feature Flags
    ENABLE_VERSIONING: bool = os.getenv("ENABLE_VERSIONING", "true").lower() == "true"
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    ENABLE_AI_SUGGESTIONS: bool = os.getenv("ENABLE_AI_SUGGESTIONS", "true").lower() == "true"
    ENABLE_TRANSLATION: bool = os.getenv("ENABLE_TRANSLATION", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if cls.ENABLE_LLM and not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set but LLM is enabled")
            return False
        return True

# Global settings instance
settings = Config()