"""
Base tool class for Semaphore MCP tools.

This module provides the base class for all Semaphore tool implementations,
handling common functionality like client initialization and error handling.
"""

import logging
from typing import NoReturn

logger = logging.getLogger(__name__)


class BaseTool:
    """Base class for all Semaphore MCP tools."""

    def __init__(self, semaphore_client):
        """Initialize the base tool with a Semaphore client.

        Args:
            semaphore_client: An initialized Semaphore API client
        """
        self.semaphore = semaphore_client

    def handle_error(self, error: Exception, operation: str) -> NoReturn:
        """Common error handling for tool operations.

        Args:
            error: The exception that was raised
            operation: Description of the operation being performed

        Raises:
            RuntimeError: With formatted error message
        """
        error_msg = f"Error during {operation}: {str(error)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
