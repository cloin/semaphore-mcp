"""
View-related tools for Semaphore MCP.

This module provides tools for managing SemaphoreUI project views.
"""

import logging
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class ViewTools(BaseTool):
    """Tools for working with Semaphore project views."""

    async def list_views(self, project_id: int) -> dict[str, Any]:
        """List all views for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing the list of views
        """
        try:
            views = self.semaphore.list_views(project_id)
            return {"views": views}
        except Exception as e:
            self.handle_error(e, f"listing views for project {project_id}")

    async def get_view(self, project_id: int, view_id: int) -> dict[str, Any]:
        """Get details of a specific view.

        Args:
            project_id: ID of the project
            view_id: ID of the view to fetch

        Returns:
            View details
        """
        try:
            return self.semaphore.get_view(project_id, view_id)
        except Exception as e:
            self.handle_error(e, f"getting view {view_id}")

    async def create_view(
        self,
        project_id: int,
        title: str,
        position: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a new view.

        Args:
            project_id: ID of the project
            title: View title
            position: View ordering position

        Returns:
            Created view details
        """
        try:
            return self.semaphore.create_view(project_id, title, position)
        except Exception as e:
            self.handle_error(e, f"creating view '{title}' in project {project_id}")

    async def update_view(
        self,
        project_id: int,
        view_id: int,
        title: Optional[str] = None,
        position: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update an existing view.

        Args:
            project_id: ID of the project
            view_id: ID of the view to update
            title: View title
            position: View ordering position

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.update_view(project_id, view_id, title, position)
        except Exception as e:
            self.handle_error(e, f"updating view {view_id}")

    async def delete_view(self, project_id: int, view_id: int) -> dict[str, Any]:
        """Delete a view.

        Args:
            project_id: ID of the project
            view_id: ID of the view to delete

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.delete_view(project_id, view_id)
        except Exception as e:
            self.handle_error(e, f"deleting view {view_id}")
