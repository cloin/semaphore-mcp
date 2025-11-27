"""
Project-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore projects.
These tools support full CRUD operations for projects.
"""

import logging
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class ProjectTools(BaseTool):
    """Tools for working with Semaphore projects.

    Provides full CRUD operations for projects in SemaphoreUI.
    All operations have been tested and verified to work with SemaphoreUI API.
    """

    async def list_projects(self) -> dict[str, Any]:
        """List all projects in SemaphoreUI.

        Returns:
            A dictionary containing the list of projects.
        """
        try:
            projects = self.semaphore.list_projects()
            return {"projects": projects}
        except Exception as e:
            self.handle_error(e, "listing projects")

    async def get_project(self, project_id: int) -> dict[str, Any]:
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

    async def create_project(
        self,
        name: str,
        alert: bool = False,
        alert_chat: Optional[str] = None,
        max_parallel_tasks: int = 0,
        project_type: Optional[str] = None,
        demo: bool = False,
    ) -> dict[str, Any]:
        """Create a new project.

        Args:
            name: Project name
            alert: Enable alerts (default: False)
            alert_chat: Chat channel for alerts (optional)
            max_parallel_tasks: Maximum parallel tasks, 0 = unlimited (default: 0)
            project_type: Project type (optional)
            demo: Create demo resources (default: False)

        Returns:
            Created project details
        """
        try:
            return self.semaphore.create_project(
                name=name,
                alert=alert,
                alert_chat=alert_chat,
                max_parallel_tasks=max_parallel_tasks,
                project_type=project_type,
                demo=demo,
            )
        except Exception as e:
            self.handle_error(e, f"creating project '{name}'")

    async def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        alert: Optional[bool] = None,
        alert_chat: Optional[str] = None,
        max_parallel_tasks: Optional[int] = None,
        project_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing project.

        Args:
            project_id: ID of the project to update
            name: Project name (optional)
            alert: Enable alerts (optional)
            alert_chat: Chat channel for alerts (optional)
            max_parallel_tasks: Maximum parallel tasks (optional)
            project_type: Project type (optional)

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.update_project(
                project_id=project_id,
                name=name,
                alert=alert,
                alert_chat=alert_chat,
                max_parallel_tasks=max_parallel_tasks,
                project_type=project_type,
            )
        except Exception as e:
            self.handle_error(e, f"updating project {project_id}")

    async def delete_project(self, project_id: int) -> dict[str, Any]:
        """Delete a project.

        Args:
            project_id: ID of the project to delete

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.delete_project(project_id)
        except Exception as e:
            self.handle_error(e, f"deleting project {project_id}")
