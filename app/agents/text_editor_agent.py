import re
from .base_agent import BaseAgent
from ..services.llm_service import LLMService
from typing import Dict, Any
import time
from datetime import datetime

class TextEditorAgent(BaseAgent):
    def __init__(self, name: str = "text_editor"):
        super().__init__(name)
        self.llm_service = LLMService()

    def remove_char(self, text: str, char: str) -> str:
        return text.replace(char, "")

    def replace_word(self, text: str, old: str, new: str) -> str:
        return re.sub(rf'\b{re.escape(old)}\b', new, text)

    def capitalize_sentences(self, text: str) -> str:
        return re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

    async def process(self, text: str, command: str) -> Dict[str, Any]:
        if self.llm_service.should_use_llm(command):
            return self.llm_service.process_complex_command(text, command)
        
        start_time = time.time()
        command_lower = command.lower()
        result = text  # Default result
        
        if "uppercase" in command_lower or "convert to uppercase" in command_lower:
            result = text.upper()
        elif "lowercase" in command_lower or "convert to lowercase" in command_lower:
            result = text.lower()
        elif "remove" in command_lower and "," in command_lower:
            result = self.remove_char(text, ",")
        elif "replace" in command_lower and "with" in command_lower:
            match = re.search(r"replace '(.*?)' with '(.*?)'", command)
            if match:
                old, new = match.group(1), match.group(2)
                result = self.replace_word(text, old, new)
        elif "capitalize" in command_lower and "sentence" in command_lower:
            result = self.capitalize_sentences(text)
        
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        return {
            "result": result,
            "agent_info": {
                "model": "rule-based",
                "processing_time_ms": processing_time_ms,
                "tokens_used": None,
                "confidence_score": 1.0 if result != text else 0.5,
                "timestamp": datetime.now().isoformat()
            }
        }