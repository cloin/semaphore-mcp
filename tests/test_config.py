"""
Tests for the configuration module.
"""

import logging
import os
from unittest.mock import patch

import pytest

from semaphore_mcp.config import (
    DEFAULT_CONFIG,
    configure_logging,
    get_config,
    get_log_level,
)


class TestConfig:
    """Test suite for configuration functionality."""

    def test_get_config_with_default(self):
        """Test getting config with default values."""
        # Test with a custom default for non-existent key
        result = get_config("NON_EXISTENT_KEY", "custom_default")
        assert result == "custom_default"

        # Test with no default provided for non-existent key
        result = get_config("NON_EXISTENT_KEY")
        assert result == ""

        # Test that actual config values can be retrieved
        # (we don't test against DEFAULT_CONFIG directly since env vars may override)
        result = get_config("SEMAPHORE_URL")
        assert result  # Should not be empty
        assert result.startswith("http")

    @patch.dict(os.environ, {"TEST_CONFIG_KEY": "test_value"})
    def test_get_config_from_environment(self):
        """Test getting config from environment variables."""
        result = get_config("TEST_CONFIG_KEY")
        assert result == "test_value"

        # Environment should override default
        result = get_config("TEST_CONFIG_KEY", "default_value")
        assert result == "test_value"

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "DEBUG"})
    def test_get_log_level_debug(self):
        """Test getting DEBUG log level."""
        result = get_log_level()
        assert result == logging.DEBUG

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "WARNING"})
    def test_get_log_level_warning(self):
        """Test getting WARNING log level."""
        result = get_log_level()
        assert result == logging.WARNING

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "ERROR"})
    def test_get_log_level_error(self):
        """Test getting ERROR log level."""
        result = get_log_level()
        assert result == logging.ERROR

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "CRITICAL"})
    def test_get_log_level_critical(self):
        """Test getting CRITICAL log level."""
        result = get_log_level()
        assert result == logging.CRITICAL

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "invalid_level"})
    def test_get_log_level_invalid(self):
        """Test getting log level with invalid value defaults to INFO."""
        result = get_log_level()
        assert result == logging.INFO

    def test_get_log_level_default(self):
        """Test getting log level with no environment variable defaults to INFO."""
        # Ensure the environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            with patch("semaphore_mcp.config.get_config", return_value="INFO"):
                result = get_log_level()
                assert result == logging.INFO

    @patch.dict(os.environ, {"MCP_LOG_LEVEL": "debug"})
    def test_get_log_level_case_insensitive(self):
        """Test that log level is case insensitive."""
        result = get_log_level()
        assert result == logging.DEBUG

    def test_configure_logging(self):
        """Test logging configuration."""
        # This is a basic test to ensure the function runs without error
        # More comprehensive testing would require checking actual logger configuration
        try:
            configure_logging()
            # If we get here without exception, the function worked
            assert True
        except Exception as e:
            pytest.fail(f"configure_logging() raised an exception: {e}")

    def test_default_config_values(self):
        """Test that default configuration values are properly defined."""
        assert "SEMAPHORE_URL" in DEFAULT_CONFIG
        assert "SEMAPHORE_API_TOKEN" in DEFAULT_CONFIG
        assert "MCP_LOG_LEVEL" in DEFAULT_CONFIG

        assert DEFAULT_CONFIG["SEMAPHORE_URL"] == "http://localhost:3000"
        assert DEFAULT_CONFIG["SEMAPHORE_API_TOKEN"] == ""
        assert DEFAULT_CONFIG["MCP_LOG_LEVEL"] == "INFO"

    @patch.dict(os.environ, {"SEMAPHORE_URL": "http://test.example.com:8080"})
    def test_config_environment_override(self):
        """Test that environment variables override defaults."""
        result = get_config("SEMAPHORE_URL")
        assert result == "http://test.example.com:8080"
        assert result != DEFAULT_CONFIG["SEMAPHORE_URL"]

    def test_config_empty_string_handling(self):
        """Test handling of empty string values."""
        # Test with explicit empty string default for non-existent key
        result = get_config("NON_EXISTENT", "")
        assert result == ""

        # Test that we can retrieve token (might be set in environment)
        result = get_config("SEMAPHORE_API_TOKEN")
        # Don't assert on specific value since it might be set in env
        assert isinstance(result, str)
