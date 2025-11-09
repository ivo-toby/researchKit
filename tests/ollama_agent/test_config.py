"""Tests for Ollama config management."""

import json
import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from ollama_agent.config import OllamaConfig, ConfigManager


class TestOllamaConfig:
    """Test OllamaConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = OllamaConfig()
        assert config.version == "1.0"
        assert config.ollama_url == "http://localhost:11434"
        assert config.model == ""
        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.num_ctx == 4096

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = OllamaConfig(
            model="llama3.2",
            temperature=0.5,
            num_ctx=8192
        )
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["model"] == "llama3.2"
        assert data["temperature"] == 0.5
        assert data["num_ctx"] == 8192

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "version": "1.0",
            "ollama_url": "http://localhost:11434",
            "model": "llama3.2",
            "temperature": 0.5,
            "top_p": 0.9,
            "num_ctx": 8192,
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00"
        }
        config = OllamaConfig.from_dict(data)

        assert config.model == "llama3.2"
        assert config.temperature == 0.5
        assert config.num_ctx == 8192

    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        config = OllamaConfig(
            model="llama3.2",
            ollama_url="http://localhost:11434",
            temperature=0.7,
            top_p=0.9,
            num_ctx=4096
        )
        is_valid, error = config.validate()

        assert is_valid is True
        assert error is None

    def test_validate_missing_model(self):
        """Test validation with missing model."""
        config = OllamaConfig(model="")
        is_valid, error = config.validate()

        assert is_valid is False
        assert "Model name is required" in error

    def test_validate_missing_url(self):
        """Test validation with missing URL."""
        config = OllamaConfig(model="llama3.2", ollama_url="")
        is_valid, error = config.validate()

        assert is_valid is False
        assert "Ollama URL is required" in error

    def test_validate_invalid_url_scheme(self):
        """Test validation with invalid URL scheme."""
        config = OllamaConfig(model="llama3.2", ollama_url="ftp://localhost:11434")
        is_valid, error = config.validate()

        assert is_valid is False
        assert "must start with http://" in error

    def test_validate_temperature_out_of_range(self):
        """Test validation with temperature out of range."""
        config = OllamaConfig(model="llama3.2", temperature=3.0)
        is_valid, error = config.validate()

        assert is_valid is False
        assert "Temperature must be between" in error

    def test_validate_top_p_out_of_range(self):
        """Test validation with top_p out of range."""
        config = OllamaConfig(model="llama3.2", top_p=1.5)
        is_valid, error = config.validate()

        assert is_valid is False
        assert "top_p must be between" in error

    def test_validate_num_ctx_too_small(self):
        """Test validation with num_ctx too small."""
        config = OllamaConfig(model="llama3.2", num_ctx=256)
        is_valid, error = config.validate()

        assert is_valid is False
        assert "num_ctx must be at least 512" in error


class TestConfigManager:
    """Test ConfigManager class."""

    def test_exists_no_file(self):
        """Test exists() when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            assert manager.exists() is False

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Create and save config
            config = OllamaConfig(
                model="llama3.2",
                temperature=0.5,
                num_ctx=8192
            )
            result = manager.save(config)
            assert result is True
            assert manager.exists() is True

            # Load config
            loaded_config = manager.load()
            assert loaded_config is not None
            assert loaded_config.model == "llama3.2"
            assert loaded_config.temperature == 0.5
            assert loaded_config.num_ctx == 8192

    def test_save_invalid_config(self):
        """Test saving invalid configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Create invalid config (no model)
            config = OllamaConfig(model="")
            result = manager.save(config)

            assert result is False
            assert manager.exists() is False

    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Create config file with invalid JSON
            manager.config_path.parent.mkdir(parents=True, exist_ok=True)
            manager.config_path.write_text("{ invalid json }")

            loaded_config = manager.load()
            assert loaded_config is None

    def test_load_invalid_config_data(self):
        """Test loading config with invalid data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Create config file with invalid values
            manager.config_path.parent.mkdir(parents=True, exist_ok=True)
            invalid_data = {
                "version": "1.0",
                "ollama_url": "http://localhost:11434",
                "model": "",  # Invalid: empty model
                "temperature": 0.7,
                "top_p": 0.9,
                "num_ctx": 4096,
                "created_at": "",
                "updated_at": ""
            }
            manager.config_path.write_text(json.dumps(invalid_data))

            loaded_config = manager.load()
            assert loaded_config is None

    def test_delete(self):
        """Test deleting configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Create config
            config = OllamaConfig(model="llama3.2")
            manager.save(config)
            assert manager.exists() is True

            # Delete config
            result = manager.delete()
            assert result is True
            assert manager.exists() is False

    def test_delete_nonexistent(self):
        """Test deleting nonexistent config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            result = manager.delete()
            assert result is True

    def test_updated_at_timestamp(self):
        """Test that updated_at timestamp is set on save."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            config = OllamaConfig(model="llama3.2")
            manager.save(config)

            loaded_config = manager.load()
            assert loaded_config.updated_at != ""

            # Parse timestamp to verify it's valid
            datetime.fromisoformat(loaded_config.updated_at)
