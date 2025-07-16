import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Test response"))]
        mock_instance.chat.completions.create.return_value = mock_completion
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture(scope="session")
def mock_env_vars():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENAI_MODEL': 'gpt-4o-mini',
        'OPENAI_TEMPERATURE': '0.7',
        'OPENAI_MAX_TOKENS': '1000'
    }):
        yield