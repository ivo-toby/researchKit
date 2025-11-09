# Ollama Standalone Agent - Technical Specification

## Overview

This document specifies a lightweight standalone agent that uses Ollama for LLM interactions and integrates with researchKit's research workflow. The agent provides a fully interactive terminal-based experience for conducting research using local Ollama models.

## Goals

1. **Standalone Operation**: Run entirely from the terminal without external AI service dependencies
2. **Local LLM Integration**: Use Ollama for all AI interactions
3. **ResearchKit Compatibility**: Leverage existing researchKit workflows (constitution, plan, execute, synthesize)
4. **User Control**: Provide approval/feedback loops at each research phase
5. **Configuration Persistence**: Store Ollama settings in version-controlled config files

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Ollama Agent CLI                         │
│                 (research-ollama command)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│Environment  │  │Conversation │  │  Workflow   │
│   Manager   │  │   Engine    │  │ Orchestrator│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Config    │  │   Ollama    │  │    Bash     │
│   Manager   │  │     API     │  │   Scripts   │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Component Responsibilities

1. **Environment Manager**: Checks git initialization, folder structure, Ollama availability
2. **Config Manager**: Handles `.researchkit/config/ollama.json` storage and retrieval
3. **Conversation Engine**: Manages multi-turn conversations with user approval loops
4. **Ollama API Client**: Handles HTTP requests to Ollama API
5. **Workflow Orchestrator**: Coordinates constitution → plan → execute → synthesize phases

## User Flows

### Flow 1: First-Time Setup (Uninitialized Folder)

```
1. User runs: research-ollama
2. Agent checks environment:
   - ✓ Ollama running? (curl http://localhost:11434/api/tags)
   - ✓ Git installed?
   - ✓ .git/ exists in current directory?
3. If .git/ missing:
   → "This folder is not a git repository. Initialize one? [y/N]"
   → If yes: run `git init`
   → If no: exit with instructions
4. Check for .researchkit/ folder
5. If missing:
   → "Initialize researchKit in this folder? [y/N]"
   → If yes: run initialization (create folder structure)
6. Query Ollama for available models:
   → GET http://localhost:11434/api/tags
   → Display list: "Select a model to use:"
      1. llama3.2:latest
      2. mistral:latest
      3. codellama:latest
   → User selects (1-3)
7. Save config to .researchkit/config/ollama.json:
   {
     "ollama_url": "http://localhost:11434",
     "model": "llama3.2:latest",
     "temperature": 0.7,
     "created_at": "2025-11-09T..."
   }
8. Commit config: git add .researchkit/config/ && git commit -m "chore: Initialize Ollama agent config"
9. Start research workflow (see Flow 3)
```

### Flow 2: Returning User (Already Initialized)

```
1. User runs: research-ollama
2. Agent checks environment:
   - ✓ .researchkit/ exists
   - ✓ .researchkit/config/ollama.json exists
   - ✓ Ollama running
3. Load config from ollama.json
4. Display: "What would you like to research?"
5. User enters research topic
6. Start research workflow (see Flow 3)
```

### Flow 3: Research Workflow with Feedback Loops

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: CONSTITUTION                                        │
└──────────────────────────────────────────────────────────────┘
1. Agent: "Let's define the research methodology."
2. Agent reads: .researchkit/memory/constitution.md (if exists)
3. Agent asks Ollama to analyze and suggest improvements
4. Display to user: [Constitution content]
5. User approval loop:
   → "Approve? [y]es / [e]dit / [f]eedback"
   → If y: Save and continue
   → If e: Open in $EDITOR, then continue
   → If f: User provides feedback, agent re-generates with Ollama
   → Loop until approved
6. Save to .researchkit/memory/constitution.md
7. Commit: git add .researchkit/memory/ && git commit -m "docs: Update research constitution"

┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: PLAN                                                │
└──────────────────────────────────────────────────────────────┘
1. Agent: "Creating research plan for: [topic]"
2. Call bash script: .researchkit/scripts/bash/plan.sh "[topic]"
   → Creates branch: research/001-topic-slug
   → Creates: .researchkit/research/001-topic-slug/plan.md
   → Creates: .researchkit/research/001-topic-slug/sources.md
