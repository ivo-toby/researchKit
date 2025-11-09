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
- [ ] Create `src/ollama_agent/ollama_client.py` - Ollama API client
- [ ] Create `src/ollama_agent/conversation.py` - Conversation engine
- [ ] Create `src/ollama_agent/workflow.py` - Workflow orchestrator
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

- [ ] Constructor: `__init__(base_url: str)`
  - Store base URL
  - Initialize session if needed

- [ ] Method: `list_models() -> List[str]`
  - GET request to `/api/tags`
  - Parse response JSON
  - Extract model names
  - Handle errors (connection, timeout, invalid JSON)
  - Return list of model names

- [ ] Method: `generate(model, prompt, temperature, stream) -> str`
  - POST request to `/api/generate`
  - Build request payload
  - Handle streaming vs non-streaming
  - Parse response
  - Return generated text

- [ ] Method: `chat(model, messages, temperature, stream) -> str`
  - POST request to `/api/chat`
  - Format messages array
  - Handle conversation context
  - Parse response
  - Return assistant message

- [ ] Error handling:
  - Connection errors
  - Timeout errors
  - Invalid responses
  - Model not found errors

### 5. Conversation Engine (`conversation.py`)

#### Class: `ConversationEngine`

- [ ] Constructor: `__init__(ollama_client, config)`
  - Store client and config
  - Initialize message history

- [ ] Method: `add_system_message(content: str) -> None`
  - Append system message to history

- [ ] Method: `add_user_message(content: str) -> None`
  - Append user message to history

- [ ] Method: `generate_response() -> str`
  - Call ollama_client.chat with message history
  - Append assistant response to history
  - Return response text

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

### 6. Workflow Orchestrator (`workflow.py`)

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
  - Test generate method (with mock)
  - Test chat method (with mock)
  - Test error handling

- [ ] Create `tests/test_conversation.py`
  - Test message history management
  - Test approval loop logic (with mock input)
  - Test display formatting

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

- [ ] Test: Fresh folder, no git
- [ ] Test: Git repo exists, no .researchkit/
- [ ] Test: .researchkit/ exists, no config
- [ ] Test: Config exists, returning user
- [ ] Test: Model selection flow
- [ ] Test: Constitution approval loop
- [ ] Test: Constitution edit mode
- [ ] Test: Constitution feedback loop
- [ ] Test: Plan generation
- [ ] Test: Plan approval/feedback
- [ ] Test: Execute phase workflow
- [ ] Test: Synthesis generation
- [ ] Test: Git commits at each phase
- [ ] Test: Error handling - Ollama not running
- [ ] Test: Error handling - Invalid model
- [ ] Test: Error handling - Bash script failures
- [ ] Test: OLLAMA_URL environment variable
- [ ] Test: EDITOR environment variable

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
- [ ] Works without internet connection (fully local)

---

## Completion Status

**Total Items**: TBD (count after all checkboxes defined)
**Completed**: 0
**In Progress**: 0
**Blocked**: 0

**Estimated Effort**: 6 days
**Actual Effort**: TBD

---

**Last Updated**: 2025-11-09
**Status**: Planning Phase
