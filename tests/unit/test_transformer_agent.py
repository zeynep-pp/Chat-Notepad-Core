import pytest
from unittest.mock import Mock, patch
from app.agents.transformer_agent import TransformerAgent
from app.services.llm_service import LLMService


class TestTransformerAgent:
    """Unit tests for TransformerAgent"""
    
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
    
    def test_init(self):
        """Test TransformerAgent initialization"""
        with patch('app.agents.transformer_agent.LLMService'):
            agent = TransformerAgent()
            assert agent.name == "text_transformer"
    
    def test_detect_transformation_type_formalization(self, transformer_agent):
        """Test detection of formalization commands"""
        formalization_commands = [
            "Make this more formal",
            "Formalize this text",
            "Convert to professional tone",
            "Make this business appropriate",
            "Change to official language",
            "Make this academic style",
            "Use proper language",
            "Make this more polite"
        ]
        
        for command in formalization_commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result == "formalization", f"Failed for command: {command}"
    
    def test_detect_transformation_type_simplification(self, transformer_agent):
        """Test detection of simplification commands"""
        simplification_commands = [
            "Simplify this text",
            "Make this simpler",
            "Explain in easier terms",
            "Make this easy to understand",
            "Convert to beginner level",
            "Use basic language",
            "Make this plain English",
            "Explain for layman"
        ]
        
        for command in simplification_commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result == "simplification", f"Failed for command: {command}"
    
    def test_detect_transformation_type_tone_shift(self, transformer_agent):
        """Test detection of tone shift commands"""
        tone_shift_commands = [
            "Change the tone",
            "Make this more casual",
            "Make this friendly",
            "Add warmth to this",
            "Make this conversational",
            "Make this approachable",
            "Add personal touch"
        ]
        
        for command in tone_shift_commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result == "tone_shift", f"Failed for command: {command}"
    
    def test_detect_transformation_type_none(self, transformer_agent):
        """Test detection when no transformation type matches"""
        unrecognized_commands = [
            "Translate to Spanish",
            "Count the words",
            "Remove punctuation",
            "Add line numbers",
            "Extract keywords"
        ]
        
        for command in unrecognized_commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result is None, f"Unexpected result for command: {command}"
    
    def test_get_transformation_prompt_formalization(self, transformer_agent):
        """Test formalization prompt generation"""
        prompt = transformer_agent.get_transformation_prompt("formalization", "Make this formal")
        
        assert len(prompt) > 100
        assert "formal" in prompt.lower()
        assert "professional" in prompt.lower()
        assert "contractions" in prompt.lower()
        assert "rules:" in prompt.lower()
    
    def test_get_transformation_prompt_simplification(self, transformer_agent):
        """Test simplification prompt generation"""
        prompt = transformer_agent.get_transformation_prompt("simplification", "Simplify this")
        
        assert len(prompt) > 100
        assert "simple" in prompt.lower()
        assert "complex" in prompt.lower()
        assert "jargon" in prompt.lower()
        assert "rules:" in prompt.lower()
    
    def test_get_transformation_prompt_tone_shift(self, transformer_agent):
        """Test tone shift prompt generation"""
        prompt = transformer_agent.get_transformation_prompt("tone_shift", "Make this casual")
        
        assert len(prompt) > 100
        assert "tone" in prompt.lower()
        assert "casual" in prompt.lower()
        assert "friendly" in prompt.lower()
        assert "conversational" in prompt.lower()
        assert "rules:" in prompt.lower()
    
    def test_get_transformation_prompt_general(self, transformer_agent):
        """Test general transformation prompt"""
        command = "Custom transformation"
        prompt = transformer_agent.get_transformation_prompt("unknown", command)
        
        assert len(prompt) > 100
        assert command in prompt
        assert "rules:" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_process_with_detected_transformation(self, transformer_agent, mock_llm_service):
        """Test processing with detected transformation type"""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is a more formal version."))]
        mock_response.usage = Mock(total_tokens=25)
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        result = await transformer_agent.process("hey there!", "Make this formal")
        
        assert result["result"] == "This is a more formal version."
        assert result["agent_info"]["model"] == "text-transformation-agent"
        assert result["agent_info"]["transformation_type"] == "formalization"
        assert result["agent_info"]["tokens_used"] == 25
        assert result["agent_info"]["confidence_score"] == 0.95
        assert result["agent_info"]["processing_time_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_process_with_llm_error(self, transformer_agent, mock_llm_service):
        """Test processing when LLM service fails"""
        mock_llm_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        result = await transformer_agent.process("hey there!", "Make this formal")
        
        assert result["result"] == "hey there!"  # Should return original text
        assert result["agent_info"]["model"] == "text-transformation-agent"
        assert result["agent_info"]["transformation_type"] == "formalization"
        assert result["agent_info"]["confidence_score"] == 0.0
        assert result["agent_info"]["tokens_used"] is None
    
    @pytest.mark.asyncio
    async def test_process_unrecognized_command(self, transformer_agent, mock_llm_service):
        """Test processing with unrecognized command (falls back to general LLM)"""
        mock_llm_result = {
            "result": "Processed text",
            "agent_info": {
                "model": "gpt-4o",
                "processing_time_ms": 1500,
                "tokens_used": 30,
                "confidence_score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        mock_llm_service.process_complex_command.return_value = mock_llm_result
        
        result = await transformer_agent.process("Some text", "Translate to Spanish")
        
        assert result["result"] == "Processed text"
        assert result["agent_info"]["model"] == "text-transformation-agent"
        assert result["agent_info"]["transformation_type"] == "general"
        assert result["agent_info"]["tokens_used"] == 30
    
    @pytest.mark.asyncio
    async def test_process_response_without_usage(self, transformer_agent, mock_llm_service):
        """Test processing when response doesn't include usage info"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Transformed text"))]
        mock_response.usage = None
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        result = await transformer_agent.process("Original text", "Make this formal")
        
        assert result["result"] == "Transformed text"
        assert result["agent_info"]["tokens_used"] is None
        assert result["agent_info"]["confidence_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_process_empty_response(self, transformer_agent, mock_llm_service):
        """Test processing when LLM returns empty response"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_response.usage = Mock(total_tokens=10)
        
        mock_llm_service.client.chat.completions.create.return_value = mock_response
        
        original_text = "Original text"
        result = await transformer_agent.process(original_text, "Make this formal")
        
        assert result["result"] == original_text  # Should return original text
        assert result["agent_info"]["tokens_used"] == 10
    
    def test_case_insensitive_detection(self, transformer_agent):
        """Test that command detection is case insensitive"""
        commands = [
            ("MAKE THIS FORMAL", "formalization"),
            ("Simplify This Text", "simplification"),
            ("change the TONE", "tone_shift"),
            ("Make this PROFESSIONAL", "formalization"),
            ("make it EASIER", "simplification"),
            ("More CASUAL please", "tone_shift")
        ]
        
        for command, expected in commands:
            result = transformer_agent.detect_transformation_type(command)
            assert result == expected, f"Failed for command: {command}"
    
    def test_partial_keyword_matching(self, transformer_agent):
        """Test that partial keyword matching works correctly"""
        # These should match
        positive_cases = [
            ("I need to formalize this document", "formalization"),
            ("Can you simplify the explanation?", "simplification"),
            ("Please make the tone more friendly", "tone_shift")
        ]
        
        for command, expected in positive_cases:
            result = transformer_agent.detect_transformation_type(command)
            assert result == expected, f"Failed for command: {command}"
    
    def test_edge_cases_command_detection(self, transformer_agent):
        """Test edge cases in command detection"""
        edge_cases = [
            ("", None),  # Empty string
            ("   ", None),  # Whitespace only
            ("a", None),  # Single character
            ("formal", "formalization"),  # Single keyword
            ("This is a formal document", "formalization"),  # Keyword in context
            ("informal", "formalization"),  # Edge case: informal contains formal
        ]
        
        for command, expected in edge_cases:
            result = transformer_agent.detect_transformation_type(command)
            assert result == expected, f"Failed for command: '{command}'"