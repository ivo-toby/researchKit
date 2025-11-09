# ResearchKit Tests

This directory contains unit tests for ResearchKit and the Ollama Agent.

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/ollama_agent/test_config.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test

```bash
pytest tests/ollama_agent/test_config.py::TestOllamaConfig::test_validate_valid_config
```

## Test Structure

```
tests/
├── ollama_agent/
│   ├── test_config.py          # Config management tests
│   ├── test_ollama_client.py   # Ollama API client tests
│   └── test_tools.py            # Research tools tests
└── README.md
```

## Writing Tests

### Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
import pytest
from ollama_agent.config import OllamaConfig

class TestOllamaConfig:
    def test_default_values(self):
        config = OllamaConfig()
        assert config.version == "1.0"
        assert config.model == ""
```

### Using Mocks

```python
from unittest.mock import patch, MagicMock

@patch('ollama_agent.tools.web_search.DDGS')
def test_web_search(mock_ddgs):
    mock_instance = MagicMock()
    mock_instance.text.return_value = [{"title": "Test"}]
    mock_ddgs.return_value.__enter__.return_value = mock_instance

    result = web_search("test")
    assert result["success"] is True
```

## Test Coverage

Current test coverage includes:

### Ollama Agent
- **Config Management** (`test_config.py`)
  - Configuration validation
  - Save/load operations
  - Error handling

- **Ollama Client** (`test_ollama_client.py`)
  - Model listing and filtering
  - Tool-compatible model detection
  - Chat API interaction
  - Tool calling support

- **Research Tools** (`test_tools.py`)
  - Web search (DuckDuckGo)
  - URL fetching and parsing
  - PDF downloading and extraction
  - Tool registry and definitions

## Continuous Integration

Tests are designed to run in CI/CD environments. Mock external dependencies (Ollama API, web requests, file I/O) to ensure tests are:

- **Fast**: No network calls or heavy I/O
- **Reliable**: No external dependencies
- **Isolated**: Each test is independent

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=src`
4. Aim for >80% coverage on new code
5. Include both success and error test cases

## Troubleshooting

### Import Errors

If you see import errors, install the package in development mode:

```bash
pip install -e .
```

### Mock Issues

When mocking, ensure you patch the correct import path:

```python
# Patch where it's used, not where it's defined
@patch('ollama_agent.tools.web_search.DDGS')  # Correct
@patch('duckduckgo_search.DDGS')              # Wrong
```

### Fixture Conflicts

If fixtures conflict, use unique names or scope them appropriately:

```python
@pytest.fixture(scope="function")  # Per-test isolation
@pytest.fixture(scope="module")    # Shared across module
```
