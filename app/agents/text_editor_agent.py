import re
from .base_agent import BaseAgent
from ..services.llm_service import LLMService

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

    async def process(self, text: str, command: str) -> str:
        if self.llm_service.should_use_llm(command):
            return self.llm_service.process_complex_command(text, command)
        
        command_lower = command.lower()
        
        if "uppercase" in command_lower or "convert to uppercase" in command_lower:
            return text.upper()
        if "lowercase" in command_lower or "convert to lowercase" in command_lower:
            return text.lower()
        if "remove" in command_lower and "," in command_lower:
            return self.remove_char(text, ",")
        if "replace" in command_lower and "with" in command_lower:
            match = re.search(r"replace '(.*?)' with '(.*?)'", command)
            if match:
                old, new = match.group(1), match.group(2)
                return self.replace_word(text, old, new)
        if "capitalize" in command_lower and "sentence" in command_lower:
            return self.capitalize_sentences(text)
        
        return text