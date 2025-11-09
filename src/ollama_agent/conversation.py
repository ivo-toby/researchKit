"""Conversation engine with approval loops and tool execution."""

import json
import os
import subprocess
import tempfile
from typing import Any, Callable, Dict, List, Optional, Tuple
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from .ollama_client import OllamaClient
from .config import OllamaConfig


class ConversationEngine:
    """Manages interactive conversations with approval loops and tool execution."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        config: OllamaConfig,
        tool_registry: Dict[str, Callable],
        tool_definitions: List[Dict]
    ):
        """Initialize conversation engine.

        Args:
            ollama_client: Ollama client instance
            config: Ollama configuration
            tool_registry: Dictionary mapping tool names to functions
            tool_definitions: List of tool definitions for Ollama API
        """
        self.client = ollama_client
        self.config = config
        self.tool_registry = tool_registry
        self.tool_definitions = tool_definitions
        self.messages: List[Dict[str, Any]] = []
        self.console = Console()

    def add_system_message(self, content: str) -> None:
        """Add system message to conversation context.

        Args:
            content: System message content
        """
        self.messages.append({
            "role": "system",
            "content": content
        })

    def add_user_message(self, content: str) -> None:
        """Add user message to conversation context.

        Args:
            content: User message content
        """
        self.messages.append({
            "role": "user",
            "content": content
        })

    def generate_response(self, use_tools: bool = True) -> str:
        """Generate AI response using current conversation context.

        This method implements a tool execution loop:
        1. Call Ollama with tools
        2. If response includes tool_calls:
           a. Execute each tool
           b. Add tool results to messages
           c. Call Ollama again
           d. Repeat until no more tool calls
        3. Return final text response

        Args:
            use_tools: If True, provide tools to the model

        Returns:
            Final response text after all tool executions
        """
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call Ollama
            try:
                response = self.client.chat(
                    model=self.config.model,
                    messages=self.messages,
                    temperature=self.config.temperature,
                    tools=self.tool_definitions if use_tools else None
                )

                message = response.get('message', {})

                # Check for tool calls
                tool_calls = message.get('tool_calls', [])

                if tool_calls:
                    # Add assistant message with tool calls to history
                    self.messages.append(message)

                    # Execute tools
                    tool_results = self.execute_tool_calls(tool_calls)

                    # Add tool results to messages
                    for result in tool_results:
                        self.messages.append(result)

                    # Continue loop to get final response
                    continue
                else:
                    # No tool calls, this is the final response
                    content = message.get('content', '')

                    # Add to history
                    self.messages.append({
                        "role": "assistant",
                        "content": content
                    })

                    return content

            except Exception as e:
                self.console.print(f"[red]Error generating response: {e}[/red]")
                return ""

        # Max iterations reached
        self.console.print("[yellow]Warning: Max tool execution iterations reached[/yellow]")
        return ""

    def execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute a list of tool calls and return results.

        Args:
            tool_calls: List of tool call objects from Ollama

        Returns:
            List of tool result messages
        """
        results = []

        for tool_call in tool_calls:
            function_info = tool_call.get('function', {})
            tool_name = function_info.get('name', '')
            arguments = function_info.get('arguments', {})

            # Parse arguments if they're a string
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            # Display tool execution to user
            self._display_tool_execution(tool_name, arguments)

            # Execute tool
            try:
                result = self.client.execute_tool_call(
                    tool_name,
                    arguments,
                    self.tool_registry
                )

                # Add result message
                results.append({
                    "role": "tool",
                    "content": result
                })

            except Exception as e:
                error_result = json.dumps({"error": str(e)})
                results.append({
                    "role": "tool",
                    "content": error_result
                })
                self.console.print(f"[red]Tool execution error: {e}[/red]")

        return results

    def _display_tool_execution(self, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Display tool execution to user.

        Args:
            tool_name: Name of the tool being executed
            arguments: Tool arguments
        """
        if tool_name == "web_search":
            query = arguments.get('query', '')
            self.console.print(f"[cyan]🔍 Searching for: '{query}'[/cyan]")
        elif tool_name == "fetch_url":
            url = arguments.get('url', '')
            self.console.print(f"[cyan]📄 Fetching: {url}[/cyan]")
        elif tool_name == "parse_pdf":
            url = arguments.get('url', '')
            self.console.print(f"[cyan]📑 Parsing PDF: {url}[/cyan]")
        else:
            self.console.print(f"[cyan]🔧 Executing: {tool_name}[/cyan]")

    def approval_loop(
        self,
        content: str,
        prompt: str = "Approve? [y]es / [e]dit / [f]eedback",
        allow_edit: bool = True
    ) -> Tuple[str, bool]:
        """Interactive approval loop.

        Args:
            content: Content to approve
            prompt: Approval prompt text
            allow_edit: Whether to allow editing in $EDITOR

        Returns:
            Tuple of (final_content, approved)
        """
        while True:
            # Display content
            self.display(content)

            # Get user input
            self.console.print(f"\n{prompt}: ", end='')
            response = input().strip().lower()

            if response in ['y', 'yes']:
                return content, True

            elif response in ['e', 'edit'] and allow_edit:
                # Open in editor
                content = self._edit_in_editor(content)
                continue

            elif response in ['f', 'feedback']:
                # Get feedback and regenerate
                self.console.print("\n[cyan]Please provide feedback:[/cyan] ", end='')
                feedback = input().strip()

                if feedback:
                    self.add_user_message(feedback)
                    content = self.generate_response()
                    continue
                else:
                    self.console.print("[yellow]No feedback provided[/yellow]")
                    continue

            elif response in ['s', 'skip']:
                return content, False

            else:
                self.console.print("[yellow]Invalid input. Use y/e/f/s[/yellow]")
                continue

    def _edit_in_editor(self, content: str) -> str:
        """Open content in $EDITOR for manual editing.

        Args:
            content: Content to edit

        Returns:
            Edited content
        """
        editor = os.environ.get('EDITOR', 'nano')

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            subprocess.run([editor, temp_path], check=True)

            with open(temp_path, 'r') as f:
                edited_content = f.read()

            return edited_content

        except subprocess.CalledProcessError:
            self.console.print("[red]Editor exited with error[/red]")
            return content

        finally:
            os.unlink(temp_path)

    def display(self, content: str, title: str = "") -> None:
        """Display content with formatting.

        Args:
            content: Content to display
            title: Optional title for the display
        """
        if title:
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]\n")

        # Try to render as markdown
        try:
            md = Markdown(content)
            panel = Panel(md, expand=False, border_style="cyan")
            self.console.print(panel)
        except Exception:
            # Fallback to plain text
            self.console.print(content)

    def clear_history(self) -> None:
        """Reset message history for new phase."""
        self.messages = []
