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
       │                ├────────────────┤
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Config    │  │   Ollama    │  │    Bash     │
│   Manager   │  │  API Client │  │   Scripts   │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
                        │ Tool Calling
                        │
                        ▼
                 ┌─────────────┐
                 │Research Tools│
                 ├─────────────┤
                 │ web_search  │
                 │ fetch_url   │
                 │ parse_pdf   │
                 └─────────────┘
```

### Component Responsibilities

1. **Environment Manager**: Checks git initialization, folder structure, Ollama availability
2. **Config Manager**: Handles `.researchkit/config/ollama.json` storage and retrieval
3. **Ollama API Client**: Handles HTTP requests to Ollama API with tool calling support
4. **Research Tools**: Provides web_search, fetch_url, and parse_pdf capabilities
5. **Conversation Engine**: Manages multi-turn conversations, tool execution, and user approval loops
6. **Workflow Orchestrator**: Coordinates constitution → plan → execute → synthesize phases

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
6. Query Ollama for available tool-compatible models:
   → GET http://localhost:11434/api/tags
   → Filter for models that support tool calling
   → Display list: "Select a model to use (tool-compatible only):"
      1. llama3.2:latest
      2. llama3.1:latest
      3. mistral-nemo:latest
      4. qwen2.5:latest
   → User selects (1-4)
   → If no tool-compatible models: Suggest "ollama pull llama3.2"
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
3. Agent conducts research with Ollama using tools:
   - For each research question in plan:
     → Agent uses web_search tool to find relevant sources
     → Agent uses fetch_url tool to extract content from web pages
     → Agent uses parse_pdf tool to analyze research papers
     → User sees: "🔍 Searching for: '[query]'"
     → User sees: "📄 Fetching: [url]"
     → User sees: "📑 Parsing PDF: [url]"
     → Agent synthesizes findings from tool results
     → After each finding:
        "Document this finding? [y]es / [e]dit / [f]eedback / [s]kip"
4. Agent updates sources.md with bibliography (URLs and PDFs)
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
│       ├── ollama_client.py         # Ollama API client with tool calling
│       ├── conversation.py          # Conversation engine
│       ├── workflow.py              # Workflow orchestrator
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── web_search.py        # Web search tool
│       │   ├── url_fetch.py         # URL fetching tool
│       │   └── pdf_parser.py        # PDF download and parsing tool
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
        self.base_url = base_url

    def list_models(self, tool_compatible_only: bool = True) -> List[str]:
        """Get available models from Ollama.

        GET /api/tags

        Args:
            tool_compatible_only: If True, filter to only models that support tools

        Returns: ["llama3.2:latest", "mistral-nemo:latest", ...]
        """

    def check_model_supports_tools(self, model: str) -> bool:
        """Check if a model supports tool calling.

        Args:
            model: Model name (e.g., "llama3.2:latest")

        Returns: True if model supports tools
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
        stream: bool = False,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Chat completion from Ollama with tool calling support.

        POST /api/chat
        {
            "model": "llama3.2:latest",
            "messages": [
                {"role": "user", "content": "..."}
            ],
            "temperature": 0.7,
            "stream": false,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]
        }

        Returns:
            {
                "message": {
                    "role": "assistant",
                    "content": "...",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "web_search",
                                "arguments": {"query": "..."}
                            }
                        }
                    ]
                }
            }
        """

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

        Returns: Tool execution result as string
        """
```

#### 4. Research Tools (`tools/`)

The agent provides three core research tools that the LLM can call:

##### 4.1 Web Search (`tools/web_search.py`)

```python
def web_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search the web for information.

    Uses a search API (DuckDuckGo, SearXNG, or similar) to find relevant
    web pages for the research query.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        {
            "results": [
                {
                    "title": "...",
                    "url": "...",
                    "snippet": "...",
                    "source": "..."
                }
            ],
            "query": "original query",
            "count": 10
        }
    """

def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for web_search."""
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    }
```

