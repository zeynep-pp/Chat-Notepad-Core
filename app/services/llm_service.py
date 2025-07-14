import openai
from typing import Optional, Dict, Any
from ..config.config import Config
import time
from datetime import datetime


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.OpenAI(
            api_key=api_key or Config.OPENAI_API_KEY
        )
        self.model = Config.OPENAI_MODEL
    
    def process_complex_command(self, text: str, command: str) -> Dict[str, Any]:
        """
        Process complex commands using GPT-4.1 for context-aware text manipulation
        Returns both the result and metadata for agent_info
        """
        start_time = time.time()
        
        try:
            system_prompt = """You are a text processing assistant. Given a text and a command, apply the command to transform the text.
            
Rules:
- Return ONLY the transformed text, no explanations
- Preserve formatting unless specifically requested to change it
- Handle complex natural language commands intelligently
- If the command is unclear or cannot be applied, return the original text unchanged

Examples:
- "make it more formal" → rewrite in formal tone
- "fix grammar" → correct grammatical errors
- "summarize" → create a concise summary
- "translate to spanish" → translate the text
- "make it sound like shakespeare" → rewrite in Shakespearean style"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Text: {text}\n\nCommand: {command}"}
                ],
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=Config.OPENAI_MAX_TOKENS
            )
            
            end_time = time.time()
            processing_time_ms = int((end_time - start_time) * 1000)
            
            content = response.choices[0].message.content
            result = content.strip() if content else text
            
            # Extract usage information if available
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
            
            return {
                "result": result,
                "agent_info": {
                    "model": self.model,
                    "processing_time_ms": processing_time_ms,
                    "tokens_used": tokens_used,
                    "confidence_score": 0.95,  # Default confidence for successful processing
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            end_time = time.time()
            processing_time_ms = int((end_time - start_time) * 1000)
            
            print(f"LLM processing error: {e}")
            return {
                "result": text,  # Return original text on error
                "agent_info": {
                    "model": self.model,
                    "processing_time_ms": processing_time_ms,
                    "tokens_used": None,
                    "confidence_score": 0.0,  # Low confidence for errors
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def should_use_llm(self, command: str) -> bool:
        """
        Determine if command should use LLM processing
        Most commands should use LLM for flexibility
        """
        command_lower = command.lower().strip()
        
        # Only very basic commands bypass LLM
        basic_patterns = [
            "remove ,",
            "remove comma", 
            "remove commas"
        ]
        
        # Check for exact basic patterns
        for pattern in basic_patterns:
            if command_lower == pattern or command_lower == pattern + "s":
                return False
        
        # Everything else uses LLM for maximum flexibility
        return True