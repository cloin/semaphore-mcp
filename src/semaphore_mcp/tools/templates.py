"""
Template-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore templates.
"""

import logging
from typing import Any, Dict

from .base import BaseTool

logger = logging.getLogger(__name__)


class TemplateTools(BaseTool):
    """Tools for working with Semaphore templates."""

    async def list_templates(self, project_id: int) -> Dict[str, Any]:
        """List all templates for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of templates for the project
        """
        try:
            return self.semaphore.list_templates(project_id)
        except Exception as e:
            self.handle_error(e, f"listing templates for project {project_id}")

    async def get_template(self, project_id: int, template_id: int) -> Dict[str, Any]:
        """Get details of a specific template.

        Args:
            project_id: ID of the project
            template_id: ID of the template to fetch

        Returns:
            Template details
        """
        try:
            return self.semaphore.get_template(project_id, template_id)
        except Exception as e:
            self.handle_error(e, f"getting template {template_id}")
