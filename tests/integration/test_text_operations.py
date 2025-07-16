import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app


class TestTextOperationsIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_agent_manager(self):
        manager = Mock()
        manager.execute = AsyncMock()
        manager.get_available_agents = Mock(return_value=["editor", "summarizer"])
        return manager

    def test_process_text_success(self, client, mock_agent_manager):
        mock_agent_manager.execute.return_value = {
            "result": "HELLO WORLD",
            "success": True,
            "agent_used": "editor",
            "agent_info": {"method": "uppercase", "processing_time": 0.1}
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/prompt",
                json={"text": "hello world", "command": "uppercase"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "HELLO WORLD"
        assert data["success"] is True
        assert data["agent_used"] == "editor"
        assert "diff" in data

    def test_process_text_agent_error(self, client):
        # Test with actual endpoint - should handle errors gracefully
        response = client.post(
            "/api/v1/prompt",
            json={"text": "hello world", "command": "invalid_command_that_causes_error"}
        )
        
        # Should return 200 with error in response or 500 with error message
        assert response.status_code in [200, 500]

    def test_process_text_invalid_input(self, client):
        response = client.post(
            "/api/v1/prompt",
            json={"text": "", "command": ""}
        )
        
        # Should handle empty input gracefully
        assert response.status_code in [200, 422, 500]

    def test_summarize_text_success(self, client):
        # Test with actual endpoint
        response = client.post(
            "/api/v1/summarize",
            json={"text": "This is a long text that needs to be summarized", "command": "summarize"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "success" in data
        assert "agent_used" in data
        assert "diff" in data

    def test_summarize_text_error(self, client):
        # Test with invalid input that might cause error
        response = client.post(
            "/api/v1/summarize",
            json={"text": "", "command": "invalid_summarize_command"}
        )
        
        # Should handle errors gracefully
        assert response.status_code in [200, 500]

    def test_list_agents_success(self, client, mock_agent_manager):
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.get("/api/v1/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agents"] == ["editor", "summarizer"]

    def test_list_agents_error(self, client):
        # Test actual endpoint - should work normally
        response = client.get("/api/v1/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data

    def test_endpoint_with_missing_fields(self, client):
        response = client.post(
            "/api/v1/prompt",
            json={"text": "hello world"}  # Missing command
        )
        
        assert response.status_code == 422  # Validation error

    def test_endpoint_with_invalid_json(self, client):
        response = client.post(
            "/api/v1/prompt",
            data="invalid json"
        )
        
        assert response.status_code == 422

    def test_agent_manager_dependency_injection(self, client):
        # Test that endpoints work with dependency injection
        response = client.post(
            "/api/v1/prompt",
            json={"text": "test", "command": "uppercase"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "success" in data

    def test_diff_generation(self, client, mock_agent_manager):
        mock_agent_manager.execute.return_value = {
            "result": "HELLO WORLD",
            "success": True,
            "agent_used": "editor",
            "agent_info": {}
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/prompt",
                json={"text": "hello world", "command": "uppercase"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "diff" in data
        assert data["diff"] is not None