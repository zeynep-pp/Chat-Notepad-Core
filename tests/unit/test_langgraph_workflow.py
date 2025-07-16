import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.langgraph_workflow import LangGraphWorkflow, WorkflowState


class TestLangGraphWorkflow:
    @pytest.fixture
    def workflow(self):
        return LangGraphWorkflow()

    @pytest.fixture
    def sample_state(self):
        return WorkflowState(
            text="Hello world",
            command="uppercase",
            result="",
            agent_used="",
            agent_info={},
            success=False,
            error=None
        )

    def test_route_decision_editor(self, workflow):
        state = WorkflowState(
            text="test",
            command="uppercase",
            result="",
            agent_used="",
            agent_info={},
            success=False,
            error=None
        )
        result = workflow._route_decision(state)
        assert result == "editor"

    def test_route_decision_summarizer(self, workflow):
        state = WorkflowState(
            text="test",
            command="summarize",
            result="",
            agent_used="",
            agent_info={},
            success=False,
            error=None
        )
        result = workflow._route_decision(state)
        assert result == "summarizer"

    def test_route_decision_default(self, workflow):
        state = WorkflowState(
            text="test",
            command="unknown command",
            result="",
            agent_used="",
            agent_info={},
            success=False,
            error=None
        )
        result = workflow._route_decision(state)
        assert result == "editor"

    @pytest.mark.asyncio
    async def test_route_request(self, workflow, sample_state):
        result = await workflow._route_request(sample_state)
        assert result == sample_state

    @pytest.mark.asyncio
    async def test_process_text_editor_success(self, workflow, sample_state):
        mock_result = {
            "result": "HELLO WORLD",
            "agent_info": {"method": "uppercase"}
        }
        
        with patch.object(workflow.text_editor, 'validate_input', return_value=True), \
             patch.object(workflow.text_editor, 'process', return_value=mock_result):
            
            result = await workflow._process_text_editor(sample_state)
            
            assert result["result"] == "HELLO WORLD"
            assert result["success"] is True
            assert result["agent_used"] == "editor"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_process_text_editor_validation_error(self, workflow, sample_state):
        with patch.object(workflow.text_editor, 'validate_input', return_value=False):
            result = await workflow._process_text_editor(sample_state)
            
            assert result["success"] is False
            assert "Error:" in result["result"]
            assert result["agent_used"] == "editor"

    @pytest.mark.asyncio
    async def test_process_text_editor_processing_error(self, workflow, sample_state):
        with patch.object(workflow.text_editor, 'validate_input', return_value=True), \
             patch.object(workflow.text_editor, 'process', side_effect=Exception("Processing failed")):
            
            result = await workflow._process_text_editor(sample_state)
            
            assert result["success"] is False
            assert "Error: Processing failed" in result["result"]
            assert result["agent_used"] == "editor"

    @pytest.mark.asyncio
    async def test_process_summarizer_success(self, workflow, sample_state):
        sample_state["command"] = "summarize"
        mock_result = {
            "result": "Summary of hello world",
            "agent_info": {"method": "summarize"}
        }
        
        with patch.object(workflow.summarizer, 'validate_input', return_value=True), \
             patch.object(workflow.summarizer, 'process', return_value=mock_result):
            
            result = await workflow._process_summarizer(sample_state)
            
            assert result["result"] == "Summary of hello world"
            assert result["success"] is True
            assert result["agent_used"] == "summarizer"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_process_summarizer_error(self, workflow, sample_state):
        sample_state["command"] = "summarize"
        
        with patch.object(workflow.summarizer, 'validate_input', return_value=False):
            result = await workflow._process_summarizer(sample_state)
            
            assert result["success"] is False
            assert "Error:" in result["result"]
            assert result["agent_used"] == "summarizer"

    @pytest.mark.asyncio
    async def test_handle_error(self, workflow, sample_state):
        sample_state["error"] = "Test error"
        
        result = await workflow._handle_error(sample_state)
        
        assert result["success"] is False
        assert result["result"] == "Error: Unable to process request"
        assert result["agent_used"] == "error_handler"

    @pytest.mark.asyncio
    async def test_execute_success(self, workflow):
        mock_final_state = {
            "result": "HELLO WORLD",
            "success": True,
            "agent_used": "editor",
            "agent_info": {"method": "uppercase"}
        }
        
        with patch.object(workflow.workflow, 'ainvoke', return_value=mock_final_state):
            result = await workflow.execute("hello world", "uppercase")
            
            assert result["result"] == "HELLO WORLD"
            assert result["success"] is True
            assert result["agent_used"] == "editor"
            assert result["agent_info"] == {"method": "uppercase"}

    @pytest.mark.asyncio
    async def test_execute_workflow_error(self, workflow):
        with patch.object(workflow.workflow, 'ainvoke', side_effect=Exception("Workflow failed")):
            result = await workflow.execute("hello world", "uppercase")
            
            assert result["success"] is False
            assert "Workflow error:" in result["result"]
            assert result["agent_used"] == "workflow_error"
            assert result["agent_info"] == {}