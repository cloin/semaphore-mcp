"""
Project-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore projects.
"""

import logging
from typing import Any, Dict

from .base import BaseTool

logger = logging.getLogger(__name__)


class ProjectTools(BaseTool):
    """Tools for working with Semaphore projects."""

    async def list_projects(self) -> Dict[str, Any]:
        """List all projects in SemaphoreUI.

        Returns:
            A dictionary containing the list of projects.
        """
        try:
            projects = self.semaphore.list_projects()
            return {"projects": projects}
        except Exception as e:
            self.handle_error(e, "listing projects")

    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get details of a specific project.

        Args:
            project_id: ID of the project to fetch

        Returns:
            Project details
        """
        try:
            return self.semaphore.get_project(project_id)
        except Exception as e:
            self.handle_error(e, f"getting project {project_id}")