##### 4.2 URL Fetch (`tools/url_fetch.py`)

```python
def fetch_url(url: str, extract_text: bool = True) -> Dict[str, Any]:
    """Fetch and parse content from a URL.

    Downloads web page content and optionally extracts clean text
    (removing HTML tags, scripts, navigation, etc.).

    Args:
        url: URL to fetch
        extract_text: If True, extract clean text from HTML

    Returns:
        {
            "url": "...",
            "title": "...",
            "content": "extracted text content",
            "content_type": "text/html",
            "status_code": 200,
            "word_count": 1234
        }
    """

def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for fetch_url."""
    return {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch and extract text content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "Extract clean text from HTML (default true)",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    }
```

##### 4.3 PDF Parser (`tools/pdf_parser.py`)

```python
def parse_pdf(url: str, save_path: Optional[str] = None) -> Dict[str, Any]:
    """Download and parse a PDF document.

    Downloads PDF from URL, extracts text content, and optionally
    saves to local file system for reference.

    Args:
        url: URL to PDF document
        save_path: Optional local path to save PDF

    Returns:
        {
            "url": "...",
            "text": "extracted text content",
            "pages": 42,
            "metadata": {
                "title": "...",
                "author": "...",
                "created": "..."
            },
            "saved_path": "/path/to/file.pdf" or None,
            "word_count": 5678
        }
    """

def get_tool_definition() -> Dict:
    """Return OpenAI-compatible tool definition for parse_pdf."""
    return {
        "type": "function",
        "function": {
            "name": "parse_pdf",
            "description": "Download and extract text from a PDF document",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to the PDF document"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional path to save the PDF locally"
                    }
                },
                "required": ["url"]
            }
        }
    }
```

##### 4.4 Tool Registry (`tools/__init__.py`)

```python
"""Research tools for the Ollama agent."""

from .web_search import web_search, get_tool_definition as web_search_def
from .url_fetch import fetch_url, get_tool_definition as url_fetch_def
from .pdf_parser import parse_pdf, get_tool_definition as pdf_parser_def

# Tool registry maps tool names to their implementations
TOOL_REGISTRY = {
    "web_search": web_search,
    "fetch_url": fetch_url,
    "parse_pdf": parse_pdf,
}

# Tool definitions for Ollama API
TOOL_DEFINITIONS = [
    web_search_def(),
    url_fetch_def(),
    pdf_parser_def(),
]

__all__ = [
    "TOOL_REGISTRY",
    "TOOL_DEFINITIONS",
    "web_search",
    "fetch_url",
    "parse_pdf",
]
```

#### 5. Conversation Engine (`conversation.py`)

```python
class ConversationEngine:
    """Manages interactive conversations with approval loops and tool execution."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        config: OllamaConfig,
        tool_registry: Dict[str, Callable],
        tool_definitions: List[Dict]
    ):
        self.client = ollama_client
        self.config = config
        self.messages: List[Dict[str, str]] = []
        self.tool_registry = tool_registry
        self.tool_definitions = tool_definitions

    def add_system_message(self, content: str) -> None:
        """Add system message to conversation context."""

    def add_user_message(self, content: str) -> None:
        """Add user message to conversation context."""

    def generate_response(self, use_tools: bool = True) -> str:
        """Generate AI response using current conversation context.

        Args:
            use_tools: If True, provide tools to the model

        Returns: Final response after tool execution (if any)

        Flow:
        1. Call Ollama with tools
        2. If response includes tool_calls:
           a. Execute each tool
           b. Add tool results to messages
           c. Call Ollama again
           d. Repeat until no more tool calls
        3. Return final text response
        """

    def execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute a list of tool calls and return results.

        Args:
            tool_calls: List of tool call objects from Ollama

        Returns: List of tool result messages
        """

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

    def clear_history(self) -> None:
        """Reset message history for new phase."""
```

#### 6. Workflow Orchestrator (`workflow.py`)

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

