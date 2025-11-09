# Ollama Agent Guide

## Overview

The Ollama Agent is a lightweight, standalone research assistant integrated into ResearchKit that uses locally-hosted Ollama models. It provides an AI-powered research workflow with built-in tool support for web search, URL fetching, and PDF parsing.

### Key Features

- **Local AI Models**: Uses Ollama for privacy-focused, offline-capable research
- **Tool Support**: Built-in web search, URL fetching, and PDF parsing capabilities
- **Structured Workflow**: Guided research process from planning to synthesis
- **Git Integration**: Automatic version control of research artifacts
- **Interactive Approval**: User control at every phase with feedback loops
- **Tool-Compatible Models Only**: Automatically filters to show only models that support function calling

## Prerequisites

Before using the Ollama Agent, ensure you have:

1. **Python 3.11 or higher**
2. **Git installed and configured**
3. **Ollama installed and running**
   - Download from: https://ollama.ai
   - Start Ollama service: `ollama serve`
4. **A tool-compatible Ollama model downloaded**
   - Recommended: `ollama pull llama3.2`
   - Other compatible models: llama3.1, mistral-nemo, qwen2.5, command-r, firefunction

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/ivo-toby/researchKit.git
cd researchKit

# Install the package
pip install -e .
```

The `research-ollama` command will be available after installation.

## Configuration

### First Run

On first run, the Ollama Agent will:

1. Check if Ollama is running
2. Check if git is initialized (prompt to initialize if not)
3. Check if `.researchkit/` structure exists (create if not)
4. Prompt you to select a tool-compatible Ollama model
5. Configure settings (temperature, context window, etc.)
6. Save configuration to `.researchkit/config/ollama.json`

### Manual Configuration

You can manually edit `.researchkit/config/ollama.json`:

```json
{
  "version": "1.0",
  "ollama_url": "http://localhost:11434",
  "model": "llama3.2",
  "temperature": 0.7,
  "top_p": 0.9,
  "num_ctx": 4096,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Environment Variables

- `OLLAMA_URL`: Override the Ollama API URL (default: `http://localhost:11434`)

Example:
```bash
export OLLAMA_URL=http://192.168.1.100:11434
research-ollama
```

## Usage

### Starting a Research Project

```bash
research-ollama
```

The agent will guide you through an interactive workflow.

### Research Workflow Phases

#### Phase 1: Constitution

Define your research methodology and guidelines.

- **Purpose**: Establish research principles, citation style, and quality standards
- **Output**: `.researchkit/memory/constitution.md`
- **Git**: Automatically committed as "docs: Update research constitution"

**Actions:**
- Review AI-generated constitution
- Approve with `y` or provide feedback with `f`
- Edit manually with `e` (opens $EDITOR)
- Skip with `s`

#### Phase 2: Planning

Create a detailed research plan for your topic.

- **Purpose**: Break down research question into investigative steps
- **Output**: `.researchkit/research/NNN-topic/plan.md`
- **Git**: Automatically committed as "docs: Add research plan for [topic]"

**Actions:**
- Enter your research topic when prompted
- Review AI-generated plan
- Approve, edit, or provide feedback
- The plan defines what will be researched and how

#### Phase 3: Execution

Conduct research using AI tools.

- **Purpose**: Gather evidence and information using web search, URLs, and PDFs
- **Output**:
  - `.researchkit/research/NNN-topic/findings.md`
  - `.researchkit/research/NNN-topic/sources.md` (auto-updated)
- **Git**: Automatically committed as "docs: Document research findings"

**Tool Usage:**
The AI agent can automatically:
- Search the web with DuckDuckGo
- Fetch and parse web pages
- Download and extract text from PDFs
- Cite sources automatically

**Actions:**
- The agent conducts research based on the plan
- Review findings and sources
- Approve, edit, or request more research

#### Phase 4: Synthesis

Generate a comprehensive final report.

- **Purpose**: Synthesize all findings into a polished research report
- **Output**:
  - `.researchkit/research/NNN-topic/synthesis.md`
  - `[topic]-synthesis-[date].md` (copied to project root)
- **Git**: Automatically committed as "docs: Complete research synthesis"

**Actions:**
- Review the synthesized report
- Approve, edit, or provide feedback
- Final report is copied to project root for easy access

## Research Tools

The Ollama Agent has three built-in tools that the AI can use automatically during the execution phase:

### 1. Web Search (`web_search`)

Searches the web using DuckDuckGo.

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Number of results to return (default: 10)

**Example usage by AI:**
```json
{
  "name": "web_search",
  "arguments": {
    "query": "quantum computing applications 2024",
    "max_results": 10
  }
}
```

**Returns:**
- Title, URL, and snippet for each result
- Automatically adds URLs to sources.md

### 2. URL Fetch (`fetch_url`)

Downloads and extracts text from web pages.

**Parameters:**
- `url` (required): URL to fetch
- `extract_text` (optional): Extract clean text (default: true)

**Example usage by AI:**
```json
{
  "name": "fetch_url",
  "arguments": {
    "url": "https://example.com/article",
    "extract_text": true
  }
}
```

**Returns:**
- Clean text content from the page
- Automatically removes scripts, styles, and navigation
- Adds URL to sources.md

### 3. PDF Parser (`parse_pdf`)

Downloads and extracts text from PDF files.

**Parameters:**
- `url` (required): URL of the PDF file
- `save_path` (optional): Local path to save PDF

**Example usage by AI:**
```json
{
  "name": "parse_pdf",
  "arguments": {
    "url": "https://example.com/paper.pdf"
  }
}
```

**Returns:**
- Extracted text from all pages
- PDF metadata (title, author, page count)
- Saves PDF for reference
- Adds URL to sources.md

## Project Structure

After running the Ollama Agent, your project will have this structure:

```
your-project/
├── .git/                          # Git repository
├── .researchkit/
│   ├── config/
│   │   └── ollama.json           # Ollama agent configuration
│   ├── memory/
│   │   └── constitution.md       # Research methodology
│   ├── research/
│   │   └── 001-topic-name/       # Research project folder
│   │       ├── plan.md           # Research plan
│   │       ├── findings.md       # Research findings
│   │       ├── sources.md        # Bibliography
│   │       └── synthesis.md      # Final report
│   ├── scripts/
│   │   └── bash/                 # Helper scripts
│   └── templates/                # Document templates
└── topic-name-synthesis-2024-01-15.md  # Final report (copied to root)
```

## Tool-Compatible Models

The Ollama Agent only shows models that support tool calling (function calling). Compatible models include:

- **llama3.2** (recommended)
- **llama3.1**
- **mistral-nemo**
- **qwen2.5**
- **command-r**
- **firefunction**

To download a compatible model:

```bash
ollama pull llama3.2
```

## Troubleshooting

### Ollama Not Running

**Error:** "Cannot connect to Ollama"

**Solution:**
1. Check if Ollama is running: `curl http://localhost:11434/api/tags`
2. Start Ollama: `ollama serve`
3. Verify model is installed: `ollama list`

### No Tool-Compatible Models

**Error:** "No tool-compatible models found"

**Solution:**
1. Pull a compatible model: `ollama pull llama3.2`
2. Restart the agent: `research-ollama`

### Git Not Initialized

**Error:** "No git repository found"

**Solution:**
The agent will prompt you to initialize git. Select `y` to initialize.

Alternatively, initialize manually:
```bash
git init
```

### Web Search Fails

**Error:** "Web search failed"

**Possible causes:**
- No internet connection
- DuckDuckGo rate limiting

**Solution:**
- Wait a few moments and try again
- Use `fetch_url` with specific URLs instead

### PDF Parsing Fails

**Error:** "Failed to parse PDF"

**Possible causes:**
- PDF is image-based (no text layer)
- PDF is password-protected
- Network timeout

**Solution:**
- Try a different PDF source
- Check if PDF is accessible in browser
- Increase timeout by modifying the code

## Advanced Usage

### Using a Custom Ollama Server

```bash
export OLLAMA_URL=http://custom-server:11434
research-ollama
```

### Skipping Constitution Phase

If you already have a constitution defined, you can skip the constitution phase by selecting `s` when prompted.

### Manual Editing

At any approval prompt, select `e` to open the content in your default editor (`$EDITOR`). Make changes, save, and close to continue.

### Providing Feedback

Select `f` at any approval prompt to provide specific feedback. The AI will regenerate the content based on your input.

## Integration with ResearchKit

The Ollama Agent is designed to coexist with the existing ResearchKit functionality:

- **Separate CLI command**: `research-ollama` vs `research`
- **Shared infrastructure**: Both use `.researchkit/` folder structure
- **Compatible workflows**: Research artifacts are compatible between tools
- **Git-based**: Both use git for version control

You can use either tool depending on your needs:
- **Ollama Agent**: Local, private, tool-enabled research
- **ResearchKit CLI**: (for other ResearchKit workflows)

## Best Practices

1. **Start with a clear research question**: The more specific your topic, the better the results
2. **Review each phase**: Don't auto-approve without reading the outputs
3. **Provide specific feedback**: If something is wrong, explain what needs to change
4. **Use appropriate models**: Larger models (llama3.1) give better quality but are slower
5. **Manage context window**: For very long research, consider breaking into multiple sessions
6. **Commit regularly**: Each phase auto-commits, maintaining a clean research history
7. **Review sources**: Check the auto-generated sources.md for citation accuracy

## Examples

### Example 1: Technology Research

```bash
research-ollama
# Constitution phase: Define academic standards
# Plan phase: Enter topic "quantum computing applications in cryptography"
# Execute phase: AI searches web, fetches articles, parses papers
# Synthesize phase: Generate comprehensive report
```

### Example 2: Market Research

```bash
research-ollama
# Constitution phase: Define business research methodology
# Plan phase: Enter topic "AI startup landscape 2024"
# Execute phase: AI gathers market data, competitor analysis
# Synthesize phase: Create market analysis report
```

## Limitations

- **Internet required**: For web search and URL fetching (PDF parsing requires download)
- **English-focused**: DuckDuckGo search and text extraction work best with English content
- **Tool compatibility**: Only works with Ollama models that support function calling
- **Local models**: Quality depends on the Ollama model you choose
- **Rate limiting**: DuckDuckGo may rate-limit excessive searches

## Contributing

To contribute to the Ollama Agent:

1. Fork the repository
2. Create a feature branch
3. Make your changes with atomic commits
4. Add tests for new functionality
5. Submit a pull request

See `OLLAMA_AGENT_SPEC.md` for technical details.

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/ivo-toby/researchKit/issues
- Documentation: https://github.com/ivo-toby/researchKit/blob/main/docs/

## Version History

- **v0.1.0** (2024-01-15): Initial release
  - Web search with DuckDuckGo
  - URL fetching and parsing
  - PDF text extraction
  - Four-phase research workflow
  - Git integration
  - Tool-compatible model filtering
