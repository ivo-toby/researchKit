"""Configuration management for Ollama agent."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


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

    def to_dict(self) -> dict:
        """Convert config to dictionary for JSON serialization.

        Returns:
            Dictionary representation of config
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OllamaConfig":
        """Create config from dictionary.

        Args:
            data: Dictionary with config data

        Returns:
            OllamaConfig instance
        """
        return cls(**data)

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration values.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.model:
            return False, "Model name is required"

        if not self.ollama_url:
            return False, "Ollama URL is required"

        if not self.ollama_url.startswith(("http://", "https://")):
            return False, "Ollama URL must start with http:// or https://"

        if self.temperature < 0.0 or self.temperature > 2.0:
            return False, "Temperature must be between 0.0 and 2.0"

        if self.top_p < 0.0 or self.top_p > 1.0:
            return False, "top_p must be between 0.0 and 1.0"

        if self.num_ctx < 512:
            return False, "num_ctx must be at least 512"

        return True, None


class ConfigManager:
    """Manages Ollama configuration persistence."""

    CONFIG_PATH = Path(".researchkit/config/ollama.json")

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize config manager.

        Args:
            project_dir: Project directory path. Defaults to current working directory.
        """
        self.project_dir = project_dir or Path.cwd()
        self.config_path = self.project_dir / self.CONFIG_PATH

    def exists(self) -> bool:
        """Check if config file exists.

        Returns:
            True if config file exists, False otherwise
        """
        return self.config_path.exists()

    def load(self) -> Optional[OllamaConfig]:
        """Load config from file.

        Returns:
            OllamaConfig instance if file exists and is valid, None otherwise
        """
        if not self.exists():
            return None

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            config = OllamaConfig.from_dict(data)

            # Validate loaded config
            is_valid, error = config.validate()
            if not is_valid:
                print(f"⚠️  Warning: Invalid config: {error}")
                return None

            return config

        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Failed to parse config file: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Warning: Failed to load config: {e}")
            return None

    def save(self, config: OllamaConfig) -> bool:
        """Save config to file.

        Args:
            config: OllamaConfig instance to save

        Returns:
            True if save was successful, False otherwise
        """
        # Validate before saving
        is_valid, error = config.validate()
        if not is_valid:
            print(f"❌ Cannot save invalid config: {error}")
            return False

        # Update timestamp
        config.updated_at = datetime.now().isoformat()

        try:
            # Create parent directories if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write config with pretty formatting
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            return True

        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False

    def delete(self) -> bool:
        """Delete config file.

        Returns:
            True if deletion was successful or file didn't exist, False on error
        """
        if not self.exists():
            return True

        try:
            self.config_path.unlink()
            return True
        except Exception as e:
            print(f"❌ Failed to delete config: {e}")
            return False