3. Agent sends to Ollama:
   - Topic: [user input]
   - Constitution: [constitution.md content]
   - Template: [plan-template.md structure]
4. Agent generates research plan via Ollama
5. Display plan to user
6. User approval loop:
   → "Approve plan? [y]es / [e]dit / [f]eedback"
   → If y: Save and continue
   → If e: Open plan.md in $EDITOR, then continue
   → If f: User provides feedback, agent revises with Ollama
7. Save to .researchkit/research/001-topic-slug/plan.md
8. Commit: git add . && git commit -m "docs: Add research plan for [topic]"

┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: EXECUTE                                             │
└──────────────────────────────────────────────────────────────┘
1. Call bash script: .researchkit/scripts/bash/execute.sh
   → Creates: findings.md from execution-template.md
2. Agent reads plan.md to understand research objectives
3. Agent conducts research with Ollama:
   - For each research question in plan:
     → Agent proposes search queries
     → User approves: "Search for: '[query]'? [y]es / [e]dit / [s]kip"
     → Agent documents findings in findings.md
     → After each finding:
        "Document this finding? [y]es / [e]dit / [f]eedback / [s]kip"
4. Agent updates sources.md with bibliography
5. Display findings summary
6. User approval loop:
   → "Approve findings? [y]es / [e]dit / [f]eedback"
7. Save findings.md and sources.md
8. Commit: git add . && git commit -m "docs: Document research findings"

┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: SYNTHESIZE                                          │
└──────────────────────────────────────────────────────────────┘
1. Call bash script: .researchkit/scripts/bash/synthesize.sh
   → Creates: synthesis.md from synthesis-template.md
2. Agent reads:
   - plan.md (research objectives)
   - findings.md (research data)
   - sources.md (bibliography)
   - constitution.md (methodology)
3. Agent sends to Ollama: "Synthesize research findings into final report"
4. Display synthesis to user
5. User approval loop:
   → "Approve synthesis? [y]es / [e]dit / [f]eedback"
6. Save synthesis.md
7. Copy to root: [topic-slug]-synthesis-[date].md
8. Commit: git add . && git commit -m "docs: Complete research synthesis for [topic]"
9. Display: "Research complete! Final report: [filename].md"
```

## Technical Implementation

### File Structure

```
researchKit/
├── src/
│   └── ollama_agent/
│       ├── __init__.py              # Package init
│       ├── cli.py                   # Main CLI entry point
│       ├── environment.py           # Environment checking
│       ├── config.py                # Config management
│       ├── ollama_client.py         # Ollama API client
│       ├── conversation.py          # Conversation engine
│       ├── workflow.py              # Workflow orchestrator
│       └── prompts/
│           ├── __init__.py
│           ├── constitution.py      # Constitution phase prompts
│           ├── plan.py              # Planning phase prompts
│           ├── execute.py           # Execution phase prompts
│           └── synthesize.py        # Synthesis phase prompts
├── .researchkit/
│   └── config/
│       └── ollama.json              # Ollama configuration (git-tracked)
└── pyproject.toml                   # Updated with ollama-agent entry point
```

### Configuration Format

**`.researchkit/config/ollama.json`**:

```json
{
  "version": "1.0",
  "ollama_url": "http://localhost:11434",
  "model": "llama3.2:latest",
  "temperature": 0.7,
  "top_p": 0.9,
  "num_ctx": 4096,
  "created_at": "2025-11-09T12:00:00Z",
  "updated_at": "2025-11-09T12:00:00Z"
}
```

### API Design

#### 1. Environment Manager (`environment.py`)

```python
class EnvironmentManager:
    """Checks and initializes the research environment."""

    def check_ollama(self, url: str = "http://localhost:11434") -> bool:
        """Check if Ollama is running and accessible."""

    def check_git(self) -> bool:
        """Check if git is installed and repo is initialized."""

    def prompt_git_init(self) -> bool:
        """Ask user to initialize git repo. Returns True if initialized."""

    def check_researchkit_initialized(self) -> bool:
        """Check if .researchkit/ structure exists."""

    def initialize_researchkit(self) -> None:
        """Create .researchkit/ folder structure."""
