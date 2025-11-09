# Ollama Standalone Agent - Deliverables Checklist

## Overview

This document tracks all deliverables for the Ollama standalone agent implementation. Each item should be checked off when completed, tested, and committed to the repository.

## Core Components

### 1. Package Structure

- [ ] Create `src/ollama_agent/` package directory
- [ ] Create `src/ollama_agent/__init__.py` with package metadata
- [ ] Create `src/ollama_agent/cli.py` - Main CLI entry point
- [ ] Create `src/ollama_agent/environment.py` - Environment checking
- [ ] Create `src/ollama_agent/config.py` - Configuration management
- [ ] Create `src/ollama_agent/ollama_client.py` - Ollama API client with tool calling
- [ ] Create `src/ollama_agent/conversation.py` - Conversation engine with tool execution
- [ ] Create `src/ollama_agent/workflow.py` - Workflow orchestrator
- [ ] Create `src/ollama_agent/tools/` directory
- [ ] Create `src/ollama_agent/tools/__init__.py` - Tool registry
- [ ] Create `src/ollama_agent/tools/web_search.py` - Web search tool
- [ ] Create `src/ollama_agent/tools/url_fetch.py` - URL fetching tool
- [ ] Create `src/ollama_agent/tools/pdf_parser.py` - PDF parsing tool
- [ ] Create `src/ollama_agent/prompts/` directory
- [ ] Create `src/ollama_agent/prompts/__init__.py`
- [ ] Create `src/ollama_agent/prompts/constitution.py` - Constitution prompts
- [ ] Create `src/ollama_agent/prompts/plan.py` - Planning prompts
- [ ] Create `src/ollama_agent/prompts/execute.py` - Execution prompts
- [ ] Create `src/ollama_agent/prompts/synthesize.py` - Synthesis prompts

### 2. Environment Manager (`environment.py`)

#### Class: `EnvironmentManager`

- [ ] Method: `check_ollama(url: str) -> bool`
  - Check if Ollama API is accessible
  - Validate response from `/api/tags`
  - Handle connection errors gracefully

- [ ] Method: `check_git() -> bool`
  - Verify git is installed
  - Check if current directory is a git repo
  - Return status

- [ ] Method: `prompt_git_init() -> bool`
  - Display prompt to user
  - Execute `git init` if user confirms
  - Return success status

- [ ] Method: `check_researchkit_initialized() -> bool`
  - Check for `.researchkit/` directory
  - Verify required subdirectories exist
  - Return initialization status

- [ ] Method: `initialize_researchkit() -> None`
  - Create `.researchkit/config/` directory
  - Copy templates if needed
  - Ensure bash scripts are in place

### 3. Config Manager (`config.py`)

#### Dataclass: `OllamaConfig`

- [ ] Define dataclass with fields:
  - `version: str`
  - `ollama_url: str`
  - `model: str`
  - `temperature: float`
  - `top_p: float`
  - `num_ctx: int`
  - `created_at: str`
  - `updated_at: str`

- [ ] Add validation methods
- [ ] Add to_dict() and from_dict() methods

#### Class: `ConfigManager`

- [ ] Constant: `CONFIG_PATH = Path(".researchkit/config/ollama.json")`

- [ ] Method: `exists() -> bool`
  - Check if config file exists

- [ ] Method: `load() -> Optional[OllamaConfig]`
  - Read JSON file
  - Parse into OllamaConfig
  - Handle missing/corrupted files
  - Return None if not found

- [ ] Method: `save(config: OllamaConfig) -> None`
  - Create parent directories if needed
  - Serialize config to JSON
  - Write to file with proper formatting
  - Set updated_at timestamp

### 4. Ollama Client (`ollama_client.py`)

#### Class: `OllamaClient`

- [ ] Class constant: `TOOL_COMPATIBLE_MODELS`
  - List of models that support tool calling
  - ["llama3.2", "llama3.1", "mistral-nemo", "qwen2.5", "command-r", "firefunction"]

- [ ] Constructor: `__init__(base_url: str)`
  - Store base URL
  - Initialize session if needed

- [ ] Method: `list_models(tool_compatible_only: bool = True) -> List[str]`
  - GET request to `/api/tags`
  - Parse response JSON
  - Extract model names
  - Filter for tool-compatible models if requested
  - Handle errors (connection, timeout, invalid JSON)
  - Return list of model names

