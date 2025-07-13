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
            templates = self.semaphore.list_templates(project_id)
            return {"templates": templates}
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
            # If individual template fetch fails, try to find it in the template list
            if "404" in str(e):
                try:
                    templates = self.semaphore.list_templates(project_id)
                    if isinstance(templates, list):
                        matching_template = next(
                            (
                                template
                                for template in templates
                                if template.get("id") == template_id
                            ),
                            None,
                        )
                        if matching_template:
                            return {
                                "template": matching_template,
                                "note": "Template found in list but individual endpoint unavailable",
                            }
                    self.handle_error(
                        e,
                        f"getting template {template_id}. Template may have been deleted or ID format may be incorrect",
                    )
                except Exception:
                    pass
            self.handle_error(e, f"getting template {template_id}")
