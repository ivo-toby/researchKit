"""
ResearchKit CLI - Structured research workflows with AI integration
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

__version__ = "0.1.1"

console = Console()
app = typer.Typer(
    name="research",
    help="CLI tool for structured research workflows with AI integration",
    add_completion=False,
    invoke_without_command=True,
)

# AI Agent configurations
AGENT_CONFIG = {
    "claude": {
        "name": "Claude Code",
        "commands_dir": ".claude/commands",
        "cli_check": "claude",
        "requires_cli": False,
        "install_url": None,
    },
    "copilot": {
        "name": "GitHub Copilot",
        "commands_dir": ".github/copilot",
        "cli_check": None,
        "requires_cli": False,
        "install_url": None,
    },
    "gemini": {
        "name": "Gemini CLI",
        "commands_dir": ".gemini",
        "cli_check": "gemini",
        "requires_cli": True,
        "install_url": "https://github.com/google-gemini/gemini-cli",
    },
    "cursor": {
        "name": "Cursor",
        "commands_dir": ".cursor",
        "cli_check": None,
        "requires_cli": False,
        "install_url": None,
    },
    "opencode": {
        "name": "OpenCode",
        "commands_dir": ".opencode",
        "cli_check": "opencode",
        "requires_cli": True,
        "install_url": "https://opencode.ai",
    },
    "codex": {
        "name": "Codex CLI",
        "commands_dir": ".codex",
        "cli_check": "codex",
        "requires_cli": True,
        "install_url": "https://github.com/openai/codex",
    }
}


class StepTracker:
    """Track and display progress for multi-step operations"""

    def __init__(self):
        self.steps = []
        self.tree = Tree("🔬 ResearchKit Setup")

    def add_step(self, message: str, status: str = "✓"):
        """Add a completed step"""
        self.tree.add(f"[green]{status}[/green] {message}")

    def add_error(self, message: str):
        """Add an error step"""
        self.tree.add(f"[red]✗[/red] {message}")

    def display(self):
        """Display the tree"""
        console.print(self.tree)


def show_banner():
    """Display ResearchKit banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║         🔬 ResearchKit CLI            ║
    ║                                       ║
    ║   Structured Research Workflows       ║
    ║        with AI Integration            ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_cli_tool(tool_name: str) -> bool:
    """Check if a CLI tool is available"""
    try:
        subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            check=True,
            timeout=2
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_common_researchkit_sections() -> str:
    """Get common ResearchKit integration sections for README files"""
    return """## ResearchKit Integration

When working on research projects:
1. Use the `.researchkit/` directory structure
2. Follow the research workflow: Plan → Execute → Synthesize
3. Maintain proper citations in `sources.md`
4. Document findings in `findings.md`
5. Create synthesis reports in `synthesis.md`

## Research Commands

Run these bash scripts to manage your research:

```bash
# Create a new research plan
bash .researchkit/scripts/bash/plan.sh "Research Topic"

# Set up execution
bash .researchkit/scripts/bash/execute.sh

# Generate synthesis
bash .researchkit/scripts/bash/synthesize.sh
```
"""


def get_template_dir() -> Path:
    """Get the templates directory from the package"""
    current_file = Path(__file__).resolve()

    # Try system location first (Python's sys.prefix/share) - for installed packages
    sys_templates = Path(sys.prefix) / "share" / "research-cli" / "templates"
    if sys_templates.exists():
        return sys_templates

    # Try development location (repo root) - for editable installs
    dev_templates = current_file.parent.parent.parent / "templates"
    if dev_templates.exists():
        return dev_templates

    # Try alternative install locations
    site_packages = current_file.parent.parent
    installed_templates = site_packages / "share" / "research-cli" / "templates"
    if installed_templates.exists():
        return installed_templates

    # Return dev location as fallback with a warning path
    return dev_templates


