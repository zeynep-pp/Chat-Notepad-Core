import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app


class TestTransformEndpointSimple:
    """Simplified integration tests for /transform endpoint"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_successful_response(self):
        """Mock successful transformation response"""
        return {
            "result": "Good morning. I hope this message finds you well.",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1250,
                "tokens_used": 450,
                "confidence_score": 0.95,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
    
    @patch('app.routers.text_operations.get_agent_manager')
    def test_transform_endpoint_success(self, mock_get_agent_manager, client, mock_successful_response):
        """Test successful transformation request"""
        mock_agent_manager = Mock()
        mock_agent_manager.execute = AsyncMock(return_value=mock_successful_response)
        mock_get_agent_manager.return_value = mock_agent_manager
        
        response = client.post(
            "/api/v1/transform",
            json={"text": "hey there! hope you're doing well", "command": "Make this more formal"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["result"] == "Good morning. I hope this message finds you well."
        assert data["success"] is True
        assert data["agent_used"] == "transformer"
        assert "diff" in data
        assert data["agent_info"]["model"] == "text-transformation-agent"
        assert data["agent_info"]["transformation_type"] == "formalization"
    
    def test_transform_endpoint_validation_errors(self, client):
        """Test validation errors"""
        # Empty text
        response = client.post(
            "/api/v1/transform",
            json={"text": "", "command": "make this formal"}
        )
        assert response.status_code == 400
        
        # Empty command
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": ""}
        )
        assert response.status_code == 400
        
        # Text too long
        long_text = "a" * 10001
        response = client.post(
            "/api/v1/transform",
            json={"text": long_text, "command": "make this formal"}
        )
        assert response.status_code == 400
        
        # Command too long
        long_command = "a" * 501
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": long_command}
        )
        assert response.status_code == 400
    
    def test_transform_endpoint_missing_fields(self, client):
        """Test missing required fields"""
        # Missing text
        response = client.post(
            "/api/v1/transform",
            json={"command": "make this formal"}
        )
        assert response.status_code == 422
        
        # Missing command
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world"}
        )
        assert response.status_code == 422
    
    @patch('app.routers.text_operations.get_agent_manager')
    def test_transform_endpoint_agent_error(self, mock_get_agent_manager, client):
        """Test error handling when agent fails"""
        mock_agent_manager = Mock()
        mock_agent_manager.execute = AsyncMock(side_effect=Exception("Agent failed"))
        mock_get_agent_manager.return_value = mock_agent_manager
        
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": "make this formal"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    @patch('app.routers.text_operations.get_agent_manager')
    def test_transform_endpoint_different_transformations(self, mock_get_agent_manager, client):
        """Test different transformation types"""
        mock_agent_manager = Mock()
        mock_get_agent_manager.return_value = mock_agent_manager
        
        test_cases = [
            ("formalization", "Make this formal"),
            ("simplification", "Simplify this"),
            ("tone_shift", "Make this casual"),
            ("general", "Transform this")
        ]
        
        for transform_type, command in test_cases:
            mock_agent_manager.execute = AsyncMock(return_value={
                "result": "Transformed text",
                "success": True,
                "agent_used": "transformer",
                "agent_info": {
                    "model": "text-transformation-agent",
                    "processing_time_ms": 1000,
                    "tokens_used": 300,
                    "confidence_score": 0.9,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "transformation_type": transform_type
                }
            })
            
            response = client.post(
                "/api/v1/transform",
                json={"text": "test text", "command": command}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["agent_info"]["transformation_type"] == transform_type
    
    @patch('app.routers.text_operations.get_agent_manager')
    def test_transform_endpoint_boundary_lengths(self, mock_get_agent_manager, client):
        """Test boundary text and command lengths"""
        mock_agent_manager = Mock()
        mock_agent_manager.execute = AsyncMock(return_value={
            "result": "Transformed text",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1000,
                "tokens_used": 300,
                "confidence_score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        })
        mock_get_agent_manager.return_value = mock_agent_manager
        
        # Test with exactly 10,000 characters (should pass)
        boundary_text = "a" * 10000
        response = client.post(
            "/api/v1/transform",
            json={"text": boundary_text, "command": "make this formal"}
        )
        assert response.status_code == 200
        
        # Test with exactly 500 characters (should pass)
        boundary_command = "make this formal " + "a" * 483  # 500 total chars
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": boundary_command}
        )
        assert response.status_code == 200
    
    @patch('app.routers.text_operations.get_agent_manager')
    def test_transform_endpoint_agent_info_structure(self, mock_get_agent_manager, client):
        """Test agent_info structure validation"""
        mock_agent_manager = Mock()
        mock_agent_manager.execute = AsyncMock(return_value={
            "result": "Transformed text",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1200,
                "tokens_used": 350,
                "confidence_score": 0.92,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        })
        mock_get_agent_manager.return_value = mock_agent_manager
        
        response = client.post(
            "/api/v1/transform",
            json={"text": "test text", "command": "make formal"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify agent_info structure
        agent_info = data["agent_info"]
        assert agent_info["model"] == "text-transformation-agent"
        assert isinstance(agent_info["processing_time_ms"], int)
        assert agent_info["processing_time_ms"] > 0
        assert isinstance(agent_info["tokens_used"], int)
        assert agent_info["tokens_used"] > 0
        assert isinstance(agent_info["confidence_score"], float)
        assert 0 <= agent_info["confidence_score"] <= 1
        assert "timestamp" in agent_info
        assert agent_info["transformation_type"] == "formalization"