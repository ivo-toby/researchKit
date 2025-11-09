"""Environment checking and initialization for Ollama agent."""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import requests


class EnvironmentManager:
    """Checks and initializes the research environment."""

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize environment manager.

        Args:
            project_dir: Project directory path. Defaults to current working directory.
        """
        self.project_dir = project_dir or Path.cwd()

    def check_ollama(self, url: str = "http://localhost:11434") -> bool:
        """Check if Ollama is running and accessible.

        Args:
            url: Ollama API URL

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False

    def check_git(self) -> bool:
        """Check if git is installed and repo is initialized.

        Returns:
            True if git is installed and current directory is a git repo
        """
        # Check if git is installed
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

        # Check if current directory is a git repo
        git_dir = self.project_dir / ".git"
        return git_dir.exists()

    def prompt_git_init(self) -> bool:
        """Ask user to initialize git repo.

        Returns:
            True if git was initialized successfully, False otherwise
        """
        print("\n⚠️  No git repository found in the current directory.")
        response = input("Initialize git repository? [y/N]: ").strip().lower()

        if response not in ['y', 'yes']:
            print("\n❌ ResearchKit requires git to function. Exiting.")
            return False

        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.project_dir,
                check=True,
                capture_output=True,
                timeout=10
            )
            print("✓ Initialized git repository")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize git: {e}")
            return False
        except FileNotFoundError:
            print("❌ Git not found - please install git")
            return False
        except subprocess.TimeoutExpired:
            print("❌ Git init timed out")
            return False

    def check_researchkit_initialized(self) -> bool:
        """Check if .researchkit/ structure exists.

        Returns:
            True if .researchkit directory exists with required subdirectories
        """
        researchkit_dir = self.project_dir / ".researchkit"

        if not researchkit_dir.exists():
            return False

        # Check for required subdirectories
        required_dirs = [
            researchkit_dir / "memory",
            researchkit_dir / "scripts" / "bash",
            researchkit_dir / "templates",
        ]

        return all(d.exists() for d in required_dirs)

    def initialize_researchkit(self) -> bool:
        """Create .researchkit/ folder structure.

        This method reuses the existing researchKit templates and scripts
        to maintain compatibility with the existing workflow.

        Returns:
            True if initialization successful, False otherwise
        """
        import shutil

        researchkit_dir = self.project_dir / ".researchkit"

        # Create main directories
        directories = [
            researchkit_dir / "memory",
            researchkit_dir / "scripts" / "bash",
            researchkit_dir / "scripts" / "powershell",
            researchkit_dir / "research",
            researchkit_dir / "templates",
            researchkit_dir / "config",  # For ollama.json
        ]

        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            print("✓ Created .researchkit directory structure")

            # Find template directory
            template_dir = self._get_template_dir()

            if template_dir and template_dir.exists():
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

                if copied_count > 0:
                    print(f"✓ Copied {copied_count} template files")

                # Copy scripts
                scripts_dir = template_dir.parent / "scripts"
                if scripts_dir.exists():
                    bash_scripts = scripts_dir / "bash"
                    if bash_scripts.exists():
                        for script_file in bash_scripts.glob("*.sh"):
                            dst = researchkit_dir / "scripts" / "bash" / script_file.name
                            shutil.copy2(script_file, dst)
                            # Make scripts executable
                            dst.chmod(0o755)

                        print("✓ Copied bash scripts")

            # Create initial constitution
            constitution_path = researchkit_dir / "memory" / "constitution.md"
            if not constitution_path.exists():
                constitution_template = researchkit_dir / "templates" / "constitution-template.md"
                if constitution_template.exists():
                    shutil.copy2(constitution_template, constitution_path)
                    print("✓ Created initial constitution")

            return True

        except Exception as e:
            print(f"❌ Error initializing researchKit: {e}")
            return False

    def _get_template_dir(self) -> Optional[Path]:
        """Find the template directory.

        Returns:
            Path to templates directory, or None if not found
        """
        # Try to find templates in the same way as research_cli
        # Look in package installation directory
        try:
            import site

            # Try system prefix
            template_dir = Path(sys.prefix) / "share" / "research-cli" / "templates"
            if template_dir.exists():
                return template_dir

            # Try development mode (relative to this file)
            module_dir = Path(__file__).parent.parent.parent
            template_dir = module_dir / "templates"
            if template_dir.exists():
                return template_dir

            # Try site-packages
            for site_dir in site.getsitepackages():
                template_dir = Path(site_dir) / "share" / "research-cli" / "templates"
                if template_dir.exists():
                    return template_dir

        except Exception:
            pass

        return None