```

#### 2. Config Manager (`config.py`)

```python
@dataclass
class OllamaConfig:
    """Ollama agent configuration."""
    version: str = "1.0"
    ollama_url: str = "http://localhost:11434"
    model: str = ""
    temperature: float = 0.7
    top_p: float = 0.9
    num_ctx: int = 4096
    created_at: str = ""
    updated_at: str = ""

class ConfigManager:
    """Manages Ollama configuration persistence."""

    CONFIG_PATH = Path(".researchkit/config/ollama.json")

    def load(self) -> Optional[OllamaConfig]:
        """Load config from file. Returns None if not found."""

    def save(self, config: OllamaConfig) -> None:
        """Save config to file."""

    def exists(self) -> bool:
        """Check if config file exists."""
```

#### 3. Ollama Client (`ollama_client.py`)

```python
class OllamaClient:
    """HTTP client for Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def list_models(self) -> List[str]:
        """Get available models from Ollama.

        GET /api/tags
        Returns: ["llama3.2:latest", "mistral:latest", ...]
        """

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate completion from Ollama.

        POST /api/generate
        {
            "model": "llama3.2:latest",
            "prompt": "...",
            "temperature": 0.7,
            "stream": false
        }
        """

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Chat completion from Ollama.

        POST /api/chat
        {
            "model": "llama3.2:latest",
            "messages": [
                {"role": "user", "content": "..."}
            ],
            "temperature": 0.7,
            "stream": false
        }
        """
```

#### 4. Conversation Engine (`conversation.py`)

```python
class ConversationEngine:
    """Manages interactive conversations with approval loops."""

    def __init__(self, ollama_client: OllamaClient, config: OllamaConfig):
        self.client = ollama_client
        self.config = config
        self.messages: List[Dict[str, str]] = []

    def add_system_message(self, content: str) -> None:
        """Add system message to conversation context."""

    def add_user_message(self, content: str) -> None:
        """Add user message to conversation context."""

    def generate_response(self) -> str:
        """Generate AI response using current conversation context."""

    def approval_loop(
        self,
        content: str,
        prompt: str = "Approve? [y]es / [e]dit / [f]eedback",
        allow_edit: bool = True
    ) -> Tuple[str, bool]:
        """Interactive approval loop.

        Returns: (final_content, approved)
        """

    def display(self, content: str, title: str = "") -> None:
        """Display content with formatting."""
```

#### 5. Workflow Orchestrator (`workflow.py`)

```python
class WorkflowOrchestrator:
    """Orchestrates the research workflow phases."""

    def __init__(
        self,
        conversation: ConversationEngine,
        config: OllamaConfig
    ):
        self.conversation = conversation
        self.config = config

    def run_constitution_phase(self) -> bool:
        """Guide user through constitution definition.

        Returns: True if completed successfully
        """

    def run_plan_phase(self, topic: str) -> bool:
        """Create research plan with user approval.

        Args:
            topic: Research topic from user

        Returns: True if plan approved and saved
        """

    def run_execute_phase(self) -> bool:
        """Execute research with iterative findings.

        Returns: True if research completed
        """

    def run_synthesize_phase(self) -> bool:
        """Synthesize findings into final report.

        Returns: True if synthesis approved
        """

    def run_full_workflow(self, topic: str) -> None:
        """Run complete workflow: constitution → plan → execute → synthesize."""
```

#### 6. CLI Entry Point (`cli.py`)

```python
def main():
    """Main entry point for research-ollama CLI."""

    # 1. Environment checks
    env = EnvironmentManager()

    if not env.check_ollama():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not env.check_git():
        if not env.prompt_git_init():
            sys.exit(1)

    if not env.check_researchkit_initialized():
        if prompt_yes_no("Initialize researchKit?"):
            env.initialize_researchkit()
        else:
            sys.exit(1)

    # 2. Config management
    config_mgr = ConfigManager()

    if not config_mgr.exists():
        # First-time setup: model selection
        client = OllamaClient()
        models = client.list_models()
        selected_model = prompt_model_selection(models)

        config = OllamaConfig(
            model=selected_model,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        config_mgr.save(config)

        # Commit config
        subprocess.run(["git", "add", ".researchkit/config/"])
        subprocess.run([
            "git", "commit", "-m",
            "chore: Initialize Ollama agent config"
        ])
    else:
        config = config_mgr.load()

    # 3. Start research workflow
    client = OllamaClient(config.ollama_url)
    conversation = ConversationEngine(client, config)
    workflow = WorkflowOrchestrator(conversation, config)

    # Prompt for research topic
    topic = input("\n🔍 What would you like to research? ").strip()

    if not topic:
        print("No topic provided. Exiting.")
        sys.exit(0)

    # Run full workflow
    workflow.run_full_workflow(topic)

    print("\n✅ Research complete!")
```

### Environment Variable Support

The agent will respect the following environment variables:

- **`OLLAMA_URL`**: Override default Ollama URL (default: `http://localhost:11434`)
- **`OLLAMA_MODEL`**: Override model from config (for one-off runs)
- **`EDITOR`**: Text editor for manual edits (default: `vim` or `nano`)

Example usage:
```bash
OLLAMA_URL=http://192.168.1.100:11434 research-ollama
```

### Prompt Templates

#### Constitution Prompt (`prompts/constitution.py`)

```python
CONSTITUTION_SYSTEM_PROMPT = """
You are a research methodology expert. Your role is to help the user define
clear research principles including:

