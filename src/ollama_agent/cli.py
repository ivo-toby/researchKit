"""CLI entry point for Ollama standalone agent."""

import os
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .environment import EnvironmentManager
from .config import ConfigManager, OllamaConfig
from .ollama_client import OllamaClient
from .conversation import ConversationEngine
from .workflow import WorkflowOrchestrator
from .tools import TOOL_REGISTRY, TOOL_DEFINITIONS


console = Console()


def show_banner():
    """Display welcome banner."""
    banner = f"""
[bold cyan]ResearchKit Ollama Agent[/bold cyan] v{__version__}

Lightweight standalone research agent using local Ollama models
    """
    console.print(Panel(banner, border_style="cyan"))


def get_ollama_url() -> str:
    """Get Ollama URL from environment or default.

    Returns:
        Ollama URL
    """
    return os.environ.get('OLLAMA_URL', 'http://localhost:11434')


def prompt_model_selection(models: list[str]) -> str:
    """Prompt user to select a model from list.

    Args:
        models: List of available model names

    Returns:
        Selected model name
    """
    console.print("\n[cyan]Available tool-compatible models:[/cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Model Name")

    for i, model in enumerate(models, 1):
        table.add_row(str(i), model)

    console.print(table)

    while True:
        console.print("\n[cyan]Select a model (enter number):[/cyan] ", end='')
        try:
            choice = input().strip()
            index = int(choice) - 1

            if 0 <= index < len(models):
                return models[index]
            else:
                console.print("[red]Invalid selection. Please try again.[/red]")

        except (ValueError, KeyboardInterrupt):
            console.print("\n[red]Invalid input. Please enter a number.[/red]")


def main():
    """Main entry point for research-ollama CLI."""
    show_banner()

    # Get Ollama URL (from env or default)
    ollama_url = get_ollama_url()

    # 1. Environment checks
    console.print("\n[bold]Checking environment...[/bold]")
    env = EnvironmentManager()

    # Check Ollama
    console.print("  Checking Ollama...", end=' ')
    if not env.check_ollama(ollama_url):
        console.print("[red]✗[/red]")
        console.print(f"\n[red]❌ Ollama is not running at {ollama_url}[/red]")
        console.print("\n[cyan]Please start Ollama:[/cyan]")
        console.print("  ollama serve")
        console.print("\n[cyan]Or set custom URL:[/cyan]")
        console.print("  export OLLAMA_URL=http://your-ollama-server:11434")
        sys.exit(1)
    console.print("[green]✓[/green]")

    # Check git
    console.print("  Checking git...", end=' ')
    if not env.check_git():
        console.print("[red]✗[/red]")
        if not env.prompt_git_init():
            sys.exit(1)
    else:
        console.print("[green]✓[/green]")

    # Check researchKit
    console.print("  Checking researchKit...", end=' ')
    if not env.check_researchkit_initialized():
        console.print("[red]✗[/red]")
        console.print("\n[yellow]⚠️  ResearchKit not initialized in this directory.[/yellow]")
        console.print("[cyan]Initialize researchKit? [y/N]:[/cyan] ", end='')
        response = input().strip().lower()

        if response in ['y', 'yes']:
            if not env.initialize_researchkit():
                console.print("[red]Failed to initialize researchKit[/red]")
                sys.exit(1)
        else:
            console.print("\n[red]ResearchKit is required. Exiting.[/red]")
            sys.exit(1)
    else:
        console.print("[green]✓[/green]")

    # 2. Config management
    console.print("\n[bold]Loading configuration...[/bold]")
    config_mgr = ConfigManager()

    if not config_mgr.exists():
        # First-time setup: model selection
        console.print("  No configuration found. Setting up...\n")

        client = OllamaClient(ollama_url)

        # Only show models that support tool calling
        try:
            models = client.list_models(tool_compatible_only=True)
        except Exception as e:
            console.print(f"[red]❌ Failed to list models: {e}[/red]")
            sys.exit(1)

        if not models:
            console.print("[red]❌ No tool-compatible models found.[/red]\n")
            console.print("[cyan]Install a compatible model:[/cyan]")
            console.print("  ollama pull llama3.2")
            console.print("  ollama pull llama3.1")
            console.print("  ollama pull mistral-nemo")
            console.print("  ollama pull qwen2.5")
            sys.exit(1)

        selected_model = prompt_model_selection(models)

        config = OllamaConfig(
            ollama_url=ollama_url,
            model=selected_model,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        if not config_mgr.save(config):
            console.print("[red]Failed to save configuration[/red]")
            sys.exit(1)

        console.print(f"\n[green]✓ Configuration saved[/green]")
        console.print(f"  Model: {selected_model}")

        # Commit config
        import subprocess
        try:
            subprocess.run(
                ["git", "add", ".researchkit/config/"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "chore: Initialize Ollama agent config"],
                check=True,
                capture_output=True
            )
            console.print("[green]✓ Committed configuration to git[/green]")
        except subprocess.CalledProcessError:
            console.print("[yellow]⚠ Failed to commit to git[/yellow]")

    else:
        config = config_mgr.load()

        if config is None:
            console.print("[red]Failed to load configuration[/red]")
            sys.exit(1)

        console.print(f"[green]✓ Using model: {config.model}[/green]")

    # 3. Test Ollama connection with selected model
    client = OllamaClient(config.ollama_url)
    connected, message = client.test_connection()

    if not connected:
        console.print(f"\n[red]❌ {message}[/red]")
        sys.exit(1)

    # 4. Prompt for research topic
    console.print("\n" + "═" * 60)
    console.print("\n[bold cyan]🔍 What would you like to research?[/bold cyan]")
    console.print("[dim](Press Ctrl+C to cancel)[/dim]\n")
    console.print("[cyan]Topic:[/cyan] ", end='')

    try:
        topic = input().strip()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)

    if not topic:
        console.print("\n[red]No topic provided. Exiting.[/red]")
        sys.exit(0)

    console.print("\n" + "═" * 60)

    # 5. Start research workflow with tools
    conversation = ConversationEngine(
        client,
        config,
        TOOL_REGISTRY,
        TOOL_DEFINITIONS
    )

    workflow = WorkflowOrchestrator(conversation, config)

    # Run full workflow
    try:
        workflow.run_full_workflow(topic)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Research cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error during research: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
