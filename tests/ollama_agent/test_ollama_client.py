"""Tests for Ollama client."""

import pytest
from unittest.mock import patch, MagicMock

from ollama_agent.ollama_client import OllamaClient, TOOL_COMPATIBLE_MODELS


class TestOllamaClient:
    """Test OllamaClient class."""

    def test_init_default_url(self):
        """Test initialization with default URL."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"

    def test_init_custom_url(self):
        """Test initialization with custom URL."""
        client = OllamaClient(base_url="http://custom:8080")
        assert client.base_url == "http://custom:8080"

    @patch('ollama_agent.ollama_client.requests.get')
    def test_list_models_all(self, mock_get):
        """Test listing all models."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest"},
                {"name": "mistral:latest"},
                {"name": "phi3:latest"}
            ]
        }
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models(tool_compatible_only=False)

        assert len(models) == 3
        assert "llama3.2:latest" in models
        assert "mistral:latest" in models
        assert "phi3:latest" in models

    @patch('ollama_agent.ollama_client.requests.get')
    def test_list_models_tool_compatible_only(self, mock_get):
        """Test listing only tool-compatible models."""
        # Mock API response with mixed models
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest"},      # Compatible
                {"name": "llama3.1:latest"},      # Compatible
                {"name": "mistral:latest"},       # Not compatible
                {"name": "phi3:latest"},          # Not compatible
                {"name": "qwen2.5:latest"},       # Compatible
                {"name": "command-r:latest"},     # Compatible
            ]
        }
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models(tool_compatible_only=True)

        # Should only return tool-compatible models
        assert "llama3.2:latest" in models
        assert "llama3.1:latest" in models
        assert "qwen2.5:latest" in models
        assert "command-r:latest" in models
        assert "mistral:latest" not in models
        assert "phi3:latest" not in models

    @patch('ollama_agent.ollama_client.requests.get')
    def test_list_models_error(self, mock_get):
        """Test list_models error handling."""
        mock_get.side_effect = Exception("Connection failed")

        client = OllamaClient()
        models = client.list_models()

        assert models == []

    @patch('ollama_agent.ollama_client.requests.post')
    def test_chat_basic(self, mock_post):
        """Test basic chat without tools."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            }
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        messages = [
            {"role": "user", "content": "Hello"}
        ]

        response = client.chat(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            stream=False
        )

        assert response["message"]["role"] == "assistant"
        assert response["message"]["content"] == "Hello! How can I help you?"

    @patch('ollama_agent.ollama_client.requests.post')
    def test_chat_with_tools(self, mock_post):
        """Test chat with tool calling."""
        # Mock API response with tool call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "web_search",
                            "arguments": {
                                "query": "quantum computing",
                                "max_results": 5
                            }
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        messages = [
            {"role": "user", "content": "Search for quantum computing"}
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        }
                    }
                }
            }
        ]

        response = client.chat(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            stream=False,
            tools=tools
        )

        assert "tool_calls" in response["message"]
        assert len(response["message"]["tool_calls"]) == 1
        assert response["message"]["tool_calls"][0]["function"]["name"] == "web_search"

    @patch('ollama_agent.ollama_client.requests.post')
    def test_chat_error(self, mock_post):
        """Test chat error handling."""
        mock_post.side_effect = Exception("API error")

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(Exception) as exc_info:
            client.chat(
                model="llama3.2",
                messages=messages,
                temperature=0.7,
                stream=False
            )

        assert "API error" in str(exc_info.value)

    def test_tool_compatible_models_constant(self):
        """Test that TOOL_COMPATIBLE_MODELS is defined correctly."""
        assert isinstance(TOOL_COMPATIBLE_MODELS, list)
        assert len(TOOL_COMPATIBLE_MODELS) > 0

        # Check expected models are in the list
        expected_models = ["llama3.2", "llama3.1", "qwen2.5", "command-r"]
        for model in expected_models:
            assert model in TOOL_COMPATIBLE_MODELS

    @patch('ollama_agent.ollama_client.requests.get')
    def test_list_models_partial_match(self, mock_get):
        """Test that partial model name matches work for tool compatibility."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:7b"},           # Should match llama3.2
                {"name": "llama3.2:13b"},          # Should match llama3.2
                {"name": "llama3.1:70b-instruct"}, # Should match llama3.1
                {"name": "other-model:latest"},    # Should not match
            ]
        }
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models(tool_compatible_only=True)

        # All llama3.2 and llama3.1 variants should be included
        assert "llama3.2:7b" in models
        assert "llama3.2:13b" in models
        assert "llama3.1:70b-instruct" in models
        assert "other-model:latest" not in models

    @patch('ollama_agent.ollama_client.requests.post')
    def test_chat_request_format(self, mock_post):
        """Test that chat request is formatted correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"role": "assistant", "content": "Response"}
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        messages = [{"role": "user", "content": "Test"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        client.chat(
            model="llama3.2",
            messages=messages,
            temperature=0.8,
            stream=False,
            tools=tools
        )

        # Verify the POST request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        assert call_args[0][0] == "http://localhost:11434/api/chat"

        # Check payload
        payload = call_args[1]["json"]
        assert payload["model"] == "llama3.2"
        assert payload["messages"] == messages
        assert payload["temperature"] == 0.8
        assert payload["stream"] is False
        assert payload["tools"] == tools