1. Citation standards (e.g., APA, MLA, Chicago)
2. Source quality requirements (peer-reviewed, primary sources, etc.)
3. Verification procedures (fact-checking, cross-referencing)
4. Research ethics (bias awareness, diverse perspectives)

The constitution should be concise (1-2 pages) but comprehensive.
Current constitution: {current_constitution}

If the user provides feedback, incorporate it and revise accordingly.
"""

CONSTITUTION_USER_PROMPT = """
Help me define a research constitution for this project.
{feedback}
"""
```

#### Plan Prompt (`prompts/plan.py`)

```python
PLAN_SYSTEM_PROMPT = """
You are a research planning expert. Create a detailed research plan that includes:

1. Research Question: Clear, focused question to investigate
2. Objectives: 3-5 specific goals
3. Methodology: How will research be conducted?
4. Key Topics: Main areas to investigate
5. Success Criteria: How to know when research is complete

Use the provided template structure and adhere to the research constitution.

Constitution: {constitution}
Template: {template}
"""

PLAN_USER_PROMPT = """
Research topic: {topic}
{feedback}
"""
```

## Dependencies

### New Python Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "requests>=2.31.0",      # For Ollama HTTP API
    "rich>=13.0.0",          # For terminal formatting
    "click>=8.1.0",          # For CLI (if needed)
]
```

### External Dependencies

- **Ollama**: Must be installed and running (`ollama serve`)
- **Git**: Required for version control
- **Bash**: For existing workflow scripts

## Installation

```bash
# Install in development mode
cd researchKit
pip install -e .

# The research-ollama command will be available
research-ollama --help
```

## pyproject.toml Updates

```toml
[project.scripts]
research = "research_cli:main"
research-ollama = "ollama_agent.cli:main"  # NEW
```

## Error Handling

### Ollama Connection Errors

```python
try:
    models = client.list_models()
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Ollama at {url}")
    print("   Make sure Ollama is running: ollama serve")
    print("   Or set custom URL: export OLLAMA_URL=http://...")
    sys.exit(1)
```

### Git Errors

```python
if subprocess.run(["git", "status"], capture_output=True).returncode != 0:
    print("❌ Git repository not initialized")
    if prompt_yes_no("Initialize git repository?"):
        subprocess.run(["git", "init"])
    else:
        print("ResearchKit requires git. Exiting.")
        sys.exit(1)
```

### Bash Script Errors

```python
result = subprocess.run(
    [".researchkit/scripts/bash/plan.sh", topic],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"❌ Error creating research plan: {result.stderr}")
    sys.exit(1)
```

## Testing Strategy

### Unit Tests

```python
# tests/test_ollama_client.py
def test_list_models():
    client = OllamaClient()
    models = client.list_models()
    assert len(models) > 0
    assert all(isinstance(m, str) for m in models)

# tests/test_config.py
def test_config_save_and_load():
    config = OllamaConfig(model="llama3.2:latest")
    manager = ConfigManager()
    manager.save(config)
    loaded = manager.load()
    assert loaded.model == "llama3.2:latest"
```

### Integration Tests

```python
# tests/test_workflow.py
def test_full_workflow(tmp_path):
    """Test complete workflow in isolated directory."""
    # Setup: Initialize git, create .researchkit/
    # Execute: Run workflow with mocked Ollama responses
    # Assert: Verify all files created and committed
```

### Manual Testing Checklist

- [ ] First-time setup: Uninitialized folder
- [ ] First-time setup: Existing git repo, no .researchkit/
- [ ] Returning user: Config already exists
- [ ] Model selection: List displays correctly
- [ ] Constitution phase: Approval loop works
- [ ] Plan phase: Creates branch and files
- [ ] Execute phase: Iterative findings loop
- [ ] Synthesize phase: Final report generated
- [ ] Feedback loops: Agent responds to user feedback
- [ ] Edit mode: Opens $EDITOR correctly
- [ ] Git commits: All changes committed properly
- [ ] Error handling: Graceful degradation

## Future Enhancements

### Phase 2 Features (Not in Initial Implementation)

1. **Web Search Integration**: Add web scraping for research execution
2. **Citation Management**: Automatic citation formatting with biblatex
3. **Multi-Model Support**: Switch models mid-conversation
4. **Research Templates**: Pre-defined research types (literature review, experimental, etc.)
5. **Collaborative Research**: Multi-user research with git branches
6. **Export Formats**: PDF, HTML, LaTeX output
7. **Research Analytics**: Track time, sources, iterations per project

## Success Criteria

The implementation will be considered successful when:

1. ✅ User can run `research-ollama` and complete a full research workflow
2. ✅ All phases (constitution, plan, execute, synthesize) work with approval loops
3. ✅ Configuration persists across sessions in `.researchkit/config/ollama.json`
4. ✅ Git commits are created at appropriate checkpoints
5. ✅ Error messages are helpful and guide users to resolution
6. ✅ No external AI service required (fully local with Ollama)
7. ✅ Compatible with existing researchKit bash scripts and templates

## Timeline Estimate

- **Phase 1**: Core infrastructure (environment, config, client) - 1 day
- **Phase 2**: Conversation engine and approval loops - 1 day
- **Phase 3**: Workflow orchestrator and phase prompts - 2 days
- **Phase 4**: CLI integration and testing - 1 day
- **Phase 5**: Documentation and refinement - 1 day

**Total**: ~6 days of development

## Security Considerations

1. **Ollama URL Validation**: Ensure URL is valid HTTP/HTTPS before connecting
2. **Config File Permissions**: `.researchkit/config/` should not contain secrets
3. **User Input Sanitization**: Escape user input before passing to bash scripts
4. **Command Injection**: Never use user input directly in subprocess without validation

## Accessibility

- Use **rich** library for color-blind friendly terminal output
- Provide plain-text fallback mode: `research-ollama --no-color`
- Keyboard-only interaction (no mouse required)
- Clear prompts with default options: `[y/N]` format

---

## Appendix: Example Session

```
$ research-ollama

🔍 ResearchKit Ollama Agent v0.1.0

Checking environment...
✓ Ollama running at http://localhost:11434
✓ Git repository initialized
✓ ResearchKit initialized

Loading configuration...
✓ Using model: llama3.2:latest

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 What would you like to research? Impact of AI on software development productivity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 1: CONSTITUTION

Loading research constitution...

[Constitution content displayed]

Approve constitution? [y]es / [e]dit / [f]eedback: y

✓ Constitution approved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 2: PLANNING

Creating research plan...

[AI generates plan using Ollama]
[Plan displayed to user]

Approve plan? [y]es / [e]dit / [f]eedback: f

Provide feedback: Include more focus on developer experience metrics

[AI revises plan with feedback]
[Updated plan displayed]

Approve plan? [y]es / [e]dit / [f]eedback: y

✓ Plan saved to .researchkit/research/001-ai-productivity/plan.md
✓ Created branch: research/001-ai-productivity
✓ Committed to git

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 3: EXECUTION

[Research execution with iterative findings...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 4: SYNTHESIS

[Final synthesis generation...]

✅ Research complete!
   Final report: ai-productivity-synthesis-2025-11-09.md
```

---

**Document Version**: 1.0
**Created**: 2025-11-09
**Author**: Specification for Ollama Agent Integration