- [ ] Method: `check_model_supports_tools(model: str) -> bool`
  - Check if model name matches any in TOOL_COMPATIBLE_MODELS
  - Return True if compatible, False otherwise

- [ ] Method: `generate(model, prompt, temperature, stream) -> str`
  - POST request to `/api/generate`
  - Build request payload
  - Handle streaming vs non-streaming
  - Parse response
  - Return generated text

- [ ] Method: `chat(model, messages, temperature, stream, tools) -> Dict[str, Any]`
  - POST request to `/api/chat`
  - Format messages array
  - Include tools parameter if provided
  - Handle conversation context
  - Parse response (including tool_calls if present)
  - Return full response dict with message and tool_calls

- [ ] Method: `execute_tool_call(tool_name, arguments, tool_registry) -> str`
  - Look up tool in registry
  - Execute tool with arguments
  - Handle tool execution errors
  - Return result as string

- [ ] Error handling:
  - Connection errors
  - Timeout errors
  - Invalid responses
  - Model not found errors
  - Tool execution errors

### 5. Research Tools (`tools/`)

#### Tool Registry (`tools/__init__.py`)

- [ ] Import all tool functions
- [ ] Create `TOOL_REGISTRY` dict mapping names to functions
- [ ] Create `TOOL_DEFINITIONS` list with OpenAI-compatible tool schemas
- [ ] Export all tools and registries

#### Web Search Tool (`tools/web_search.py`)

- [ ] Function: `web_search(query: str, max_results: int = 10) -> Dict[str, Any]`
  - Implement DuckDuckGo search integration
  - Return results with title, URL, snippet, source
  - Handle search errors gracefully
  - Limit results to max_results

- [ ] Function: `get_tool_definition() -> Dict`
  - Return OpenAI-compatible function schema
  - Include parameter descriptions
  - Specify required parameters

#### URL Fetch Tool (`tools/url_fetch.py`)

- [ ] Function: `fetch_url(url: str, extract_text: bool = True) -> Dict[str, Any]`
  - Download page content with requests
  - Parse HTML with BeautifulSoup
  - Extract clean text (remove scripts, nav, etc.)
  - Return URL, title, content, metadata
  - Handle HTTP errors, timeouts

- [ ] Function: `get_tool_definition() -> Dict`
  - Return OpenAI-compatible function schema
  - Document extract_text parameter

#### PDF Parser Tool (`tools/pdf_parser.py`)

- [ ] Function: `parse_pdf(url: str, save_path: Optional[str] = None) -> Dict[str, Any]`
  - Download PDF from URL
  - Extract text with pypdf
  - Extract metadata (title, author, created date)
  - Optionally save to local path
  - Return text, page count, metadata
  - Handle malformed PDFs, download errors

- [ ] Function: `get_tool_definition() -> Dict`
  - Return OpenAI-compatible function schema
  - Document save_path parameter

### 6. Conversation Engine (`conversation.py`)

#### Class: `ConversationEngine`

- [ ] Constructor: `__init__(ollama_client, config, tool_registry, tool_definitions)`
  - Store client, config, tool registry, and tool definitions
  - Initialize message history

- [ ] Method: `add_system_message(content: str) -> None`
  - Append system message to history

- [ ] Method: `add_user_message(content: str) -> None`
  - Append user message to history

- [ ] Method: `generate_response(use_tools: bool = True) -> str`
  - Call ollama_client.chat with message history and tools
  - If response contains tool_calls:
    - Execute each tool call
    - Add tool results to message history
    - Call ollama_client.chat again
    - Repeat until no more tool calls
  - Append final assistant response to history
  - Return final response text

- [ ] Method: `execute_tool_calls(tool_calls: List[Dict]) -> List[Dict]`
  - For each tool call:
    - Extract tool name and arguments
    - Look up tool in registry
    - Execute tool function
    - Display tool execution to user (e.g., "🔍 Searching for: query")
    - Collect result
  - Return list of tool result messages

- [ ] Method: `approval_loop(content, prompt, allow_edit) -> Tuple[str, bool]`
  - Display content to user
  - Show approval prompt
  - Handle user input:
    - `y` → return (content, True)
    - `e` → open in $EDITOR, return (edited_content, True)
    - `f` → prompt for feedback, regenerate, loop
    - `s` → return (content, False) for skip
  - Loop until approved or skipped