#### 7. CLI Entry Point (`cli.py`)

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
        # Only show models that support tool calling
        models = client.list_models(tool_compatible_only=True)

        if not models:
            print("❌ No tool-compatible models found.")
            print("   Install a compatible model:")
            print("   ollama pull llama3.2")
            print("   ollama pull mistral-nemo")
            sys.exit(1)

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

    # 3. Start research workflow with tools
    from ollama_agent.tools import TOOL_REGISTRY, TOOL_DEFINITIONS

    client = OllamaClient(config.ollama_url)
    conversation = ConversationEngine(
        client,
        config,
        TOOL_REGISTRY,
        TOOL_DEFINITIONS
    )
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
    "requests>=2.31.0",           # For Ollama HTTP API and URL fetching
    "rich>=13.0.0",               # For terminal formatting
    "beautifulsoup4>=4.12.0",     # For HTML parsing
    "lxml>=4.9.0",                # For efficient HTML/XML parsing
    "pypdf>=3.17.0",              # For PDF parsing
    "ddgs>=1.0.0",                # For web search (DuckDuckGo)
    "markdownify>=0.11.0",        # For HTML to Markdown conversion
]
```

**Alternative search backends** (choose one):
- `ddgs` - No API key required, privacy-focused (formerly duckduckgo-search)
- `searxng` - Self-hosted search aggregator
- `tavily-python` - Requires API key, research-focused

### External Dependencies

- **Ollama**: Must be installed and running (`ollama serve`)
  - **Tool-compatible model required**: llama3.2, llama3.1, mistral-nemo, qwen2.5, command-r, or firefunction
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

### Phase 2 Features (Post-MVP)

1. **Tool Calling for Non-Native Models**: Implement tool calling wrapper for models that don't natively support it
   - Parse function call syntax from text output
   - Provide few-shot examples for tool usage
   - Support models like codellama, deepseek, etc.

2. **MCP (Model Context Protocol) Support**: Integrate with MCP servers for extended capabilities
   - File system access via MCP
   - Database connections via MCP
   - Custom tool servers via MCP
   - Standardized tool interface

3. **Citation Management**: Automatic citation formatting with biblatex
   - BibTeX generation from sources
   - Citation style selection (APA, MLA, Chicago)
   - Automatic in-text citations

4. **Multi-Model Support**: Switch models mid-conversation
   - Different models for different phases
   - Model comparison mode
   - Cost/performance optimization

5. **Research Templates**: Pre-defined research types
   - Literature review template
   - Experimental research template
   - Meta-analysis template
   - Technical evaluation template

6. **Collaborative Research**: Multi-user research with git branches
   - Shared research projects
   - Branch-based collaboration
   - Research review workflow

7. **Export Formats**: Multiple output formats
   - PDF generation (via LaTeX or WeasyPrint)
   - HTML with styling
   - LaTeX academic paper format
   - Jupyter notebook format

8. **Research Analytics**: Track research metrics
   - Time spent per phase
   - Number of sources consulted
   - Iteration count per phase
   - Research velocity tracking

9. **Advanced Search Features**:
   - Academic paper search (arXiv, Google Scholar, PubMed)
   - Patent search
   - News archive search
   - Social media monitoring

10. **Multimodal Research**:
    - Image analysis for research
    - Chart/graph extraction from papers
    - Video content analysis
    - Audio transcription and analysis

## Success Criteria

The implementation will be considered successful when:

1. ✅ User can run `research-ollama` and complete a full research workflow
2. ✅ All phases (constitution, plan, execute, synthesize) work with approval loops
3. ✅ Configuration persists across sessions in `.researchkit/config/ollama.json`
4. ✅ Git commits are created at appropriate checkpoints
5. ✅ Error messages are helpful and guide users to resolution
6. ✅ No external AI service required (fully local with Ollama)
7. ✅ Compatible with existing researchKit bash scripts and templates
8. ✅ **Tool calling works**: Agent can use web_search, fetch_url, and parse_pdf tools
9. ✅ **Only tool-compatible models shown**: Model selection filters for function calling support
10. ✅ **Web research functional**: Agent can search, fetch URLs, and parse PDFs during execution phase
11. ✅ **Sources tracked**: All URLs and PDFs added to sources.md automatically

## Timeline Estimate

- **Phase 1**: Core infrastructure (environment, config, client) - 1 day
- **Phase 2**: Tool implementation (web_search, fetch_url, parse_pdf) - 1.5 days
- **Phase 3**: Ollama tool calling integration - 1 day
- **Phase 4**: Conversation engine with tool execution - 1.5 days
- **Phase 5**: Workflow orchestrator and phase prompts - 2 days
- **Phase 6**: CLI integration and testing - 1 day
- **Phase 7**: Documentation and refinement - 1 day

**Total**: ~9 days of development

## Backward Compatibility & Non-Interference

The Ollama standalone agent is designed to **coexist** with the existing researchKit functionality without any interference:

### Separation of Concerns

1. **Separate Package Structure**
   - Existing: `src/research_cli/` (unchanged)
   - New: `src/ollama_agent/` (isolated package)
   - No modifications to existing `research_cli` code

2. **Separate CLI Commands**
   - Existing: `research init`, `research check`
   - New: `research-ollama` (completely separate command)
   - Both commands can be installed and used simultaneously

3. **Shared Infrastructure** (Non-Breaking)
   - Both use `.researchkit/` folder structure
   - Both use the same bash scripts (`plan.sh`, `execute.sh`, `synthesize.sh`)
   - Both use the same templates (plan, execution, synthesis, constitution)
   - Ollama agent adds: `.researchkit/config/ollama.json` (new file, doesn't affect existing workflows)

4. **Configuration Isolation**
   - Existing researchKit: No config file currently
   - Ollama agent: `.researchkit/config/ollama.json` (new, isolated)
   - No overlap or conflict

5. **Entry Point Separation**
   ```toml
   [project.scripts]
   research = "research_cli:main"          # Existing (unchanged)
   research-ollama = "ollama_agent.cli:main"  # New (additive)
   ```

### Compatibility Guarantees

✅ **Existing workflows continue to work exactly as before**
- `research init` and `research check` remain unchanged
- Claude Code slash commands (`/researchkit.*`) unaffected
- All existing bash scripts work identically
- No changes to template files

✅ **Users can choose their workflow**
- Use `research init` + Claude Code (existing workflow)
- Use `research-ollama` (new Ollama workflow)
- Use both in different projects
- No conflicts between the two approaches

✅ **Shared benefits**
- Any improvements to bash scripts benefit both
- Template updates work for both
- Both use the same git-based research project structure

### Migration Path (Optional)

Users are **not required** to migrate. However, if they want to use Ollama:

1. Install `ollama` and pull a tool-compatible model
2. Run `research-ollama` instead of `research init`
3. Continue using all researchKit features with Ollama as the AI backend

The existing Claude Code workflow remains fully supported and unchanged.

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

**Document Version**: 2.0
**Created**: 2025-11-09
**Updated**: 2025-11-09
**Author**: Specification for Ollama Agent Integration

## Changelog

### Version 2.0 (2025-11-09)
- **Added MVP Features**:
  - Tool calling support (function calling) for Ollama models
  - Web search tool (web_search)
  - URL fetching tool (fetch_url)
  - PDF parsing tool (parse_pdf)
- **Updated**:
  - Model selection now filters for tool-compatible models only
  - Architecture diagram includes Research Tools component
  - Dependencies updated with beautifulsoup4, pypdf, ddgs
  - Timeline extended to 9 days to account for tool implementation
  - Success criteria updated with tool-related requirements
- **Future Enhancements**:
  - Added MCP (Model Context Protocol) support
  - Added tool calling for non-native models
  - Reorganized and expanded future feature list

### Version 1.0 (2025-11-09)
- Initial specification
