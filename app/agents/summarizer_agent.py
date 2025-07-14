from .base_agent import BaseAgent
from ..services.llm_service import LLMService
from typing import Dict, Any
import time
from datetime import datetime

class SummarizerAgent(BaseAgent):
    def __init__(self, name: str = "summarizer"):
        super().__init__(name)
        self.llm_service = LLMService()

    async def process(self, text: str, command: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            system_prompt = """You are a text summarization specialist. Your task is to create concise, accurate summaries of the provided text.

Rules:
- Create clear, well-structured summaries
- Preserve key information and main points
- Maintain the original tone and context
- Return ONLY the summary, no additional explanations
- If the text is already very short, provide a brief condensed version
- Handle different types of content: articles, emails, documents, notes, etc.

Examples of summarization styles based on command:
- "summarize" → Standard summary (3-5 sentences)
- "brief summary" → Very short summary (1-2 sentences)
- "detailed summary" → More comprehensive summary with key points
- "bullet points" → Summary in bullet point format
- "executive summary" → Business-style executive summary"""

            # Determine summarization style based on command
            if "brief" in command.lower() or "short" in command.lower():
                user_prompt = f"Create a brief 1-2 sentence summary of this text:\n\n{text}"
            elif "detailed" in command.lower() or "comprehensive" in command.lower():
                user_prompt = f"Create a detailed summary with key points from this text:\n\n{text}"
            elif "bullet" in command.lower() or "points" in command.lower():
                user_prompt = f"Summarize this text in bullet point format:\n\n{text}"
            elif "executive" in command.lower():
                user_prompt = f"Create an executive summary of this text:\n\n{text}"
            else:
                user_prompt = f"Summarize this text in 3-5 clear sentences:\n\n{text}"

            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
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
                    "model": self.llm_service.model,
                    "processing_time_ms": processing_time_ms,
                    "tokens_used": tokens_used,
                    "confidence_score": 0.95,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            end_time = time.time()
            processing_time_ms = int((end_time - start_time) * 1000)
            
            self.logger.error(f"Summarization failed: {e}")
            return {
                "result": f"Error: Unable to summarize text - {str(e)}",
                "agent_info": {
                    "model": self.llm_service.model,
                    "processing_time_ms": processing_time_ms,
                    "tokens_used": None,
                    "confidence_score": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
            }