- [ ] Method: `display(content: str, title: str) -> None`
  - Use rich library for formatting
  - Display title with styling
  - Display content with markdown rendering
  - Add separator lines

- [ ] Method: `clear_history() -> None`
  - Reset message history for new phase

### 7. Workflow Orchestrator (`workflow.py`)

#### Class: `WorkflowOrchestrator`

- [ ] Constructor: `__init__(conversation, config)`
  - Store conversation engine and config
  - Initialize state tracking

- [ ] Method: `run_constitution_phase() -> bool`
  - Load existing constitution if present
  - Set system prompt from prompts.constitution
  - Generate constitution with Ollama
  - Run approval loop
  - Save to `.researchkit/memory/constitution.md`
  - Git add and commit
  - Return success status

- [ ] Method: `run_plan_phase(topic: str) -> bool`
  - Call `.researchkit/scripts/bash/plan.sh` with topic
  - Load plan template
  - Set system prompt with constitution and template
  - Generate research plan with Ollama
  - Run approval loop
  - Save to plan.md in research directory
  - Git add and commit
  - Return success status

- [ ] Method: `run_execute_phase() -> bool`
  - Call `.researchkit/scripts/bash/execute.sh`
  - Load plan.md to understand objectives
  - For each research objective:
    - Generate search queries with Ollama
    - Get user approval for queries
    - Simulate/document findings
    - Run approval loop for each finding
  - Update findings.md
  - Update sources.md
  - Git add and commit
  - Return success status

- [ ] Method: `run_synthesize_phase() -> bool`
  - Call `.researchkit/scripts/bash/synthesize.sh`
  - Load plan.md, findings.md, sources.md, constitution.md
  - Set system prompt for synthesis
  - Generate final report with Ollama
  - Run approval loop
  - Save to synthesis.md
  - Copy to root with timestamped filename
  - Git add and commit
  - Return success status

- [ ] Method: `run_full_workflow(topic: str) -> None`
  - Print phase header
  - Run constitution phase
  - Run plan phase with topic
  - Run execute phase
  - Run synthesize phase
  - Print completion message

### 7. Prompt Templates (`prompts/`)

- [ ] `constitution.py`:
  - `CONSTITUTION_SYSTEM_PROMPT` constant
  - `CONSTITUTION_USER_PROMPT` constant
  - Formatting helpers

- [ ] `plan.py`:
  - `PLAN_SYSTEM_PROMPT` constant
  - `PLAN_USER_PROMPT` constant
  - Template variable substitution

- [ ] `execute.py`:
  - `EXECUTE_SYSTEM_PROMPT` constant
  - `EXECUTE_USER_PROMPT` constant
  - Query generation prompts

- [ ] `synthesize.py`:
  - `SYNTHESIZE_SYSTEM_PROMPT` constant
  - `SYNTHESIZE_USER_PROMPT` constant
  - Report formatting guidelines

### 8. CLI Entry Point (`cli.py`)

- [ ] Function: `prompt_yes_no(question: str) -> bool`
  - Display question with [y/N] format
  - Read user input
  - Return boolean

- [ ] Function: `prompt_model_selection(models: List[str]) -> str`
  - Display numbered list of models
  - Read user selection (1-N)
  - Validate input
  - Return selected model name

- [ ] Function: `get_ollama_url() -> str`
  - Check OLLAMA_URL environment variable
  - Return env var if set, else default

- [ ] Function: `main() -> None`
  - Print banner with version
  - Initialize EnvironmentManager
  - Check Ollama (exit if not running)
  - Check git (prompt to init if needed)
  - Check researchKit (prompt to init if needed)
  - Initialize ConfigManager
  - If config doesn't exist:
    - List available models
    - Prompt user to select model
    - Create config
    - Save config
    - Git commit config
  - Else:
    - Load existing config
  - Prompt for research topic
  - Initialize OllamaClient
  - Initialize ConversationEngine
  - Initialize WorkflowOrchestrator
  - Run full workflow
  - Print completion message

- [ ] Add argparse/click for CLI arguments:
  - `--version`: Show version
  - `--help`: Show help
  - `--no-color`: Disable rich formatting
  - `--model MODEL`: Override model from config

