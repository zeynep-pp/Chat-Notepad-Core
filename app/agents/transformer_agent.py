import re
from .base_agent import BaseAgent
from ..services.llm_service import LLMService
from typing import Dict, Any, Optional
import time
from datetime import datetime


class TransformerAgent(BaseAgent):
    """
    Specialized agent for advanced text transformations including:
    - Tone shift (formal ↔ casual, professional ↔ friendly)
    - Simplification (complex → simple, technical → layman)
    - Formalization (casual → formal, informal → professional)
    
    🔮 PHASE 2 ROADMAP - Advanced Transformation Features:
    
    📝 Content Enhancement:
    - ⬜️ Length adjustment (expand/condense while maintaining meaning)
    - ⬜️ Readability optimization (Flesch-Kincaid score targeting)
    - ⬜️ Audience adaptation (technical → general, adult → child-friendly)
    - ⬜️ Emotion injection (add enthusiasm, urgency, empathy)
    - ⬜️ Perspective shifting (first → third person, active → passive voice)
    
    🌍 Language & Localization:
    - ⬜️ Cultural adaptation (US → UK English, regional expressions)
    - ⬜️ Industry-specific terminology (legal, medical, technical jargon)
    - ⬜️ Brand voice consistency (match company style guides)
    - ⬜️ Accessibility improvements (plain language, screen reader friendly)
    
    🤖 AI-Powered Intelligence:
    - ⬜️ Context-aware transformations (preserve document structure)
    - ⬜️ Multi-step transformation chains (casual → formal → technical)
    - ⬜️ Confidence scoring per transformation type
    - ⬜️ Suggestion alternatives (provide multiple transformation options)
    - ⬜️ Undo/redo transformation history
    
    📊 Analytics & Optimization:
    - ⬜️ Transformation success metrics tracking
    - ⬜️ Popular transformation patterns analysis
    - ⬜️ Performance optimization for batch processing
    - ⬜️ Custom transformation pattern learning
    - ⬜️ A/B testing for prompt effectiveness
    
    🛠️ Advanced Features:
    - ⬜️ Batch transformation (multiple texts at once)
    - ⬜️ Template-based transformations (emails, reports, proposals)
    - ⬜️ Integration with grammar/spell checkers
    - ⬜️ Custom transformation rules engine
    - ⬜️ Real-time transformation preview
    
    💻 Developer Experience:
    - ⬜️ Transformation plugins system
    - ⬜️ Custom prompt templates
    - ⬜️ Webhook notifications for completed transformations
    - ⬜️ GraphQL API for complex queries
    - ⬜️ Streaming responses for large texts
    """
    
    def __init__(self, name: str = "text_transformer"):
        super().__init__(name)
        self.llm_service = LLMService()
        
    def detect_transformation_type(self, command: str) -> Optional[str]:
        """
        Detect the type of transformation based on command keywords
        Returns: 'formalization', 'simplification', 'tone_shift', or None
        """
        if not command:
            return None
            
        command_lower = command.lower().strip()
        
        # Formalization keywords
        formal_keywords = [
            'formal', 'formalize', 'professional', 'business', 'official',
            'academic', 'proper', 'correct', 'standard', 'polite'
        ]
        
        # Simplification keywords
        simple_keywords = [
            'simplify', 'simple', 'simpler', 'easier', 'easy', 'beginner',
            'basic', 'plain', 'layman', 'explain', 'understand', 'clear'
        ]
        
        # Tone shift keywords
        tone_keywords = [
            'tone', 'casual', 'friendly', 'warm', 'conversational',
            'informal', 'relax', 'approachable', 'personal', 'human'
        ]
        
        # Check for formalization
        if any(keyword in command_lower for keyword in formal_keywords):
            return 'formalization'
        
        # Check for simplification
        if any(keyword in command_lower for keyword in simple_keywords):
            return 'simplification'
        
        # Check for tone shift
        if any(keyword in command_lower for keyword in tone_keywords):
            return 'tone_shift'
        
        return None
    
    def get_transformation_prompt(self, transformation_type: str, command: str) -> str:
        """
        Get specialized prompt for each transformation type
        """
        base_rules = """
Rules:
- Return ONLY the transformed text, no explanations or comments
- Preserve the original meaning and key information
- Maintain appropriate length unless specifically requested to change it
- If transformation is unclear or inappropriate, return original text unchanged
        """
        
        if transformation_type == 'formalization':
            return f"""You are a professional text formalization expert. Transform the given text to be more formal and professional.

{base_rules}

Formalization guidelines:
- Use formal language and professional terminology
- Replace casual expressions with formal equivalents
- Use complete sentences and proper grammar
- Avoid contractions, slang, and informal expressions
- Use third person perspective where appropriate
- Maintain respectful and courteous tone
- Use precise and specific language

Examples:
- "hey there" → "Good morning" or "Dear [Name]"
- "can't" → "cannot"
- "gonna" → "going to"
- "kinda" → "somewhat"
- "stuff" → "materials" or "items"
"""
        
        elif transformation_type == 'simplification':
            return f"""You are a text simplification expert. Transform the given text to be simpler and more accessible.

{base_rules}

Simplification guidelines:
- Use simple, common words instead of complex vocabulary
- Break down complex sentences into shorter ones
- Replace technical jargon with everyday language
- Use active voice instead of passive voice
- Explain concepts in layman's terms
- Use examples and analogies when helpful
- Maintain clarity and readability

Examples:
- "utilize" → "use"
- "demonstrate" → "show"
- "facilitate" → "help"
- "subsequently" → "then"
- "aforementioned" → "mentioned before"
"""
        
        elif transformation_type == 'tone_shift':
            return f"""You are a tone adjustment expert. Transform the given text to have a more casual, friendly, and approachable tone.

{base_rules}

Tone shift guidelines:
- Use conversational and friendly language
- Add warmth and personality to the text
- Use contractions naturally ("you're", "it's", "we'll")
- Include friendly expressions and transitional phrases
- Make it sound more human and relatable
- Use inclusive language ("we", "us", "our")
- Add appropriate enthusiasm where suitable

Examples:
- "Please be advised" → "Just wanted to let you know"
- "It is recommended" → "We'd suggest" or "You might want to"
- "Upon completion" → "Once you're done"
- "In accordance with" → "Following" or "Based on"
"""
        
        else:
            command_text = command if command else "general transformation"
            return f"""You are a text transformation assistant. Apply the following command to transform the text: {command_text}

{base_rules}

Apply the transformation as requested while maintaining the original meaning and context.
"""
    
    async def process(self, text: str, command: str) -> Dict[str, Any]:
        """
        Process text transformation with specialized handling for different types
        """
        start_time = time.time()
        
        # Detect transformation type
        transformation_type = self.detect_transformation_type(command)
        
        if transformation_type:
            # Use specialized prompt for detected transformation type
            system_prompt = self.get_transformation_prompt(transformation_type, command)
            
            try:
                response = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Text: {text}\n\nCommand: {command}"}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent transformations
                    max_tokens=1500
                )
                
                end_time = time.time()
                processing_time_ms = int((end_time - start_time) * 1000)
                
                content = response.choices[0].message.content
                result = content.strip() if content and content.strip() else text
                
                # Extract usage information
                tokens_used = None
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = response.usage.total_tokens
                
                return {
                    "result": result,
                    "agent_info": {
                        "model": "text-transformation-agent",
                        "processing_time_ms": processing_time_ms,
                        "tokens_used": tokens_used,
                        "confidence_score": 0.95,
                        "timestamp": datetime.now().isoformat(),
                        "transformation_type": transformation_type
                    }
                }
                
            except Exception as e:
                end_time = time.time()
                processing_time_ms = int((end_time - start_time) * 1000)
                
                print(f"Transformation error: {e}")
                return {
                    "result": text,
                    "agent_info": {
                        "model": "text-transformation-agent",
                        "processing_time_ms": processing_time_ms,
                        "tokens_used": None,
                        "confidence_score": 0.0,
                        "timestamp": datetime.now().isoformat(),
                        "transformation_type": transformation_type
                    }
                }
        
        else:
            # Fall back to general LLM processing for unrecognized commands
            try:
                result = self.llm_service.process_complex_command(text, command)
                
                # Update agent info to reflect transformer agent usage
                if result.get("agent_info"):
                    result["agent_info"]["model"] = "text-transformation-agent"
                    result["agent_info"]["transformation_type"] = "general"
                
                return result
            except Exception as e:
                end_time = time.time()
                processing_time_ms = int((end_time - start_time) * 1000)
                
                print(f"LLM service fallback error: {e}")
                return {
                    "result": text,
                    "agent_info": {
                        "model": "text-transformation-agent",
                        "processing_time_ms": processing_time_ms,
                        "tokens_used": None,
                        "confidence_score": 0.0,
                        "timestamp": datetime.now().isoformat(),
                        "transformation_type": "general"
                    }
                }