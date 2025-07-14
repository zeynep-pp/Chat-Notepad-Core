import re
import time
from datetime import datetime
from app.services.llm_service import LLMService

# Initialize LLM service
llm_service = LLMService()

def remove_char(text: str, char: str) -> str:
    return text.replace(char, "")

def replace_word(text: str, old: str, new: str) -> str:
    return re.sub(rf'\b{re.escape(old)}\b', new, text)

def capitalize_sentences(text: str) -> str:
    # Capitalize the first letter of each sentence
    return re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

def process_command(text: str, command: str) -> dict:
    # Check if we should use LLM for complex processing
    if llm_service.should_use_llm(command):
        return llm_service.process_complex_command(text, command)
    
    # Fall back to simple rule-based command parsing with timing
    start_time = time.time()
    command_lower = command.lower()
    result = text  # Default result
    
    # Handle basic text transformations
    if "uppercase" in command_lower or "convert to uppercase" in command_lower:
        result = text.upper()
    elif "lowercase" in command_lower or "convert to lowercase" in command_lower:
        result = text.lower()
    elif "remove" in command_lower and "," in command_lower:
        result = remove_char(text, ",")
    elif "replace" in command_lower and "with" in command_lower:
        # Example: Replace 've' with 'ile'
        import re
        match = re.search(r"replace '(.*?)' with '(.*?)'", command)
        if match:
            old, new = match.group(1), match.group(2)
            result = replace_word(text, old, new)
    elif "capitalize" in command_lower and "sentence" in command_lower:
        result = capitalize_sentences(text)
    
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