### 9. Package Configuration

- [ ] Update `pyproject.toml`:
  - Add `ollama_agent` to packages
  - Add `research-ollama = "ollama_agent.cli:main"` to scripts
  - Add dependencies:
    - `requests>=2.31.0`
    - `rich>=13.0.0`

- [ ] Update `src/ollama_agent/__init__.py`:
  - Add `__version__` constant
  - Add package docstring
  - Export main classes

## Testing

### Unit Tests

- [ ] Create `tests/test_environment.py`
  - Test Ollama connectivity checking
  - Test git initialization prompting
  - Test researchKit folder detection

- [ ] Create `tests/test_config.py`
  - Test config save/load cycle
  - Test missing config handling
  - Test config validation

- [ ] Create `tests/test_ollama_client.py`
  - Test model listing (with mock)
  - Test model filtering for tool compatibility
  - Test generate method (with mock)
  - Test chat method (with mock)
  - Test chat with tools (with mock)
  - Test tool execution
  - Test error handling

- [ ] Create `tests/test_tools.py`
  - Test web_search with mock DuckDuckGo
  - Test fetch_url with mock requests
  - Test parse_pdf with mock PDF file
  - Test tool definition schemas
  - Test error handling in each tool

- [ ] Create `tests/test_conversation.py`
  - Test message history management
  - Test approval loop logic (with mock input)
  - Test display formatting
  - Test tool execution in conversation flow
  - Test multi-turn tool calling

- [ ] Create `tests/test_workflow.py`
  - Test individual phase execution (with mocks)
  - Test full workflow integration

### Integration Tests

- [ ] Create `tests/integration/test_full_workflow.py`
  - Test complete workflow in temp directory
  - Mock Ollama responses
  - Verify all files created
  - Verify git commits

### Manual Testing Checklist

**Ollama Agent Functionality:**

- [ ] Test: Fresh folder, no git
- [ ] Test: Git repo exists, no .researchkit/
- [ ] Test: .researchkit/ exists, no config
- [ ] Test: Config exists, returning user
- [ ] Test: Model selection flow (tool-compatible models only)
- [ ] Test: No tool-compatible models available
- [ ] Test: Constitution approval loop
- [ ] Test: Constitution edit mode
- [ ] Test: Constitution feedback loop
- [ ] Test: Plan generation
- [ ] Test: Plan approval/feedback
- [ ] Test: Execute phase workflow with tools
- [ ] Test: Web search tool execution
- [ ] Test: URL fetch tool execution
- [ ] Test: PDF parse tool execution
- [ ] Test: Sources.md updated with URLs and PDFs
- [ ] Test: Synthesis generation
- [ ] Test: Git commits at each phase
- [ ] Test: Error handling - Ollama not running
- [ ] Test: Error handling - Invalid model
- [ ] Test: Error handling - Bash script failures
- [ ] Test: Error handling - Web search failure
- [ ] Test: Error handling - URL fetch failure (404, timeout)
- [ ] Test: Error handling - PDF parse failure (malformed PDF)
- [ ] Test: OLLAMA_URL environment variable
- [ ] Test: EDITOR environment variable

**Backward Compatibility & Non-Interference:**

- [ ] Test: `research init` still works after installing ollama_agent
- [ ] Test: `research check` still works after installing ollama_agent
- [ ] Test: Both `research` and `research-ollama` commands available
- [ ] Test: Existing .researchkit/ projects work with both workflows
- [ ] Test: Claude Code slash commands still work
- [ ] Test: Ollama config file doesn't interfere with existing workflows
- [ ] Test: Can use `research init` and `research-ollama` in different projects
- [ ] Test: Bash scripts (plan.sh, execute.sh, synthesize.sh) work for both

## Documentation

- [ ] Create `docs/ollama-agent-guide.md`:
  - Installation instructions
  - Quick start guide
  - Configuration reference
  - Troubleshooting section

- [ ] Update main `README.md`:
  - Add Ollama agent section
  - Link to detailed guide
  - Add installation instructions

- [ ] Create `examples/ollama-agent-demo.md`:
  - Show example session
  - Demonstrate feedback loops
  - Show expected output

