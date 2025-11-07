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

__version__ = "0.1.0"

console = Console()
app = typer.Typer(
    name="research",
    help="CLI tool for structured research workflows with AI integration",
    add_completion=False,
    invoke_without_command=True,
)

# AI Agent configurations (currently supporting Claude)
AGENT_CONFIG = {
    "claude": {
        "name": "Claude Code",
        "commands_dir": ".claude/commands",
        "cli_check": "claude",
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


def get_template_dir() -> Path:
    """Get the templates directory from the package"""
    # In development, templates are in the repo root
    # When installed, they'll be in the package
    current_file = Path(__file__).resolve()

    # Try package location first (installed via uv)
    package_templates = current_file.parent.parent.parent / "templates"
    if package_templates.exists():
        return package_templates

    # Fall back to development location
    dev_templates = current_file.parent.parent.parent / "templates"
    return dev_templates


def init_git_repo(project_dir: Path, tracker: StepTracker):
    """Initialize git repository if not already initialized"""
    if (project_dir / ".git").exists():
        tracker.add_step("Git repository already initialized")
        return

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
    except FileNotFoundError:
        tracker.add_error("Git not found - please install git")


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
    if template_dir.exists():
        # Copy templates
        template_files = [
            "plan-template.md",
            "execution-template.md",
            "synthesis-template.md",
            "constitution-template.md",
        ]

        for template_file in template_files:
            src = template_dir / template_file
            if src.exists():
                dst = researchkit_dir / "templates" / template_file
                shutil.copy2(src, dst)

        tracker.add_step("Copied template files")

        # Copy scripts
        scripts_dir = template_dir.parent / "scripts"
        if scripts_dir.exists():
            # Copy bash scripts
            bash_src = scripts_dir / "bash"
            if bash_src.exists():
                for script in bash_src.glob("*.sh"):
                    dst = researchkit_dir / "scripts" / "bash" / script.name
                    shutil.copy2(script, dst)
                    # Make executable on Unix-like systems
                    if os.name != "nt":
                        os.chmod(dst, 0o755)

            # Copy PowerShell scripts
            ps_src = scripts_dir / "powershell"
            if ps_src.exists():
                for script in ps_src.glob("*.ps1"):
                    dst = researchkit_dir / "scripts" / "powershell" / script.name
                    shutil.copy2(script, dst)

            tracker.add_step("Copied shell scripts")

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


def create_claude_commands(project_dir: Path, ai_agent: str, tracker: StepTracker):
    """Create Claude Code command files"""
    if ai_agent != "claude":
        return

    commands_dir = project_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Copy command files from templates
    template_dir = get_template_dir()
    commands_template_dir = template_dir.parent / "claude_commands"

    if commands_template_dir.exists():
        for command_file in commands_template_dir.glob("*.md"):
            dst = commands_dir / command_file.name
            shutil.copy2(command_file, dst)
        tracker.add_step("Created Claude Code slash commands")
    else:
        tracker.add_error("Claude command templates not found")


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Project name or '.' for current directory"),
    ai: str = typer.Option("claude", help="AI agent to use (currently supports: claude)"),
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

    tracker.add_step(f"Selected AI agent: {AGENT_CONFIG[ai]['name']}")

    # Initialize git
    init_git_repo(project_dir, tracker)

    # Create ResearchKit structure
    create_researchkit_structure(project_dir, tracker)

    # Create AI-specific commands
    create_claude_commands(project_dir, ai, tracker)

    # Display results
    tracker.display()

    console.print("\n✨ [bold green]ResearchKit project initialized successfully![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. [cyan]cd {}[/cyan]".format(project_dir if project_name and project_name != "." else "."))
    console.print("  2. [cyan]claude[/cyan]  # Start Claude Code")
    console.print("  3. Use [cyan]/researchkit.constitution[/cyan] to define research principles")
    console.print("  4. Use [cyan]/researchkit.plan[/cyan] to start a research project\n")


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

    # Check Claude CLI
    try:
        subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            check=True,
            timeout=2
        )
        checks.add("[green]✓[/green] Claude CLI: Installed")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        checks.add("[yellow]○[/yellow] Claude CLI: Not found (optional)")

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
