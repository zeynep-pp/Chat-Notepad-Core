import pytest
from unittest.mock import Mock, patch
from app.agents.transformer_agent import TransformerAgent
from app.services.llm_service import LLMService
from openai import OpenAIError


class TestTransformErrorHandling:
    """Unit tests for error handling in transformation functionality"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing"""
        mock_service = Mock(spec=LLMService)
        mock_service.model = "gpt-4o"
        mock_service.client = Mock()
        return mock_service
    
    @pytest.fixture
    def transformer_agent(self, mock_llm_service):
        """Create TransformerAgent with mocked LLM service"""
        with patch('app.agents.transformer_agent.LLMService', return_value=mock_llm_service):
            agent = TransformerAgent()
            agent.llm_service = mock_llm_service
            return agent
    
    @pytest.mark.asyncio
    async def test_openai_api_error(self, transformer_agent, mock_llm_service):
        """Test handling of OpenAI API errors"""
        mock_llm_service.client.chat.completions.create.side_effect = OpenAIError("API rate limit exceeded")
        
        original_text = "Test text"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        # Should return original text on error
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["tokens_used"] is None
        assert result["agent_info"]["model"] == "text-transformation-agent"
        assert result["agent_info"]["transformation_type"] == "formalization"
    
    @pytest.mark.asyncio
    async def test_network_timeout_error(self, transformer_agent, mock_llm_service):
        """Test handling of network timeout errors"""
        mock_llm_service.client.chat.completions.create.side_effect = TimeoutError("Request timed out")
        
        original_text = "Test text for timeout"
        result = await transformer_agent.process(original_text, "Simplify this")
        
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["transformation_type"] == "simplification"
    
    @pytest.mark.asyncio
    async def test_connection_error(self, transformer_agent, mock_llm_service):
        """Test handling of connection errors"""
        mock_llm_service.client.chat.completions.create.side_effect = ConnectionError("Connection failed")
        
        original_text = "Test text for connection error"
        result = await transformer_agent.process(original_text, "Make this casual")
        
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["transformation_type"] == "tone_shift"
    
    @pytest.mark.asyncio
    async def test_generic_exception(self, transformer_agent, mock_llm_service):
        """Test handling of generic exceptions"""
        mock_llm_service.client.chat.completions.create.side_effect = Exception("Unexpected error")
        
        original_text = "Test text for generic error"
        result = await transformer_agent.process(original_text, "Unknown command")
        
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["transformation_type"] == "general"
    
    @pytest.mark.asyncio
    async def test_malformed_response(self, transformer_agent, mock_llm_service):
        """Test handling of malformed OpenAI responses"""
        # Mock response with missing or malformed structure
        mock_response = Mock()
        mock_response.choices = []  # Empty choices
        mock_response.usage = None
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        original_text = "Test text for malformed response"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        # Should handle gracefully and return original text
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
    
    @pytest.mark.asyncio
    async def test_response_with_none_content(self, transformer_agent, mock_llm_service):
        """Test handling of response with None content"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_response.usage = Mock(total_tokens=15)
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        original_text = "Test text with None content"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        assert result["result"] == original_text
        assert result["agent_info"]["tokens_used"] == 15
        assert result["agent_info"]["confidence_score"] == 0.95  # Should still be high as no error occurred
    
    @pytest.mark.asyncio
    async def test_response_with_empty_content(self, transformer_agent, mock_llm_service):
        """Test handling of response with empty content"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=""))]
        mock_response.usage = Mock(total_tokens=10)
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        original_text = "Test text with empty content"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        assert result["result"] == original_text
        assert result["agent_info"]["tokens_used"] == 10
        assert result["agent_info"]["confidence_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_response_with_whitespace_only_content(self, transformer_agent, mock_llm_service):
        """Test handling of response with whitespace-only content"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="   \n\t  "))]
        mock_response.usage = Mock(total_tokens=5)
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        original_text = "Test text with whitespace content"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        assert result["result"] == original_text
        assert result["agent_info"]["tokens_used"] == 5
    
    @pytest.mark.asyncio
    async def test_fallback_to_llm_service_error(self, transformer_agent, mock_llm_service):
        """Test error handling when falling back to LLM service"""
        # Test with unrecognized command that falls back to LLM service
        mock_llm_service.process_complex_command.side_effect = Exception("LLM service error")
        
        original_text = "Test text for fallback error"
        result = await transformer_agent.process(original_text, "Translate to Spanish")
        
        # Should handle the error and return original text
        assert result["result"] == original_text
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["transformation_type"] == "general"
    
    @pytest.mark.asyncio
    async def test_fallback_to_llm_service_success(self, transformer_agent, mock_llm_service):
        """Test successful fallback to LLM service"""
        mock_llm_result = {
            "result": "Translated text",
            "agent_info": {
                "model": "gpt-4o",
                "processing_time_ms": 1500,
                "tokens_used": 40,
                "confidence_score": 0.85,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        mock_llm_service.process_complex_command.return_value = mock_llm_result
        
        result = await transformer_agent.process("Hello world", "Translate to Spanish")
        
        assert result["result"] == "Translated text"
        assert result["agent_info"]["model"] == "text-transformation-agent"
        assert result["agent_info"]["transformation_type"] == "general"
        assert result["agent_info"]["tokens_used"] == 40
    
    def test_command_detection_with_none_input(self, transformer_agent):
        """Test command detection with None input"""
        result = transformer_agent.detect_transformation_type(None)
        assert result is None
    
    def test_command_detection_with_numeric_input(self, transformer_agent):
        """Test command detection with numeric input"""
        result = transformer_agent.detect_transformation_type("123")
        assert result is None
    
    def test_command_detection_with_special_characters(self, transformer_agent):
        """Test command detection with special characters"""
        special_commands = [
            ("!@#$%^&*()", None),
            ("formal!!!", "formalization"),
            ("simple???", "simplification"),
            ("casual...tone", "tone_shift"),
            ("make-this-formal", "formalization"),
            ("simplify_this_text", "simplification")
        ]
        
        for command, expected in special_commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result == expected, f"Failed for command '{command}', expected {expected}, got {result}"
    
    def test_prompt_generation_with_invalid_type(self, transformer_agent):
        """Test prompt generation with invalid transformation type"""
        prompt = transformer_agent.get_transformation_prompt("invalid_type", "test command")
        
        # Should fall back to general prompt
        assert len(prompt) > 100
        assert "test command" in prompt
        assert "rules:" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_processing_time_calculation_on_error(self, transformer_agent, mock_llm_service):
        """Test that processing time is calculated even when errors occur"""
        mock_llm_service.client.chat.completions.create.side_effect = Exception("Test error")
        
        result = await transformer_agent.process("test text", "make this formal")
        
        # Processing time should be calculated even on error
        assert result["agent_info"]["processing_time_ms"] >= 0
        assert isinstance(result["agent_info"]["processing_time_ms"], int)
    
    @pytest.mark.asyncio
    async def test_timestamp_generation_on_error(self, transformer_agent, mock_llm_service):
        """Test that timestamp is generated even when errors occur"""
        mock_llm_service.client.chat.completions.create.side_effect = Exception("Test error")
        
        result = await transformer_agent.process("test text", "make this formal")
        
        # Timestamp should be generated even on error
        assert "timestamp" in result["agent_info"]
        assert result["agent_info"]["timestamp"] is not None
        assert len(result["agent_info"]["timestamp"]) > 0
    
    @pytest.mark.asyncio
    async def test_error_logging_verification(self, transformer_agent, mock_llm_service):
        """Test that errors are logged appropriately"""
        with patch('builtins.print') as mock_print:
            mock_llm_service.client.chat.completions.create.side_effect = Exception("Test error for logging")
            
            await transformer_agent.process("test text", "make this formal")
            
            # Verify error was logged
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Transformation error: Test error for logging" in args[0]
    
    def test_command_detection_case_sensitivity_edge_cases(self, transformer_agent):
        """Test command detection with various case combinations"""
        case_variations = [
            ("FoRmAl", "formalization"),
            ("SiMpLiFy", "simplification"),
            ("CaSuAl", "tone_shift"),
            ("FORMAL", "formalization"),
            ("simple", "simplification"),
            ("Tone", "tone_shift")
        ]
        
        for command, expected in case_variations:
            result = transformer_agent.detect_transformation_type(command)
            assert result == expected, f"Failed case sensitivity test for '{command}'"
    
    def test_prompt_generation_with_empty_command(self, transformer_agent):
        """Test prompt generation with empty command"""
        prompt = transformer_agent.get_transformation_prompt("formalization", "")
        
        # Should still generate a valid prompt
        assert len(prompt) > 100
        assert "formal" in prompt.lower()
        assert "rules:" in prompt.lower()
    
    def test_prompt_generation_with_none_command(self, transformer_agent):
        """Test prompt generation with None command"""
        prompt = transformer_agent.get_transformation_prompt("formalization", None)
        
        # Should handle gracefully
        assert len(prompt) > 100
        assert "formal" in prompt.lower()
        assert "rules:" in prompt.lower()