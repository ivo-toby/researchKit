"""HTTP client for Ollama API with tool calling support."""

import json
from typing import Any, Callable, Dict, List, Optional
import requests


class OllamaClient:
    """HTTP client for Ollama API with tool calling support."""

    # Models known to support tool calling (function calling)
    TOOL_COMPATIBLE_MODELS = [
        "llama3.2",
        "llama3.1",
        "mistral-nemo",
        "qwen2.5",
        "command-r",
        "firefunction",
    ]

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API base URL
        """
        self.base_url = base_url.rstrip('/')

    def list_models(self, tool_compatible_only: bool = True) -> List[str]:
        """Get available models from Ollama.

        Args:
            tool_compatible_only: If True, filter to only models that support tools

        Returns:
            List of model names (e.g., ["llama3.2:latest", "mistral-nemo:latest"])

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            data = response.json()
            models = [model['name'] for model in data.get('models', [])]

            if tool_compatible_only:
                models = [m for m in models if self.check_model_supports_tools(m)]

            return sorted(models)

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to list models from Ollama: {e}"
            )

    def check_model_supports_tools(self, model: str) -> bool:
        """Check if a model supports tool calling.

        Args:
            model: Model name (e.g., "llama3.2:latest")

        Returns:
            True if model supports tools, False otherwise
        """
        # Extract base model name (before the colon)
        base_name = model.split(':')[0] if ':' in model else model

        # Check if base name is in our list of tool-compatible models
        return any(
            base_name.lower().startswith(compatible.lower())
            for compatible in self.TOOL_COMPATIBLE_MODELS
        )

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate completion from Ollama.

        Args:
            model: Model name
            prompt: Input prompt
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Generated text

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": stream
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()
            return data.get('response', '')

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to generate response from Ollama: {e}"
            )

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Chat completion from Ollama with tool calling support.

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            stream: Whether to stream the response
            tools: Optional list of tool definitions for function calling

        Returns:
            Response dict with 'message' and optional 'tool_calls'

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }

            # Add tools if provided
            if tools:
                payload["tools"] = tools

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()

            # Extract message from response
            message = data.get('message', {})

            return {
                "message": message,
                "done": data.get('done', True)
            }

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to chat with Ollama: {e}"
            )

    def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_registry: Dict[str, Callable]
    ) -> str:
        """Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            tool_registry: Dictionary mapping tool names to functions

        Returns:
            Tool execution result as JSON string

        Raises:
            ValueError: If tool not found in registry
            Exception: If tool execution fails
        """
        if tool_name not in tool_registry:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        try:
            tool_function = tool_registry[tool_name]
            result = tool_function(**arguments)

            # Convert result to JSON string
            return json.dumps(result)

        except Exception as e:
            error_result = {
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments
            }
            return json.dumps(error_result)

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Ollama API.

        Returns:
            Tuple of (is_connected, message)
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, "Ollama is running"
            else:
                return False, f"Ollama returned status code {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Ollama at {self.base_url}"
        except requests.exceptions.Timeout:
            return False, f"Connection to Ollama at {self.base_url} timed out"
        except Exception as e:
            return False, f"Error connecting to Ollama: {e}"
