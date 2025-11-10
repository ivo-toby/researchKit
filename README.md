# 🔬 ResearchKit

**Structured research workflows with AI integration**

ResearchKit is a CLI tool for conducting rigorous, well-documented research with AI assistance. Inspired by [SpecKit](https://github.com/github/spec-kit), it provides a systematic approach to research projects with proper citation management, source tracking, and structured synthesis.

---

## Features

- 📋 **Structured Research Workflow**: Plan → Execute → Synthesize
- 📚 **Citation Management**: Built-in bibliography tracking with quality ratings
- 🤖 **Multi-AI Support**: Works with Claude Code, GitHub Copilot, Gemini CLI, Cursor, OpenCode, and Codex CLI
- 🎯 **Research Constitution**: Define methodology principles and standards
- 📊 **Progress Tracking**: Git-based project organization with auto-incrementing IDs
- ✅ **Quality Assurance**: Checklists and verification requirements

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Git
- **AI Editor/Tool** (optional, choose one or more):
  - [Claude Code](https://docs.claude.com/claude-code) - Full slash command support
  - [GitHub Copilot](https://github.com/features/copilot) - IDE integration
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) - Command-line interface
  - [Cursor](https://cursor.sh) - AI-powered editor
  - [OpenCode](https://opencode.ai) - AI research assistant
  - [Codex CLI](https://github.com/openai/codex) - Code generation for research
- [uv](https://github.com/astral-sh/uv) (recommended)

### Install with uv

```bash
# Install ResearchKit CLI
uv tool install research-cli --from git+https://github.com/ivo-toby/researchKit.git

# Verify installation
research check
```

### Install for Development

```bash
# Clone the repository
git clone https://github.com/ivo-toby/researchKit.git
cd researchKit

# Install in editable mode
uv pip install -e .

# Or use pip
pip install -e .
```

---

## Quick Start

### 1. Initialize a Research Project

```bash
# Create a new project with your preferred AI tool
research init my-research-project --ai claude
cd my-research-project

# Or use current directory
research init . --ai claude

# Available AI options:
# --ai claude, copilot, gemini, cursor, opencode, codex
```

This creates:
```
.researchkit/
├── memory/
│   └── constitution.md          # Research methodology principles
├── scripts/
│   └── bash/                    # Research workflow scripts
├── research/                    # Your research projects (auto-created)
└── templates/                   # Document templates
```

### 2. Start Your AI Tool

```bash
# For Claude Code
claude

# For Cursor
cursor .

# For other tools, see the "Supported AI Editors and Tools" section below
```

### 3. Define Research Constitution (Optional but Recommended)

```
/researchkit.constitution
```

Define your research standards:
- Citation requirements
- Source quality criteria
- Verification standards
- Documentation practices

### 4. Plan Your Research

```
/researchkit.plan
```

Provide your research topic, and ResearchKit will:
- Create a new research project with ID (e.g., `001-topic-name`)
- Generate a git branch (`research/001-topic-name`)
- Set up `plan.md` from template
- Create `sources.md` for bibliography

Fill in the plan with:
- Research question
- Objectives
- Scope (in/out)
- Search strategy
- Success criteria

### 5. Execute Research

```
/researchkit.execute
```

This sets up `findings.md` where you'll document:
- Research sessions (chronological)
- Sources found with citations
- Key points and quotes
- Emerging themes
- Questions raised

**Research Process**:
- Use web search to gather information
- Document findings in `findings.md` as you go
- Add sources to `sources.md` immediately
- Follow your constitution's citation standards
- Cross-verify important claims

### 6. Synthesize Findings

```
/researchkit.synthesize
```

This creates `synthesis.md` where you'll write:
- Executive summary
- Key findings with evidence
- Analysis and discussion
- Evidence-based conclusions
- Recommendations
- Complete bibliography

---

## Supported AI Editors and Tools

ResearchKit supports multiple AI editors and CLI tools. Choose the one that best fits your workflow:

### Claude Code (Recommended)

Full integration with slash commands for guided research workflows.

```bash
research init my-project --ai claude
cd my-project
claude
```

**Features:**
- Interactive slash commands (`/researchkit.plan`, `/researchkit.execute`, etc.)
- Guided research workflow
- Built-in citation and source management
- Constitution-based research standards

**Use when:** You want comprehensive guided research with interactive AI assistance.

---

### GitHub Copilot

IDE-based AI assistant working in VS Code, JetBrains, and other editors.

```bash
research init my-project --ai copilot
```

**Features:**
- In-editor AI suggestions
- Code and document completion
- Citation formatting assistance
- Works in your existing IDE

**Use when:** You prefer working in your IDE with inline AI suggestions.

---

### Gemini CLI

Google's AI assistant via command-line interface.

```bash
# Requires Gemini CLI installation
research init my-project --ai gemini
```

**Features:**
- Command-line AI interactions
- Literature review and summarization
- Citation formatting
- Research question refinement

**Installation:** https://github.com/google-gemini/gemini-cli

**Use when:** You prefer command-line workflows and Google's AI models.

---

### Cursor

AI-powered code editor built on VS Code with integrated AI assistance.

```bash
research init my-project --ai cursor
```

**Features:**
- AI-powered editor with chat interface
- Automatic `.cursorrules` configuration
- Research workflow awareness
- Citation and document structuring

**Installation:** https://cursor.sh

**Use when:** You want an AI-native editor experience for research.

---

### OpenCode

AI research assistant with specialized prompts for academic work.

```bash
# Requires OpenCode CLI installation
research init my-project --ai opencode
```

**Features:**
- Research-specific AI prompts
- Citation management and formatting
- Literature review synthesis
- Custom research assistant configuration
- **Ollama support for local models** 🔥

**Installation:** https://opencode.ai

**Use when:** You need specialized AI assistance for academic research.

#### 🏠 Privacy-First Research: OpenCode + Ollama

OpenCode supports [Ollama](https://ollama.ai), enabling **100% local AI research** with no data leaving your machine. This is perfect for:

- **Privacy-sensitive research** - Medical, legal, or proprietary research
- **Cost-effective workflows** - No API costs, unlimited usage
- **Offline research** - Work without internet connectivity
- **Data sovereignty** - Full control over your research data

**Setup:**

1. Install Ollama: https://ollama.ai
2. Pull a model (e.g., `ollama pull llama3.2` or `ollama pull qwen2.5:32b`)
3. Configure OpenCode to use Ollama
4. Initialize ResearchKit:
   ```bash
   research init my-private-research --ai opencode
   cd my-private-research
   opencode
   ```

**Recommended models for research:**
- `qwen2.5:32b` - Excellent for research tasks, citation formatting
- `llama3.2` - Good general-purpose research assistant
- `mixtral` - Strong reasoning for complex analysis

Now you can conduct rigorous, well-documented research entirely on your local machine! 🔬🏠

---

### Codex CLI

OpenAI's code generation tool for research automation and data analysis.

```bash
# Requires Codex CLI installation
research init my-project --ai codex
```

**Features:**
- Code generation for data analysis
- Research automation scripts
- Statistical analysis and visualization
- Requires `CODEX_HOME` environment variable setup

**Installation:** https://github.com/openai/codex

**Environment Setup:**
```bash
export CODEX_HOME="/path/to/your/project/.codex"
```

**Use when:** You need code generation for data analysis and research automation.

---

### Checking Available Tools

Verify which AI tools are installed:

```bash
research check
```

This displays the status of Git and all supported AI CLI tools.

---

## Workflow Example

```bash
# Initialize project
research init ai-safety-research --ai claude
cd ai-safety-research

# Start Claude Code
claude
```

In Claude Code:
```
# Set research standards
/researchkit.constitution

# Plan the research
/researchkit.plan
> Research question: What are current best practices for AI safety in production systems?

# Execute research
/researchkit.execute
> [Use web search to find sources]
> [Document findings with citations]
> [Track sources in bibliography]

# Synthesize results
/researchkit.synthesize
> [Create comprehensive report]
> [Include evidence-based conclusions]
> [Provide actionable recommendations]
```

---

## Project Structure

When you initialize a ResearchKit project:

```
my-research-project/
├── .researchkit/
│   ├── memory/
│   │   └── constitution.md              # Your research principles
│   ├── scripts/
│   │   └── bash/
│   │       ├── common.sh                # Shared utilities
│   │       ├── plan.sh                  # Create research plans
│   │       ├── execute.sh               # Set up execution
│   │       └── synthesize.sh            # Generate synthesis
│   ├── research/
│   │   └── 001-ai-safety/               # Auto-created research projects
│   │       ├── plan.md                  # Research plan
│   │       ├── sources.md               # Bibliography
│   │       ├── findings.md              # Research notes
│   │       └── synthesis.md             # Final report
│   └── templates/
│       ├── plan-template.md
│       ├── execution-template.md
│       ├── synthesis-template.md
│       └── constitution-template.md
├── .claude/
│   └── commands/
│       ├── researchkit_constitution.md  # Slash commands
│       ├── researchkit_plan.md
│       ├── researchkit_execute.md
│       ├── researchkit_synthesize.md
│       └── researchkit_sources.md
└── .git/                                # Git repository
```

---

## Slash Commands

ResearchKit provides Claude Code slash commands for guided research:

| Command | Purpose |
|---------|---------|
| `/researchkit.constitution` | Define research methodology and standards |
| `/researchkit.plan` | Create a structured research plan |
| `/researchkit.execute` | Execute research with proper documentation |
| `/researchkit.synthesize` | Generate comprehensive research report |
| `/researchkit.sources` | Manage bibliography and citations |

---

## Research Constitution

The constitution defines your research standards. Key sections:

### Citation Standards
- What citation format to use (APA, MLA, Chicago, etc.)
- When citations are required
- How to format different source types

### Source Quality Standards
- ⭐⭐⭐⭐⭐ Peer-reviewed academic
- ⭐⭐⭐⭐ Technical documentation / Industry reports
- ⭐⭐⭐ Expert analysis
- ⭐⭐ General articles
- ⭐ Use with caution (verify elsewhere)

### Research Process
- **Planning**: Define clear questions and strategy
- **Execution**: Systematic gathering with documentation
- **Synthesis**: Evidence-based analysis and conclusions

### Verification Requirements
- How many sources needed to verify claims
- Cross-referencing standards
- Handling conflicting information

---

## Best Practices

### During Planning
✅ Write a clear, specific research question
✅ Define realistic scope boundaries
✅ Plan your search strategy by phase
✅ Set measurable success criteria

### During Execution
✅ Cite sources immediately (don't wait!)
✅ Evaluate source quality and bias
✅ Document the research process
✅ Note emerging themes and questions
✅ Cross-verify important claims
✅ Commit progress regularly

### During Synthesis
✅ Answer the research question directly
✅ Base conclusions on evidence
✅ Cite every claim properly
✅ Acknowledge limitations
✅ Provide actionable recommendations
✅ Include complete bibliography

---

## Citation Examples

### APA Format
```
In-text: (Smith, 2023, p. 42)

Bibliography:
Smith, J. (2023). Modern authentication patterns. Journal of Web Security,
  15(3), 234-256. https://doi.org/10.1234/jws.2023.123
```

### IEEE Format
```
In-text: [1]

Bibliography:
[1] J. Smith, "Modern authentication patterns," Journal of Web Security,
    vol. 15, no. 3, pp. 234-256, June 2023.
```

---

## Git Workflow

ResearchKit uses git for organization:

```bash
# Each research project gets its own branch
research/001-topic-name
research/002-another-topic
research/003-more-research

# Your main branch stays clean
main
```

When research is complete:
```bash
# Push your research branch
git push -u origin research/001-topic-name

# Create a PR for review (optional)
gh pr create --title "Research: Topic Name" --body "..."

# Or merge directly
git checkout main
git merge research/001-topic-name
```

---

## CLI Commands

```bash
# Initialize a new project with AI support
research init <project-name> --ai <agent>
research init . --ai claude

# Supported AI agents:
# --ai claude    (Claude Code - recommended)
# --ai copilot   (GitHub Copilot)
# --ai gemini    (Gemini CLI)
# --ai cursor    (Cursor editor)
# --ai opencode  (OpenCode)
# --ai codex     (Codex CLI)

# Check installation and AI tool status
research check

# Show version
research --version

# Get help
research --help
```

---

## Examples

### Academic Research (Claude Code)

```bash
research init literature-review --ai claude
cd literature-review
claude
```

Constitution emphasizes:
- Peer-reviewed sources required
- APA citation format
- Cross-verification with 3+ sources
- Methodology documentation

Use Claude's slash commands for guided research workflow.

### Technical Documentation (GitHub Copilot)

```bash
research init framework-comparison --ai copilot
cd framework-comparison
code .  # Open in VS Code
```

Constitution emphasizes:
- Official documentation priority
- Version-specific information
- Reproducible examples
- Link verification

Use Copilot for inline documentation and code example suggestions.

### Data Analysis Research (Codex CLI)

```bash
research init data-analysis --ai codex
cd data-analysis
export CODEX_HOME="$(pwd)/.codex"
```

Constitution emphasizes:
- Reproducible analysis scripts
- Statistical rigor
- Data visualization standards
- Code documentation

Use Codex to generate analysis scripts and visualization code.

### AI/ML Research (Gemini CLI)

```bash
research init ml-benchmarks --ai gemini
cd ml-benchmarks
```

Constitution emphasizes:
- Recent research papers
- Benchmark comparisons
- Model architecture details
- Performance metrics

Use Gemini CLI for literature review and summarization.

### Market Research (Cursor)

```bash
research init industry-analysis --ai cursor
cd industry-analysis
cursor .
```

Constitution emphasizes:
- Industry report quality
- Data source verification
- Bias acknowledgment
- Recency requirements

Use Cursor's AI chat to help structure findings and analysis.

### Privacy-First Research (OpenCode + Ollama)

```bash
# Install Ollama and pull a research-optimized model
ollama pull qwen2.5:32b

# Initialize ResearchKit with OpenCode
research init medical-research --ai opencode
cd medical-research

# Start OpenCode (configured to use Ollama)
opencode
```

Constitution emphasizes:
- Data privacy and local processing
- Sensitive information handling
- HIPAA/GDPR compliance awareness
- Source verification without cloud dependencies

**Perfect for:**
- Medical and healthcare research
- Legal research and case analysis
- Proprietary business research
- Research with confidential data
- Academic research on a budget
- Offline research environments

**Benefits:**
- 💰 **Zero API costs** - Run unlimited queries locally
- 🔒 **Complete privacy** - Your research never leaves your machine
- 🚀 **Fast iterations** - No network latency or rate limits
- 📡 **Offline capable** - Research anywhere, anytime

Use OpenCode's slash commands (`/researchkit.plan`, `/researchkit.execute`, etc.) with the power of local AI models!

---

## Troubleshooting

### "Not in a ResearchKit project directory"

Make sure you've run `research init` in your project:
```bash
research init . --ai claude
```

### "Not on a research branch"

Use `/researchkit.plan` to create a research project, which automatically creates a branch.

### Scripts not executable

On Unix-like systems:
```bash
chmod +x .researchkit/scripts/bash/*.sh
```

### Claude Code commands not found

Verify `.claude/commands/` contains the ResearchKit command files:
```bash
ls .claude/commands/researchkit_*
```

---

## Contributing

We welcome contributions! Areas for improvement:

- [ ] PowerShell script implementation
- [x] Multiple AI agent support (Claude, Copilot, Gemini, Cursor, OpenCode, Codex)
- [ ] Export formats (PDF, LaTeX, etc.)
- [ ] Citation format validation
- [ ] Source quality auto-detection
- [ ] Research analytics dashboard
- [ ] MCP (Model Context Protocol) server integration

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Inspiration

ResearchKit is inspired by [SpecKit](https://github.com/github/spec-kit) from GitHub, which provides structured spec-driven development workflows. We adapted the architecture for research workflows with a focus on citation management and source quality.

---

## Comparison with SpecKit

| Feature | SpecKit | ResearchKit |
|---------|---------|-------------|
| Purpose | Software specifications | Research documentation |
| Workflow | Spec → Implement → Review | Plan → Execute → Synthesize |
| Focus | Code implementation | Source verification & citations |
| Output | Feature specs | Research reports |
| Quality Check | Test coverage | Citation completeness |

---

## Support

- 📖 [Documentation](https://github.com/yourusername/researchKit/wiki)
- 🐛 [Issues](https://github.com/yourusername/researchKit/issues)
- 💬 [Discussions](https://github.com/yourusername/researchKit/discussions)

---

## Roadmap

### Version 0.2.0
- [ ] PowerShell script implementation
- [x] Multiple AI agent support (Claude, Copilot, Gemini, Cursor, OpenCode, Codex)
- [ ] Enhanced citation format validation
- [ ] MCP server integration

### Version 0.3.0
- [ ] Export to PDF/LaTeX
- [ ] Research analytics
- [ ] Collaborative research features
- [ ] AI-powered source quality assessment

### Version 1.0.0
- [ ] Full documentation site
- [ ] Plugin system
- [ ] Template marketplace
- [ ] Multi-language support

---

**Happy Researching! 🔬**
