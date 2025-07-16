import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app


class TestTransformEndpointIntegration:
    """Integration tests for /transform endpoint"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_agent_manager(self):
        """Mock agent manager for testing"""
        manager = Mock()
        manager.execute = AsyncMock()
        manager.get_available_agents = Mock(return_value=["editor", "summarizer", "transformer"])
        return manager
    
    @pytest.fixture
    def mock_successful_transform_response(self):
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
    
    def test_transform_endpoint_success(self, client, mock_agent_manager, mock_successful_transform_response):
        """Test successful transformation request"""
        mock_agent_manager.execute.return_value = mock_successful_transform_response
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
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
        assert data["agent_info"]["tokens_used"] == 450
        assert data["agent_info"]["confidence_score"] == 0.95
        
        # Verify agent manager was called correctly
        mock_agent_manager.execute.assert_called_once_with(
            "transformer",
            "hey there! hope you're doing well",
            "Make this more formal"
        )
    
    def test_transform_endpoint_formalization(self, client, mock_agent_manager):
        """Test formalization transformation"""
        mock_agent_manager.execute.return_value = {
            "result": "Good afternoon. I would like to request your assistance with this matter.",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1100,
                "tokens_used": 380,
                "confidence_score": 0.93,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={"text": "hi! can you help me with this?", "command": "make this professional"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent_info"]["transformation_type"] == "formalization"
    
    def test_transform_endpoint_simplification(self, client, mock_agent_manager):
        """Test simplification transformation"""
        mock_agent_manager.execute.return_value = {
            "result": "We need to make this process easier for everyone to understand.",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 950,
                "tokens_used": 320,
                "confidence_score": 0.91,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "simplification"
            }
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={
                    "text": "We must endeavor to facilitate comprehensive understanding of this methodology.",
                    "command": "simplify this text"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent_info"]["transformation_type"] == "simplification"
    
    def test_transform_endpoint_tone_shift(self, client, mock_agent_manager):
        """Test tone shift transformation"""
        mock_agent_manager.execute.return_value = {
            "result": "Hey! We'd love to help you out with this. Let's get started!",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1050,
                "tokens_used": 290,
                "confidence_score": 0.89,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "tone_shift"
            }
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={
                    "text": "We are pleased to offer our assistance with your request.",
                    "command": "make this more casual and friendly"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent_info"]["transformation_type"] == "tone_shift"
    
    def test_transform_endpoint_empty_text(self, client):
        """Test transformation with empty text"""
        response = client.post(
            "/api/v1/transform",
            json={"text": "", "command": "make this formal"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Text cannot be empty" in data["detail"]
    
    def test_transform_endpoint_whitespace_only_text(self, client):
        """Test transformation with whitespace-only text"""
        response = client.post(
            "/api/v1/transform",
            json={"text": "   ", "command": "make this formal"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Text cannot be empty" in data["detail"]
    
    def test_transform_endpoint_empty_command(self, client):
        """Test transformation with empty command"""
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": ""}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Command cannot be empty" in data["detail"]
    
    def test_transform_endpoint_whitespace_only_command(self, client):
        """Test transformation with whitespace-only command"""
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": "   "}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Command cannot be empty" in data["detail"]
    
    def test_transform_endpoint_text_too_long(self, client):
        """Test transformation with text exceeding length limit"""
        long_text = "a" * 10001  # Exceeds 10,000 character limit
        
        response = client.post(
            "/api/v1/transform",
            json={"text": long_text, "command": "make this formal"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Text too long" in data["detail"]
    
    def test_transform_endpoint_command_too_long(self, client):
        """Test transformation with command exceeding length limit"""
        long_command = "a" * 501  # Exceeds 500 character limit
        
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world", "command": long_command}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Command too long" in data["detail"]
    
    def test_transform_endpoint_missing_text_field(self, client):
        """Test transformation with missing text field"""
        response = client.post(
            "/api/v1/transform",
            json={"command": "make this formal"}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_transform_endpoint_missing_command_field(self, client):
        """Test transformation with missing command field"""
        response = client.post(
            "/api/v1/transform",
            json={"text": "hello world"}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_transform_endpoint_invalid_json(self, client):
        """Test transformation with invalid JSON"""
        response = client.post(
            "/api/v1/transform",
            data="invalid json"
        )
        
        assert response.status_code == 422
    
    def test_transform_endpoint_agent_manager_error(self, client, mock_agent_manager):
        """Test transformation when agent manager raises exception"""
        mock_agent_manager.execute.side_effect = Exception("Agent processing failed")
        
        with patch('app.routers.text_operations.get_agent_manager') as mock_get_agent_manager:
            mock_get_agent_manager.return_value = mock_agent_manager
            response = client.post(
                "/api/v1/transform",
                json={"text": "hello world", "command": "make this formal"}
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    def test_transform_endpoint_diff_generation(self, client, mock_agent_manager):
        """Test that diff is generated correctly"""
        mock_agent_manager.execute.return_value = {
            "result": "HELLO WORLD",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 500,
                "tokens_used": 100,
                "confidence_score": 0.95,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={"text": "hello world", "command": "make this uppercase"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "diff" in data
        assert data["diff"] is not None
    
    def test_transform_endpoint_agent_info_structure(self, client, mock_agent_manager):
        """Test that agent_info has correct structure"""
        mock_agent_manager.execute.return_value = {
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
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
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
    
    def test_transform_endpoint_various_commands(self, client, mock_agent_manager):
        """Test transformation with various command types"""
        test_cases = [
            ("Please make this formal", "formalization"),
            ("Simplify this explanation", "simplification"),
            ("Make it more casual", "tone_shift"),
            ("Transform this text", "general")
        ]
        
        for command, expected_type in test_cases:
            mock_agent_manager.execute.return_value = {
                "result": "Transformed text",
                "success": True,
                "agent_used": "transformer",
                "agent_info": {
                    "model": "text-transformation-agent",
                    "processing_time_ms": 1000,
                    "tokens_used": 300,
                    "confidence_score": 0.9,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "transformation_type": expected_type
                }
            }
            
            with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
                response = client.post(
                    "/api/v1/transform",
                    json={"text": "test text", "command": command}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["agent_info"]["transformation_type"] == expected_type
    
    def test_transform_endpoint_unicode_text(self, client, mock_agent_manager):
        """Test transformation with unicode text"""
        mock_agent_manager.execute.return_value = {
            "result": "Formal unicode text with émojis: 🎉",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1100,
                "tokens_used": 250,
                "confidence_score": 0.88,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={"text": "hey unicode text with émojis: 🎉", "command": "make this formal"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "émojis" in data["result"]
        assert "🎉" in data["result"]
    
    def test_transform_endpoint_boundary_text_length(self, client, mock_agent_manager):
        """Test transformation with text at boundary lengths"""
        mock_agent_manager.execute.return_value = {
            "result": "Transformed text",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 1500,
                "tokens_used": 400,
                "confidence_score": 0.85,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        # Test with exactly 10,000 characters (should pass)
        boundary_text = "a" * 10000
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={"text": boundary_text, "command": "make this formal"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_transform_endpoint_boundary_command_length(self, client, mock_agent_manager):
        """Test transformation with command at boundary length"""
        mock_agent_manager.execute.return_value = {
            "result": "Transformed text",
            "success": True,
            "agent_used": "transformer",
            "agent_info": {
                "model": "text-transformation-agent",
                "processing_time_ms": 800,
                "tokens_used": 200,
                "confidence_score": 0.9,
                "timestamp": "2024-01-15T10:30:00Z",
                "transformation_type": "formalization"
            }
        }
        
        # Test with exactly 500 characters (should pass)
        boundary_command = "make this formal " + "a" * 483  # 500 total chars
        
        with patch('app.routers.text_operations.get_agent_manager', return_value=mock_agent_manager):
            response = client.post(
                "/api/v1/transform",
                json={"text": "hello world", "command": boundary_command}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True