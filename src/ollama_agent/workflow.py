"""Workflow orchestrator for research phases."""

import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console

from .conversation import ConversationEngine
from .config import OllamaConfig
from .prompts import constitution, plan, execute, synthesize


class WorkflowOrchestrator:
    """Orchestrates the research workflow phases."""

    def __init__(
        self,
        conversation: ConversationEngine,
        config: OllamaConfig,
        project_dir: Optional[Path] = None
    ):
        """Initialize workflow orchestrator.

        Args:
            conversation: Conversation engine instance
            config: Ollama configuration
            project_dir: Project directory path
        """
        self.conversation = conversation
        self.config = config
        self.project_dir = project_dir or Path.cwd()
        self.console = Console()
        self.researchkit_dir = self.project_dir / ".researchkit"

    def run_constitution_phase(self) -> bool:
        """Guide user through constitution definition.

        Returns:
            True if completed successfully, False otherwise
        """
        self.console.print("\n[bold cyan]═══ PHASE 1: CONSTITUTION ═══[/bold cyan]\n")

        # Load existing constitution if present
        constitution_path = self.researchkit_dir / "memory" / "constitution.md"
        current_constitution = ""

        if constitution_path.exists():
            with open(constitution_path, 'r', encoding='utf-8') as f:
                current_constitution = f.read()
            self.console.print("📖 Loading existing constitution...")
        else:
            self.console.print("📝 Creating new constitution...")

        # Set up conversation
        self.conversation.clear_history()
        system_prompt = constitution.get_constitution_system_prompt(current_constitution)
        user_prompt = constitution.get_constitution_user_prompt()

        self.conversation.add_system_message(system_prompt)
        self.conversation.add_user_message(user_prompt)

        # Generate constitution
        constitution_text = self.conversation.generate_response()

        # Approval loop
        final_constitution, approved = self.conversation.approval_loop(
            constitution_text,
            prompt="Approve constitution? [y]es / [e]dit / [f]eedback"
        )

        if approved:
            # Save constitution
            constitution_path.parent.mkdir(parents=True, exist_ok=True)
            with open(constitution_path, 'w', encoding='utf-8') as f:
                f.write(final_constitution)

            self.console.print(f"✓ Saved constitution to {constitution_path}")

            # Git commit
            try:
                subprocess.run(
                    ["git", "add", str(constitution_path)],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "docs: Update research constitution"],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                self.console.print("✓ Committed to git")
            except subprocess.CalledProcessError:
                self.console.print("[yellow]⚠ Failed to commit to git[/yellow]")

            return True
        else:
            self.console.print("[yellow]Constitution phase skipped[/yellow]")
            return False

    def run_plan_phase(self, topic: str) -> bool:
        """Create research plan with user approval.

        Args:
            topic: Research topic from user

        Returns:
            True if plan approved and saved, False otherwise
        """
        self.console.print("\n[bold cyan]═══ PHASE 2: PLANNING ═══[/bold cyan]\n")
        self.console.print(f"📋 Creating research plan for: [bold]{topic}[/bold]\n")

        # Call bash script to set up plan structure
        plan_script = self.researchkit_dir / "scripts" / "bash" / "plan.sh"

        if plan_script.exists():
            try:
                result = subprocess.run(
                    [str(plan_script), topic],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    self.console.print(f"[red]Error running plan.sh: {result.stderr}[/red]")
                    return False

                self.console.print("✓ Created research project structure")

            except subprocess.TimeoutExpired:
                self.console.print("[red]Plan script timed out[/red]")
                return False
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                return False

        # Load constitution and template
        constitution_text = self._load_file(self.researchkit_dir / "memory" / "constitution.md")
        template_text = self._load_file(self.researchkit_dir / "templates" / "plan-template.md")

        # Set up conversation
        self.conversation.clear_history()
        system_prompt = plan.get_plan_system_prompt(constitution_text, template_text)
        user_prompt = plan.get_plan_user_prompt(topic)

        self.conversation.add_system_message(system_prompt)
        self.conversation.add_user_message(user_prompt)

        # Generate plan
        plan_text = self.conversation.generate_response()

        # Approval loop
        final_plan, approved = self.conversation.approval_loop(
            plan_text,
            prompt="Approve plan? [y]es / [e]dit / [f]eedback"
        )

        if approved:
            # Find the research directory (most recent)
            research_dir = self._get_current_research_dir()

            if research_dir:
                plan_path = research_dir / "plan.md"
                with open(plan_path, 'w', encoding='utf-8') as f:
                    f.write(final_plan)

                self.console.print(f"✓ Saved plan to {plan_path}")

                # Git commit
                try:
                    subprocess.run(
                        ["git", "add", str(research_dir)],
                        cwd=self.project_dir,
                        check=True,
                        capture_output=True
                    )
                    subprocess.run(
                        ["git", "commit", "-m", f"docs: Add research plan for {topic}"],
                        cwd=self.project_dir,
                        check=True,
                        capture_output=True
                    )
                    self.console.print("✓ Committed to git")
                except subprocess.CalledProcessError:
                    self.console.print("[yellow]⚠ Failed to commit to git[/yellow]")

                return True
            else:
                self.console.print("[red]Could not find research directory[/red]")
                return False
        else:
            self.console.print("[yellow]Plan phase skipped[/yellow]")
            return False

    def run_execute_phase(self) -> bool:
        """Execute research with iterative findings.

        Returns:
            True if research completed, False otherwise
        """
        self.console.print("\n[bold cyan]═══ PHASE 3: EXECUTION ═══[/bold cyan]\n")

        # Call bash script to set up execution structure
        execute_script = self.researchkit_dir / "scripts" / "bash" / "execute.sh"

        if execute_script.exists():
            try:
                subprocess.run(
                    [str(execute_script)],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True,
                    timeout=30
                )
                self.console.print("✓ Set up execution structure")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.console.print(f"[yellow]⚠ Execute script warning: {e}[/yellow]")

        # Get research directory
        research_dir = self._get_current_research_dir()
        if not research_dir:
            self.console.print("[red]No active research project found[/red]")
            return False

        # Load plan and constitution
        plan_text = self._load_file(research_dir / "plan.md")
        constitution_text = self._load_file(self.researchkit_dir / "memory" / "constitution.md")

        # Set up conversation
        self.conversation.clear_history()
        system_prompt = execute.get_execute_system_prompt(plan_text, constitution_text)
        user_prompt = execute.get_execute_user_prompt()

        self.conversation.add_system_message(system_prompt)
        self.conversation.add_user_message(user_prompt)

        # Generate findings (with tool calling)
        self.console.print("🔬 Conducting research...\n")
        findings_text = self.conversation.generate_response(use_tools=True)

        # Approval loop
        final_findings, approved = self.conversation.approval_loop(
            findings_text,
            prompt="Approve findings? [y]es / [e]dit / [f]eedback"
        )

        if approved:
            # Save findings
            findings_path = research_dir / "findings.md"
            with open(findings_path, 'w', encoding='utf-8') as f:
                f.write(final_findings)

            self.console.print(f"✓ Saved findings to {findings_path}")

            # Update sources.md (extract URLs from conversation history)
            self._update_sources(research_dir)

            # Git commit
            try:
                subprocess.run(
                    ["git", "add", str(research_dir)],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "docs: Document research findings"],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                self.console.print("✓ Committed to git")
            except subprocess.CalledProcessError:
                self.console.print("[yellow]⚠ Failed to commit to git[/yellow]")

            return True
        else:
            self.console.print("[yellow]Execute phase skipped[/yellow]")
            return False

    def run_synthesize_phase(self) -> bool:
        """Synthesize findings into final report.

        Returns:
            True if synthesis approved, False otherwise
        """
        self.console.print("\n[bold cyan]═══ PHASE 4: SYNTHESIS ═══[/bold cyan]\n")

        # Call bash script to set up synthesis structure
        synthesize_script = self.researchkit_dir / "scripts" / "bash" / "synthesize.sh"

        if synthesize_script.exists():
            try:
                subprocess.run(
                    [str(synthesize_script)],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True,
                    timeout=30
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.console.print(f"[yellow]⚠ Synthesize script warning: {e}[/yellow]")

        # Get research directory
        research_dir = self._get_current_research_dir()
        if not research_dir:
            self.console.print("[red]No active research project found[/red]")
            return False

        # Load all documents
        plan_text = self._load_file(research_dir / "plan.md")
        findings_text = self._load_file(research_dir / "findings.md")
        sources_text = self._load_file(research_dir / "sources.md")
        constitution_text = self._load_file(self.researchkit_dir / "memory" / "constitution.md")

        # Set up conversation
        self.conversation.clear_history()
        system_prompt = synthesize.get_synthesize_system_prompt(
            plan_text, findings_text, sources_text, constitution_text
        )
        user_prompt = synthesize.get_synthesize_user_prompt()

        self.conversation.add_system_message(system_prompt)
        self.conversation.add_user_message(user_prompt)

        # Generate synthesis
        self.console.print("📊 Synthesizing research...\n")
        synthesis_text = self.conversation.generate_response(use_tools=False)

        # Approval loop
        final_synthesis, approved = self.conversation.approval_loop(
            synthesis_text,
            prompt="Approve synthesis? [y]es / [e]dit / [f]eedback"
        )

        if approved:
            # Save synthesis
            synthesis_path = research_dir / "synthesis.md"
            with open(synthesis_path, 'w', encoding='utf-8') as f:
                f.write(final_synthesis)

            self.console.print(f"✓ Saved synthesis to {synthesis_path}")

            # Copy to root with descriptive name
            from datetime import datetime
            topic_slug = research_dir.name.split('-', 1)[-1] if '-' in research_dir.name else "research"
            date_str = datetime.now().strftime("%Y-%m-%d")
            root_filename = f"{topic_slug}-synthesis-{date_str}.md"
            root_path = self.project_dir / root_filename

            import shutil
            shutil.copy2(synthesis_path, root_path)
            self.console.print(f"✓ Copied synthesis to {root_path}")

            # Git commit
            try:
                subprocess.run(
                    ["git", "add", str(research_dir), str(root_path)],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "docs: Complete research synthesis"],
                    cwd=self.project_dir,
                    check=True,
                    capture_output=True
                )
                self.console.print("✓ Committed to git")
            except subprocess.CalledProcessError:
                self.console.print("[yellow]⚠ Failed to commit to git[/yellow]")

            self.console.print(f"\n[bold green]✅ Research complete![/bold green]")
            self.console.print(f"[cyan]Final report: {root_filename}[/cyan]\n")

            return True
        else:
            self.console.print("[yellow]Synthesis phase skipped[/yellow]")
            return False

    def run_full_workflow(self, topic: str) -> None:
        """Run complete workflow: constitution → plan → execute → synthesize.

        Args:
            topic: Research topic
        """
        # Constitution
        self.run_constitution_phase()

        # Plan
        if not self.run_plan_phase(topic):
            self.console.print("[red]Planning failed. Aborting workflow.[/red]")
            return

        # Execute
        if not self.run_execute_phase():
            self.console.print("[red]Execution failed. Aborting workflow.[/red]")
            return

        # Synthesize
        self.run_synthesize_phase()

    def _load_file(self, path: Path) -> str:
        """Load file content or return empty string.

        Args:
            path: File path

        Returns:
            File content or empty string if file doesn't exist
        """
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def _get_current_research_dir(self) -> Optional[Path]:
        """Get the current research directory.

        Returns:
            Path to current research directory, or None if not found
        """
        research_root = self.researchkit_dir / "research"

        if not research_root.exists():
            return None

        # Find the most recently created research directory
        research_dirs = sorted(
            [d for d in research_root.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        return research_dirs[0] if research_dirs else None

    def _update_sources(self, research_dir: Path) -> None:
        """Update sources.md with URLs from tool calls.

        Args:
            research_dir: Research directory path
        """
        sources_path = research_dir / "sources.md"

        # Extract URLs from conversation history
        urls = set()
        for message in self.conversation.messages:
            if message.get('role') == 'tool':
                import json
                try:
                    result = json.loads(message.get('content', '{}'))
                    if 'url' in result:
                        urls.add(result['url'])
                    if 'results' in result:
                        for r in result['results']:
                            if 'url' in r:
                                urls.add(r['url'])
                except json.JSONDecodeError:
                    pass

        if urls:
            with open(sources_path, 'a', encoding='utf-8') as f:
                f.write("\n\n## Sources from Research\n\n")
                for url in sorted(urls):
                    f.write(f"- {url}\n")

            self.console.print(f"✓ Updated {len(urls)} sources in sources.md")