def init_git_repo(project_dir: Path, tracker: StepTracker):
    """Initialize git repository if not already initialized"""
    if (project_dir / ".git").exists():
        tracker.add_step("Git repository already initialized")
        return

    # Ask user if they want to initialize git
    console.print("\n[yellow]⚠[/yellow]  No git repository found in the current directory.")
    response = typer.confirm("Would you like to run 'git init' to initialize a git repository?")

    if not response:
        console.print("\n[red]✗ ResearchKit needs Git to function[/red]\n")
        raise typer.Exit(1)

    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            capture_output=True
        )
        tracker.add_step("Initialized git repository")
    except subprocess.CalledProcessError as e:
        tracker.add_error(f"Failed to initialize git: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        tracker.add_error("Git not found - please install git")
        raise typer.Exit(1)


def create_researchkit_structure(project_dir: Path, tracker: StepTracker):
    """Create the .researchkit directory structure"""
    researchkit_dir = project_dir / ".researchkit"

    # Create main directories
    directories = [
        researchkit_dir / "memory",
        researchkit_dir / "scripts" / "bash",
        researchkit_dir / "scripts" / "powershell",
        researchkit_dir / "research",
        researchkit_dir / "templates",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    tracker.add_step("Created .researchkit directory structure")

    # Copy template files
    template_dir = get_template_dir()
    if not template_dir.exists():
        tracker.add_error(f"Template directory not found: {template_dir}")
        tracker.add_error("Templates must be included in package distribution")
    else:
        # Copy templates
        template_files = [
            "plan-template.md",
            "execution-template.md",
            "synthesis-template.md",
            "constitution-template.md",
        ]

        copied_count = 0
        for template_file in template_files:
            src = template_dir / template_file
            if src.exists():
                dst = researchkit_dir / "templates" / template_file
                shutil.copy2(src, dst)
                copied_count += 1
            else:
                tracker.add_error(f"Template file not found: {template_file}")

        if copied_count > 0:
            tracker.add_step(f"Copied {copied_count} template files")
        else:
            tracker.add_error("No template files could be copied")

    # Copy scripts
    scripts_dir = template_dir.parent / "scripts"
    if not scripts_dir.exists():
        tracker.add_error(f"Scripts directory not found: {scripts_dir}")
    else:
        script_count = 0
        # Copy bash scripts
        bash_src = scripts_dir / "bash"
        if bash_src.exists():
            for script in bash_src.glob("*.sh"):
                dst = researchkit_dir / "scripts" / "bash" / script.name
                shutil.copy2(script, dst)
                # Make executable on Unix-like systems
                if os.name != "nt":
                    os.chmod(dst, 0o755)
                script_count += 1
        else:
            tracker.add_error("Bash scripts directory not found")

        # Copy PowerShell scripts
        ps_src = scripts_dir / "powershell"
        if ps_src.exists():
            for script in ps_src.glob("*.ps1"):
                dst = researchkit_dir / "scripts" / "powershell" / script.name
                shutil.copy2(script, dst)
                script_count += 1

        if script_count > 0:
            tracker.add_step(f"Copied {script_count} shell scripts")
        else:
            tracker.add_error("No shell scripts could be copied")

    # Create initial constitution
    constitution_path = researchkit_dir / "memory" / "constitution.md"
    if not constitution_path.exists():
        constitution_path.write_text("""# Research Constitution

## Research Methodology Principles

### Citation Standards
- All claims must be properly cited with sources
- Prefer peer-reviewed sources when available
- Cross-reference important claims with multiple sources
- Maintain clear bibliography in sources.md

### Source Quality Standards
- Evaluate source credibility and bias
- Note publication date and relevance
- Distinguish between primary and secondary sources
- Document limitations of sources

### Research Process
1. **Planning Phase**: Define clear research questions and scope
2. **Execution Phase**: Systematic information gathering with proper documentation
3. **Synthesis Phase**: Analysis and conclusion drawing with evidence

### Verification Requirements
- Cross-check facts across multiple sources
- Question assumptions and biases
- Document conflicting information
- Mark uncertain claims clearly

---
*This constitution guides all research activities in this project.*
""")
        tracker.add_step("Created research constitution")


def create_agent_commands(project_dir: Path, ai_agent: str, tracker: StepTracker):
    """Create AI agent-specific command files and directories"""
    if ai_agent not in AGENT_CONFIG:
        return

    agent_config = AGENT_CONFIG[ai_agent]
    commands_dir = project_dir / agent_config["commands_dir"]
    commands_dir.mkdir(parents=True, exist_ok=True)

    # For Claude, copy command files from templates
    if ai_agent == "claude":
        template_dir = get_template_dir()
        commands_template_dir = template_dir.parent / "claude_commands"

        if commands_template_dir.exists():
            for command_file in commands_template_dir.glob("*.md"):
                dst = commands_dir / command_file.name
                shutil.copy2(command_file, dst)
            tracker.add_step("Created Claude Code slash commands")
        else:
            tracker.add_error("Claude command templates not found")

    # For GitHub Copilot, create a README with instructions
    elif ai_agent == "copilot":
        readme_path = commands_dir / "README.md"
        readme_content = f"""# ResearchKit with GitHub Copilot

This directory contains ResearchKit configuration for GitHub Copilot.

## Usage

GitHub Copilot works within your IDE (VS Code, JetBrains, etc.) to provide AI-powered code suggestions.

{get_common_researchkit_sections()}

## Copilot Tips for Research

- Ask Copilot to help format citations
- Use Copilot to generate search query suggestions
- Have Copilot help structure your findings
- Let Copilot assist with summarizing sources
"""
        readme_path.write_text(readme_content)
        tracker.add_step(f"Created {agent_config['name']} configuration")

    # For Gemini CLI, create configuration and instructions
    elif ai_agent == "gemini":
        readme_path = commands_dir / "README.md"
        readme_content = f"""# ResearchKit with Gemini CLI

This directory contains ResearchKit configuration for Gemini CLI.

## Installation

Install Gemini CLI from: https://github.com/google-gemini/gemini-cli

{get_common_researchkit_sections()}

## Using Gemini CLI for Research

Gemini CLI can help with:
- Literature review and summarization
- Citation formatting and verification
- Research question refinement
- Data analysis and interpretation
- Source quality assessment

Example commands:
```bash
# Ask Gemini to help refine your research question
gemini chat "Help me refine this research question: [your question]"

# Get help with citation formatting
gemini chat "Format this source as APA citation: [source details]"

# Summarize research findings
gemini chat "Summarize these key points: [your findings]"
```
"""
        readme_path.write_text(readme_content)
        tracker.add_step(f"Created {agent_config['name']} configuration")

    # For Cursor, create configuration with AI rules
    elif ai_agent == "cursor":
        readme_path = commands_dir / "README.md"
        readme_content = f"""# ResearchKit with Cursor

This directory contains ResearchKit configuration for Cursor AI editor.

## About Cursor

Cursor is an AI-powered code editor built on VS Code with integrated AI assistance.

{get_common_researchkit_sections()}

## Using Cursor for Research

Cursor's AI can help with:
- Structuring research documents
- Formatting citations consistently
- Summarizing research findings
- Generating literature review outlines
- Analyzing research data

### Tips

- Use Cursor's chat to ask about citation formats
- Highlight text and ask Cursor to refine or summarize
- Use Cursor to help maintain consistent document structure
- Ask Cursor to help verify citation completeness
"""
        readme_path.write_text(readme_content)
        # Create .cursorrules file for AI context
        cursorrules_path = commands_dir / ".cursorrules"
        cursorrules_path.write_text("""# ResearchKit Cursor AI Rules

## Project Context
This is a ResearchKit research project following structured research workflows.

## Research Workflow
1. **Plan**: Define research questions, objectives, and methodology
2. **Execute**: Gather sources, document findings, maintain citations
3. **Synthesize**: Analyze findings and create comprehensive reports

## Key Principles
- All claims must be properly cited
- Maintain source quality ratings (1-5 stars)
- Follow the research constitution in `.researchkit/memory/constitution.md`
- Keep findings organized chronologically
- Cross-reference important claims

## File Structure
- `plan.md`: Research question, objectives, and strategy
- `sources.md`: Bibliography with quality ratings
- `findings.md`: Research notes and discoveries
- `synthesis.md`: Final analysis and conclusions

## Citation Standards
- Use consistent citation format throughout
- Include source URLs and access dates
- Rate source quality and note any bias
- Maintain complete bibliography

## When Editing Research Files
- Preserve existing citation formats
- Maintain chronological order in findings
- Keep source quality ratings consistent
- Follow the established document structure
""")
        tracker.add_step(f"Created {agent_config['name']} configuration with .cursorrules")

    # For OpenCode, create configuration and prompts
    elif ai_agent == "opencode":
        readme_path = commands_dir / "README.md"
        readme_content = f"""# ResearchKit with OpenCode

This directory contains ResearchKit configuration for OpenCode AI.

## Installation

Install OpenCode from: https://opencode.ai

{get_common_researchkit_sections()}

## Using OpenCode for Research

OpenCode can assist with:
- Research document generation
- Citation management and formatting
- Literature review synthesis
- Data analysis and visualization
- Research methodology design

### Example Workflows

**Planning Research:**
```bash
opencode "Help me create a research plan for studying [topic]"
```

**Managing Citations:**
```bash
opencode "Format these sources as APA citations: [source list]"
```

**Synthesizing Findings:**
```bash
opencode "Summarize these research findings into key themes: [findings]"
```

### Tips

- Use OpenCode to help structure your research documents
- Ask for help with citation formatting
- Request summaries of complex sources
- Get assistance with research methodology
- Use OpenCode to identify gaps in your research
"""
        readme_path.write_text(readme_content)
        # Create prompts directory with research-specific prompts
        prompts_dir = commands_dir / "prompts"
        prompts_dir.mkdir(exist_ok=True)

        research_prompt = prompts_dir / "research_assistant.txt"
        research_prompt.write_text("""You are a research assistant helping with structured research using ResearchKit.

Your role is to help maintain research quality by:
1. Ensuring all claims are properly cited
2. Helping format citations consistently
3. Identifying gaps in research coverage
4. Suggesting relevant sources
5. Maintaining research organization

Always follow the research constitution in .researchkit/memory/constitution.md

Key files:
- plan.md: Research questions and methodology
- sources.md: Bibliography with quality ratings
- findings.md: Research notes and discoveries
- synthesis.md: Final analysis and conclusions

When helping with research:
- Ask for citations when claims are made
- Suggest source quality ratings (1-5 stars)
- Maintain chronological organization
- Cross-reference important findings
- Follow established citation format
""")
        tracker.add_step(f"Created {agent_config['name']} configuration with prompts")

    # For Codex CLI, create configuration with environment setup
    elif ai_agent == "codex":
        readme_path = commands_dir / "README.md"
        codex_home_path = (project_dir / agent_config["commands_dir"]).as_posix()
        readme_content = f"""# ResearchKit with Codex CLI

This directory contains ResearchKit configuration for OpenAI Codex CLI.

## Installation

Install Codex CLI from: https://github.com/openai/codex

## Environment Setup

**IMPORTANT:** Set the CODEX_HOME environment variable to use this configuration:

### Bash/Zsh
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export CODEX_HOME="{codex_home_path}"
```

### Fish
Add to your `~/.config/fish/config.fish`:
```fish
set -x CODEX_HOME "{codex_home_path}"
```

### PowerShell
Add to your PowerShell profile:
```powershell
$env:CODEX_HOME = "{codex_home_path}"
```

Then restart your shell or run `source ~/.bashrc` (or equivalent).

{get_common_researchkit_sections()}

## Using Codex CLI for Research

Codex can help with:
- Code generation for data analysis
- Research automation scripts
- Data processing and transformation
- Statistical analysis code
- Visualization generation

### Example Commands

**Generate Analysis Code:**
```bash
codex "Write a Python script to analyze [data type]"
```

**Data Processing:**
```bash
codex "Create a script to clean and process this CSV data"
```

**Visualization:**
```bash
codex "Generate matplotlib code to visualize [data description]"
```

### Tips

- Use Codex for research-related code generation
- Ask Codex to help with data analysis scripts
- Generate test code for research automation
- Create data pipeline scripts
- Build research tools and utilities
"""
        readme_path.write_text(readme_content)
        # Create config file
        config_path = commands_dir / "config.json"
        config_path.write_text("""{
  "research_mode": true,
  "context": "ResearchKit structured research project",
  "files": {
    "plan": ".researchkit/research/*/plan.md",
    "findings": ".researchkit/research/*/findings.md",
    "sources": ".researchkit/research/*/sources.md",
    "synthesis": ".researchkit/research/*/synthesis.md"
  },
  "guidelines": [
    "Follow research constitution",
    "Maintain citation standards",
    "Ensure code is well-documented",
    "Generate reproducible analysis"
  ]
}
""")
        tracker.add_step(f"Created {agent_config['name']} configuration")

        # Display environment setup message
        console.print(f"\n[yellow]⚠  Important:[/yellow] Set CODEX_HOME environment variable:")
        console.print(f"[cyan]   export CODEX_HOME=\"{codex_home_path}\"[/cyan]\n")

    # For other agents, create basic directory structure
    else:
        tracker.add_step(f"Created {agent_config['name']} directory structure")


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Project name or '.' for current directory"),
    ai: str = typer.Option("claude", help="AI agent to use (supports: claude, copilot, gemini, cursor, opencode, codex)"),
):
    """
    Initialize a new ResearchKit project with structured research workflow support.

    Examples:
        research init my-research-project
        research init . --ai claude
    """
    show_banner()
    tracker = StepTracker()

    # Determine project directory
    if project_name is None or project_name == ".":
        project_dir = Path.cwd()
        tracker.add_step(f"Using current directory: {project_dir}")
    else:
        project_dir = Path.cwd() / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        tracker.add_step(f"Created project directory: {project_dir}")

    # Validate AI agent
    if ai not in AGENT_CONFIG:
        console.print(f"[red]Error:[/red] Unsupported AI agent: {ai}")
        console.print(f"Supported agents: {', '.join(AGENT_CONFIG.keys())}")
        raise typer.Exit(1)

    agent_config = AGENT_CONFIG[ai]
    tracker.add_step(f"Selected AI agent: {agent_config['name']}")

    # Check if CLI tool is required and available
    if agent_config.get("requires_cli") and agent_config.get("cli_check"):
        cli_tool = agent_config["cli_check"]
        if not check_cli_tool(cli_tool):
            console.print(f"\n[yellow]⚠[/yellow]  {agent_config['name']} CLI tool not found")
            console.print(f"[yellow]   The '{cli_tool}' command is not available[/yellow]")
            if agent_config.get("install_url"):
                console.print(f"[yellow]   Install from: {agent_config['install_url']}[/yellow]")
            console.print(f"\n[red]✗ {agent_config['name']} requires the CLI tool to be installed[/red]\n")
            raise typer.Exit(1)
        tracker.add_step(f"Verified {cli_tool} CLI tool is installed")

    # Initialize git
    init_git_repo(project_dir, tracker)

    # Create ResearchKit structure
    create_researchkit_structure(project_dir, tracker)

    # Create AI-specific commands
    create_agent_commands(project_dir, ai, tracker)

    # Display results
    tracker.display()

    console.print("\n✨ [bold green]ResearchKit project initialized successfully![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. [cyan]cd {}[/cyan]".format(project_dir if project_name and project_name != "." else "."))

    # Dynamic step 2 based on AI agent
    if ai == "claude":
        console.print("  2. [cyan]claude[/cyan]  # Start Claude Code")
        console.print("  3. Use [cyan]/researchkit.constitution[/cyan] to define research principles")
        console.print("  4. Use [cyan]/researchkit.plan[/cyan] to start a research project\n")
    elif ai == "opencode":
        console.print("  2. [cyan]opencode[/cyan]  # Start OpenCode")
        console.print("  3. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  4. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")
    elif ai == "gemini":
        console.print("  2. [cyan]gemini chat[/cyan]  # Start Gemini CLI")
        console.print("  3. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  4. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")
    elif ai == "codex":
        console.print("  2. Set CODEX_HOME environment variable (see [cyan]{}/README.md[/cyan])".format(agent_config["commands_dir"]))
        console.print("  3. [cyan]codex[/cyan]  # Start Codex CLI")
        console.print("  4. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  5. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")
    elif ai == "copilot":
        console.print("  2. Open this project in your IDE (VS Code, JetBrains, etc.)")
        console.print("  3. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  4. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")
    elif ai == "cursor":
        console.print("  2. [cyan]cursor .[/cyan]  # Open project in Cursor")
        console.print("  3. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  4. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")
    else:
        console.print("  2. Review [cyan].researchkit/memory/constitution.md[/cyan] to define research principles")
        console.print("  3. Run [cyan]bash .researchkit/scripts/bash/plan.sh \"Your Topic\"[/cyan] to start a research project\n")


@app.command()
def check():
    """
    Check if required tools are installed (git, AI CLI tools).
    """
    show_banner()

    checks = Tree("🔍 Checking Requirements")

    # Check git
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        checks.add(f"[green]✓[/green] Git: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        checks.add("[red]✗[/red] Git: Not found")

    # Check all AI agent CLI tools
    for agent_name, agent_config in AGENT_CONFIG.items():
        cli_tool = agent_config.get("cli_check")
        if cli_tool:
            is_required = agent_config.get("requires_cli", False)
            if check_cli_tool(cli_tool):
                checks.add(f"[green]✓[/green] {agent_config['name']}: Installed")
            else:
                status = "required" if is_required else "optional"
                color = "red" if is_required else "yellow"
                symbol = "✗" if is_required else "○"
                checks.add(f"[{color}]{symbol}[/{color}] {agent_config['name']}: Not found ({status})")

    console.print(checks)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """
    ResearchKit CLI - Structured research workflows with AI integration
    """
    if version:
        console.print(f"ResearchKit CLI v{__version__}")
        raise typer.Exit(0)

    # If no subcommand was specified, show help
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print("\n[bold]Usage:[/bold] research [COMMAND]\n")
        console.print("[bold]Commands:[/bold]")
        console.print("  init   - Initialize a new ResearchKit project")
        console.print("  check  - Verify required tools are installed\n")
        console.print("[dim]Run 'research --help' for more information[/dim]\n")


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
