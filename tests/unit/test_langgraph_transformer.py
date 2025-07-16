import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.langgraph_workflow import LangGraphWorkflow


class TestLangGraphTransformerIntegration:
    """Unit tests for transformer integration in LangGraph workflow"""
    
    @pytest.fixture
    def mock_agents(self):
        """Mock all agents used in the workflow"""
        mock_text_editor = Mock()
        mock_text_editor.name = "editor"
        mock_text_editor.validate_input = AsyncMock(return_value=True)
        mock_text_editor.process = AsyncMock()
        
        mock_summarizer = Mock()
        mock_summarizer.name = "summarizer"
        mock_summarizer.validate_input = AsyncMock(return_value=True)
        mock_summarizer.process = AsyncMock()
        
        mock_transformer = Mock()
        mock_transformer.name = "transformer"
        mock_transformer.validate_input = AsyncMock(return_value=True)
        mock_transformer.process = AsyncMock()
        
        return {
            "text_editor": mock_text_editor,
            "summarizer": mock_summarizer,
            "transformer": mock_transformer
        }
    
    @pytest.fixture
    def workflow(self, mock_agents):
        """Create workflow with mocked agents"""
        with patch('app.core.langgraph_workflow.TextEditorAgent', return_value=mock_agents["text_editor"]), \
             patch('app.core.langgraph_workflow.SummarizerAgent', return_value=mock_agents["summarizer"]), \
             patch('app.core.langgraph_workflow.TransformerAgent', return_value=mock_agents["transformer"]):
            
            workflow = LangGraphWorkflow()
            workflow.text_editor = mock_agents["text_editor"]
            workflow.summarizer = mock_agents["summarizer"]
            workflow.transformer = mock_agents["transformer"]
            return workflow
    
    def test_workflow_initialization(self, workflow, mock_agents):
        """Test that workflow initializes with transformer agent"""
        assert workflow.transformer == mock_agents["transformer"]
        assert hasattr(workflow, 'text_editor')
        assert hasattr(workflow, 'summarizer')
        assert hasattr(workflow, 'transformer')
    
    def test_route_decision_formalization_commands(self, workflow):
        """Test routing of formalization commands to transformer"""
        formalization_commands = [
            "Make this formal",
            "Formalize this text",
            "Make this professional",
            "Convert to business language",
            "Make this official"
        ]
        
        for command in formalization_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "transformer", f"Failed to route '{command}' to transformer"
    
    def test_route_decision_simplification_commands(self, workflow):
        """Test routing of simplification commands to transformer"""
        simplification_commands = [
            "Simplify this text",
            "Make this simpler",
            "Explain in easy terms",
            "Make this basic",
            "Convert to plain language"
        ]
        
        for command in simplification_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "transformer", f"Failed to route '{command}' to transformer"
    
    def test_route_decision_tone_shift_commands(self, workflow):
        """Test routing of tone shift commands to transformer"""
        tone_shift_commands = [
            "Change the tone",
            "Make this casual",
            "Make this friendly",
            "Make this conversational",
            "Add warmth to this"
        ]
        
        for command in tone_shift_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "transformer", f"Failed to route '{command}' to transformer"
    
    def test_route_decision_transform_commands(self, workflow):
        """Test routing of explicit transform commands"""
        transform_commands = [
            "Transform this text",
            "Please transform this",
            "I need to transform this"
        ]
        
        for command in transform_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "transformer", f"Failed to route '{command}' to transformer"
    
    def test_route_decision_summarization_commands(self, workflow):
        """Test routing of summarization commands to summarizer"""
        summarization_commands = [
            "Summarize this text",
            "Give me a summary",
            "Create a brief overview"
        ]
        
        for command in summarization_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "summarizer", f"Failed to route '{command}' to summarizer"
    
    def test_route_decision_editor_commands(self, workflow):
        """Test routing of editor commands to text editor"""
        editor_commands = [
            "Edit this text",
            "Replace word with another",
            "Remove commas",
            "Make this uppercase",
            "Convert to lowercase",
            "Capitalize sentences"
        ]
        
        for command in editor_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "editor", f"Failed to route '{command}' to editor"
    
    def test_route_decision_default_to_transformer(self, workflow):
        """Test that unknown commands default to transformer"""
        unknown_commands = [
            "Do something with this text",
            "Process this content",
            "Handle this request",
            "Work on this"
        ]
        
        for command in unknown_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == "transformer", f"Failed to default '{command}' to transformer"
    
    def test_route_decision_case_insensitive(self, workflow):
        """Test that routing is case insensitive"""
        mixed_case_commands = [
            ("MAKE THIS FORMAL", "transformer"),
            ("Simplify This TEXT", "transformer"),
            ("SUMMARIZE this content", "summarizer"),
            ("EDIT this text", "editor")
        ]
        
        for command, expected_route in mixed_case_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == expected_route, f"Failed case insensitive routing for '{command}'"
    
    @pytest.mark.asyncio
    async def test_process_transformer_success(self, workflow, mock_agents):
        """Test successful transformer processing"""
        mock_agents["transformer"].process.return_value = {
            "result": "Transformed text",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1200,
                "tokens_used": 350,
                "confidence_score": 0.92,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        state = {
            "text": "Original text",
            "command": "Make this formal",
            "result": "",
            "agent_used": "",
            "agent_info": {},
            "success": False,
            "error": None
        }
        
        result = await workflow._process_transformer(state)
        
        assert result["result"] == "Transformed text"
        assert result["agent_used"] == "transformer"
        assert result["success"] is True
        assert result["error"] is None
        assert result["agent_info"]["transformation_type"] == "formalization"
        
        # Verify transformer was called correctly
        mock_agents["transformer"].validate_input.assert_called_once_with("Original text", "Make this formal")
        mock_agents["transformer"].process.assert_called_once_with("Original text", "Make this formal")
    
    @pytest.mark.asyncio
    async def test_process_transformer_validation_error(self, workflow, mock_agents):
        """Test transformer processing with validation error"""
        mock_agents["transformer"].validate_input.return_value = False
        
        state = {
            "text": "Invalid text",
            "command": "Make this formal",
            "result": "",
            "agent_used": "",
            "agent_info": {},
            "success": False,
            "error": None
        }
        
        result = await workflow._process_transformer(state)
        
        assert result["success"] is False
        assert result["agent_used"] == "transformer"
        assert "Invalid input for transformer" in result["result"]
        assert result["error"] is not None
        
        # Verify transformer process was not called
        mock_agents["transformer"].process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_transformer_processing_error(self, workflow, mock_agents):
        """Test transformer processing with processing error"""
        mock_agents["transformer"].process.side_effect = Exception("Processing failed")
        
        state = {
            "text": "Original text",
            "command": "Make this formal",
            "result": "",
            "agent_used": "",
            "agent_info": {},
            "success": False,
            "error": None
        }
        
        result = await workflow._process_transformer(state)
        
        assert result["success"] is False
        assert result["agent_used"] == "transformer"
        assert "Error: Processing failed" in result["result"]
        assert result["error"] == "Processing failed"
    
    @pytest.mark.asyncio
    async def test_workflow_execution_with_transformer(self, workflow, mock_agents):
        """Test full workflow execution with transformer"""
        mock_agents["transformer"].process.return_value = {
            "result": "Professionally formatted text",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1100,
                "tokens_used": 280,
                "confidence_score": 0.94,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        # Mock the workflow execution
        with patch.object(workflow, 'workflow') as mock_workflow:
            mock_workflow.ainvoke = AsyncMock(return_value={
                "result": "Professionally formatted text",
                "success": True,
                "agent_used": "transformer",
                "agent_info": {
                    "model": "text-transformation-agent",
                    "processing_time_ms": 1100,
                    "tokens_used": 280,
                    "confidence_score": 0.94,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "transformation_type": "formalization"
                }
            })
            
            result = await workflow.execute("casual text here", "make this professional")
            
            assert result["result"] == "Professionally formatted text"
            assert result["success"] is True
            assert result["agent_used"] == "transformer"
            assert result["agent_info"]["transformation_type"] == "formalization"
    
    @pytest.mark.asyncio
    async def test_workflow_execution_error_handling(self, workflow):
        """Test workflow execution error handling"""
        # Mock the workflow execution to raise an exception
        with patch.object(workflow, 'workflow') as mock_workflow:
            mock_workflow.ainvoke = AsyncMock(side_effect=Exception("Workflow execution failed"))
            
            result = await workflow.execute("test text", "transform this")
            
            assert result["success"] is False
            assert result["agent_used"] == "workflow_error"
            assert "Workflow error: Workflow execution failed" in result["result"]
            assert result["agent_info"] == {}
    
    def test_routing_priority_order(self, workflow):
        """Test that transformation keywords have priority over general keywords"""
        # Commands that contain both transformation and general keywords
        mixed_commands = [
            ("edit this text to make it formal", "transformer"),  # formal > edit
            ("simplify and edit this text", "transformer"),       # simplify > edit
            ("summarize this in a casual tone", "transformer"),   # casual > summarize
            ("make this professional summary", "transformer"),    # professional > summary
        ]
        
        for command, expected_route in mixed_commands:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == expected_route, f"Failed priority routing for '{command}'"
    
    def test_edge_cases_routing(self, workflow):
        """Test edge cases in command routing"""
        edge_cases = [
            ("", "transformer"),          # Empty command defaults to transformer
            ("   ", "transformer"),       # Whitespace only defaults to transformer
            ("a", "transformer"),         # Single character defaults to transformer
            ("formal", "transformer"),    # Single keyword routes correctly
            ("This is formal language", "transformer"),  # Keyword in context
        ]
        
        for command, expected_route in edge_cases:
            state = {"command": command}
            result = workflow._route_decision(state)
            assert result == expected_route, f"Failed edge case routing for '{command}'"