- [ ] Add inline code documentation:
  - Docstrings for all classes
  - Docstrings for all public methods
  - Type hints throughout

## CI/CD

- [ ] Update GitHub Actions workflow (if exists):
  - Add ollama_agent tests to test suite
  - Install Ollama in CI environment (if feasible)
  - Run integration tests

- [ ] Add pre-commit hooks (if not exists):
  - Black formatting
  - Flake8 linting
  - Type checking with mypy

## Release Preparation

- [ ] Update `CHANGELOG.md`:
  - Add entry for Ollama agent feature
  - Document new command `research-ollama`
  - List all new components

- [ ] Version bump:
  - Update version in `pyproject.toml`
  - Update version in `src/ollama_agent/__init__.py`

- [ ] Create migration guide (if needed):
  - Explain new config file location
  - Document environment variables

## Quality Gates

### Before Merge

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing checklist complete
- [ ] Code coverage > 80%
- [ ] Documentation complete
- [ ] No linting errors
- [ ] Type hints validated with mypy
- [ ] Code reviewed by at least one person

### Before Release

- [ ] Version numbers updated
- [ ] CHANGELOG updated
- [ ] README updated
- [ ] Example documentation tested
- [ ] Installation tested on clean environment
- [ ] Works with latest Ollama version

## Dependencies Verification

- [ ] Verify Ollama API compatibility:
  - Test with Ollama 0.1.x
  - Test with latest Ollama version
  - Document minimum supported version

- [ ] Verify Python version compatibility:
  - Test with Python 3.9
  - Test with Python 3.10
  - Test with Python 3.11
  - Test with Python 3.12

- [ ] Verify platform compatibility:
  - Test on Linux
  - Test on macOS
  - Test on Windows (if applicable)

## File Checklist

### New Files to Create

```
src/ollama_agent/
├── __init__.py                          [ ]
├── cli.py                               [ ]
├── environment.py                       [ ]
├── config.py                            [ ]
├── ollama_client.py                     [ ]
├── conversation.py                      [ ]
├── workflow.py                          [ ]
├── tools/
│   ├── __init__.py                      [ ]
│   ├── web_search.py                    [ ]
│   ├── url_fetch.py                     [ ]
│   └── pdf_parser.py                    [ ]
└── prompts/
    ├── __init__.py                      [ ]
    ├── constitution.py                  [ ]
    ├── plan.py                          [ ]
    ├── execute.py                       [ ]
    └── synthesize.py                    [ ]

tests/
├── test_environment.py                  [ ]
├── test_config.py                       [ ]
├── test_ollama_client.py                [ ]
├── test_tools.py                        [ ]
├── test_conversation.py                 [ ]
├── test_workflow.py                     [ ]
└── integration/
    └── test_full_workflow.py            [ ]

docs/
└── ollama-agent-guide.md                [ ]

examples/
└── ollama-agent-demo.md                 [ ]
```

### Files to Modify

```
pyproject.toml                           [ ]
README.md                                [ ]
CHANGELOG.md                             [ ]
```

## Success Metrics

- [ ] `research-ollama` command runs successfully
- [ ] Full workflow completes without errors
- [ ] Config persists across sessions
- [ ] All git commits created correctly
- [ ] Approval loops work as expected
- [ ] Error messages are helpful
- [ ] Tool calling works correctly (web_search, fetch_url, parse_pdf)
- [ ] Only tool-compatible models shown in selection
- [ ] Web research functional during execution phase
- [ ] Sources.md updated with URLs and PDFs automatically
- [ ] Agent can search, fetch URLs, and parse PDFs

---

## Completion Status

**Total Items**: TBD (count after all checkboxes defined)
**Completed**: 0
**In Progress**: 0
**Blocked**: 0

**Estimated Effort**: 9 days
**Actual Effort**: TBD

---

**Last Updated**: 2025-11-09
**Status**: Planning Phase - Version 2.0

## Changelog

### Version 2.0 (2025-11-09)
- Added Research Tools section (web_search, fetch_url, parse_pdf)
- Updated OllamaClient with tool calling support
- Updated ConversationEngine with tool execution
- Added tool-related tests
- Updated manual testing checklist
- Updated success metrics
- Increased estimated effort from 6 to 9 days

### Version 1.0 (2025-11-09)
- Initial deliverables checklist
