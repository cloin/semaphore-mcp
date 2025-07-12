"""
Configuration module for SemaphoreMCP.

Handles environment variable loading and configuration management.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default configuration values
DEFAULT_CONFIG = {
    "SEMAPHORE_URL": "http://localhost:3000",
    "SEMAPHORE_API_TOKEN": "",
    "MCP_LOG_LEVEL": "INFO",
}


def get_config(key: str, default: Optional[str] = None) -> str:
    """
    Get a configuration value from environment variables.

    Args:
        key: Configuration key
        default: Default value if not found in environment

    Returns:
        Configuration value
    """
    return os.environ.get(key, default or DEFAULT_CONFIG.get(key, ""))


def get_log_level() -> int:
    """
    Get the configured log level.

    Returns:
        Log level as a logging module constant
    """
    level_name = get_config("MCP_LOG_LEVEL", "INFO").upper()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_name, logging.INFO)


def configure_logging() -> None:
    """Configure logging based on environment variables."""
    logging.basicConfig(
        level=get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
