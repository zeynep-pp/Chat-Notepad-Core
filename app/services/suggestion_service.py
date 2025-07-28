from typing import List, Dict, Optional, Any
from uuid import UUID
import openai
from supabase import Client
from app.config.supabase import get_supabase_client
from app.config.config import settings
from app.models.requests import SuggestionRequest, SuggestionResponse
from app.services.history_service import HistoryService

class SuggestionService:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self.history_service = HistoryService()
        
        # Initialize OpenAI client
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_enabled = True
        else:
            self.openai_enabled = False
            print("⚠️ OpenAI API key not configured, AI suggestions disabled")

    async def get_suggestions(
        self,
        user_id: UUID,
        request: SuggestionRequest
    ) -> SuggestionResponse:
        """Get context-aware suggestions for the user."""
        try:
            suggestions = []
            confidence = 0.0
            
            # Get different types of suggestions based on context type
            if request.context_type == "command":
                suggestions = await self._get_command_suggestions(user_id, request)
                confidence = 0.9
            elif request.context_type == "content":
                suggestions = await self._get_content_suggestions(user_id, request)
                confidence = 0.8
            elif request.context_type == "style":
                suggestions = await self._get_style_suggestions(user_id, request)
                confidence = 0.7
            
            # Store successful suggestions for learning
            if suggestions:
                await self._store_suggestion_context(user_id, request, suggestions)
            
            return SuggestionResponse(
                suggestions=suggestions,
                context_type=request.context_type,
                confidence=confidence
            )
            
        except Exception as e:
            raise Exception(f"Failed to get suggestions: {str(e)}")

    async def _get_command_suggestions(
        self,
        user_id: UUID,
        request: SuggestionRequest
    ) -> List[str]:
        """Get command suggestions based on user history and context."""
        suggestions = []
        
        # Get popular commands from history
        popular_commands = await self.history_service.get_popular_commands(
            user_id=user_id,
            limit=5,
            days_back=14
        )
        
        # Add popular commands as suggestions
        for cmd in popular_commands:
            suggestions.append(cmd["command"])
        
        # Add common commands if no history
        if not suggestions:
            suggestions = [
                "summarize",
                "expand",
                "simplify",
                "translate",
                "correct grammar",
                "make formal",
                "make casual",
                "bullet points",
                "paragraph",
                "explain"
            ]
        
        # Filter based on current context
        context_lower = request.context.lower()
        filtered_suggestions = []
        
        for suggestion in suggestions:
            if len(filtered_suggestions) >= 5:
                break
                
            # Simple relevance check
            if any(word in context_lower for word in suggestion.split()):
                filtered_suggestions.append(suggestion)
            elif len(filtered_suggestions) < 3:
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions[:5]

    async def _get_content_suggestions(
        self,
        user_id: UUID,
        request: SuggestionRequest
    ) -> List[str]:
        """Get content completion suggestions using AI."""
        suggestions = []
        
        if not self.openai_enabled:
            return self._get_fallback_content_suggestions(request)
        
        try:
            # Get text around cursor for context
            text = request.text
            cursor_pos = request.cursor_position
            
            # Get context window (50 chars before and after cursor)
            start = max(0, cursor_pos - 50)
            end = min(len(text), cursor_pos + 50)
            context_window = text[start:end]
            
            # Create prompt for OpenAI
            prompt = f"""
            Given this text context: "{context_window}"
            The cursor is at position {cursor_pos - start} in this context.
            
            Provide 3-5 helpful completions or suggestions for what might come next.
            Focus on:
            1. Completing the current sentence naturally
            2. Suggesting relevant next sentences
            3. Improving clarity or style
            
            Return only the suggestions, one per line, without numbering or bullets.
            """
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100,
                temperature=0.7,
                n=1,
                stop=None
            )
            
            if response.choices:
                content = response.choices[0].text.strip()
                suggestions = [s.strip() for s in content.split('\n') if s.strip()]
                suggestions = suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            print(f"OpenAI suggestion error: {e}")
            suggestions = self._get_fallback_content_suggestions(request)
        
        return suggestions

    def _get_fallback_content_suggestions(self, request: SuggestionRequest) -> List[str]:
        """Fallback content suggestions when AI is not available."""
        text = request.text
        cursor_pos = request.cursor_position
        
        # Simple rule-based suggestions
        suggestions = []
        
        # Get the word or sentence being typed
        start = max(0, cursor_pos - 20)
        context = text[start:cursor_pos].lower()
        
        # Basic completion suggestions
        if context.endswith(("the ", "a ", "an ")):
            suggestions.extend(["main idea", "key point", "important aspect"])
        elif context.endswith("is "):
            suggestions.extend(["important because", "significant for", "relevant to"])
        elif context.endswith("and "):
            suggestions.extend(["furthermore", "additionally", "also"])
        elif context.endswith("."):
            suggestions.extend([" Moreover,", " However,", " Therefore,", " In addition,"])
        else:
            suggestions.extend(["Therefore,", "However,", "Furthermore,", "In conclusion,"])
        
        return suggestions[:5]

    async def _get_style_suggestions(
        self,
        user_id: UUID,
        request: SuggestionRequest
    ) -> List[str]:
        """Get style improvement suggestions."""
        suggestions = [
            "Make more formal",
            "Make more casual", 
            "Simplify language",
            "Use active voice",
            "Add more details",
            "Make more concise",
            "Improve flow",
            "Add transitions",
            "Use stronger verbs",
            "Vary sentence length"
        ]
        
        # Analyze current text for specific style suggestions
        text = request.text.lower()
        
        specific_suggestions = []
        if "very " in text or "really " in text:
            specific_suggestions.append("Replace weak intensifiers")
        if text.count("is") + text.count("was") + text.count("are") + text.count("were") > len(text.split()) * 0.1:
            specific_suggestions.append("Use more active voice")
        if len([s for s in text.split('.') if len(s.split()) > 25]) > 0:
            specific_suggestions.append("Break up long sentences")
        
        # Combine specific and general suggestions
        final_suggestions = specific_suggestions + suggestions
        return final_suggestions[:5]

    async def _store_suggestion_context(
        self,
        user_id: UUID,
        request: SuggestionRequest,
        suggestions: List[str]
    ):
        """Store suggestion context for learning."""
        try:
            context_data = {
                "text_context": request.context,
                "cursor_position": request.cursor_position,
                "suggestions_provided": suggestions
            }
            
            # Check if similar context exists
            result = self.supabase.table("suggestion_contexts") \
                .select("*") \
                .eq("user_id", str(user_id)) \
                .eq("context_type", request.context_type) \
                .execute()
            
            # Simple similarity check (could be improved)
            similar_context = None
            for ctx in result.data:
                stored_context = ctx.get("context_data", {}).get("text_context", "")
                if self._are_contexts_similar(stored_context, request.context):
                    similar_context = ctx
                    break
            
            if similar_context:
                # Update frequency
                self.supabase.table("suggestion_contexts") \
                    .update({
                        "frequency": similar_context["frequency"] + 1,
                        "last_used": "now()"
                    }) \
                    .eq("id", similar_context["id"]) \
                    .execute()
            else:
                # Create new context record
                self.supabase.table("suggestion_contexts") \
                    .insert({
                        "user_id": str(user_id),
                        "context_type": request.context_type,
                        "context_data": context_data,
                        "frequency": 1
                    }) \
                    .execute()
                    
        except Exception as e:
            # Don't fail the main operation if context storage fails
            print(f"Failed to store suggestion context: {e}")

    def _are_contexts_similar(self, context1: str, context2: str) -> bool:
        """Simple similarity check for contexts."""
        if not context1 or not context2:
            return False
        
        words1 = set(context1.lower().split())
        words2 = set(context2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union)
        return jaccard_similarity > 0.3  # 30% similarity threshold

    async def get_user_suggestion_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's suggestion usage statistics."""
        try:
            result = self.supabase.table("suggestion_contexts") \
                .select("context_type, frequency") \
                .eq("user_id", str(user_id)) \
                .execute()
            
            if not result.data:
                return {"total_suggestions": 0, "by_type": {}}
            
            stats = {"by_type": {}, "total_suggestions": 0}
            
            for ctx in result.data:
                context_type = ctx["context_type"]
                frequency = ctx["frequency"]
                
                if context_type not in stats["by_type"]:
                    stats["by_type"][context_type] = 0
                
                stats["by_type"][context_type] += frequency
                stats["total_suggestions"] += frequency
            
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to get suggestion stats: {str(e)}")