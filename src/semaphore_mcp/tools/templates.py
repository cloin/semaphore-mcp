"""
Template-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore templates.
These tools support full CRUD operations for templates.
"""

import logging
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class TemplateTools(BaseTool):
    """Tools for working with Semaphore templates.

    Provides full CRUD operations for templates in SemaphoreUI projects.
    All operations have been tested and verified to work with SemaphoreUI API.
    """

    async def list_templates(self, project_id: int) -> dict[str, Any]:
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

    async def get_template(self, project_id: int, template_id: int) -> dict[str, Any]:
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

    async def create_template(
        self,
        project_id: int,
        name: str,
        playbook: str,
        inventory_id: int,
        repository_id: int,
        environment_id: int,
        description: Optional[str] = None,
        arguments: Optional[str] = None,
        allow_override_args_in_task: bool = False,
        suppress_success_alerts: bool = False,
        app: str = "ansible",
        git_branch: Optional[str] = None,
        survey_vars: Optional[list[dict[str, Any]]] = None,
        vaults: Optional[list[dict[str, Any]]] = None,
        template_type: Optional[str] = None,
        start_version: Optional[str] = None,
        build_template_id: Optional[int] = None,
        autorun: bool = False,
        view_id: Optional[int] = None,
        task_params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a new template.

        Args:
            project_id: ID of the project
            name: Template name
            playbook: Playbook file path (e.g., "playbook.yml")
            inventory_id: Inventory ID
            repository_id: Repository ID
            environment_id: Environment ID
            description: Template description (optional)
            arguments: Extra arguments as JSON string (optional)
            allow_override_args_in_task: Allow overriding arguments in task (default: False)
            suppress_success_alerts: Suppress success alerts (default: False)
            app: Application type (default: "ansible")
            git_branch: Git branch to use (optional)
            survey_vars: Survey variables for prompting (optional)
            vaults: Vault configurations (optional)
            template_type: Template type - "", "build", or "deploy" (optional)
            start_version: Start version (optional)
            build_template_id: Build template ID for deploy templates (optional)
            autorun: Enable autorun (default: False)
            view_id: View ID (optional)
            task_params: App-specific task parameters (optional). For Ansible templates:
                - allow_override_limit: Allow task-level --limit override (required for run_task limit)
                - allow_override_inventory: Allow task-level inventory override
                - allow_override_tags: Allow task-level --tags override
                - allow_override_skip_tags: Allow task-level --skip-tags override
                - limit: Default limit (list of hosts/groups)
                - tags: Default tags (list)
                - skip_tags: Default skip tags (list)

        Returns:
            Created template details
        """
        try:
            return self.semaphore.create_template(
                project_id=project_id,
                name=name,
                playbook=playbook,
                inventory_id=inventory_id,
                repository_id=repository_id,
                environment_id=environment_id,
                description=description,
                arguments=arguments,
                allow_override_args_in_task=allow_override_args_in_task,
                suppress_success_alerts=suppress_success_alerts,
                app=app,
                git_branch=git_branch,
                survey_vars=survey_vars,
                vaults=vaults,
                template_type=template_type,
                start_version=start_version,
                build_template_id=build_template_id,
                autorun=autorun,
                view_id=view_id,
                task_params=task_params,
            )
        except Exception as e:
            self.handle_error(e, f"creating template '{name}' in project {project_id}")

    async def update_template(
        self,
        project_id: int,
        template_id: int,
        name: Optional[str] = None,
        playbook: Optional[str] = None,
        inventory_id: Optional[int] = None,
        repository_id: Optional[int] = None,
        environment_id: Optional[int] = None,
        description: Optional[str] = None,
        arguments: Optional[str] = None,
        allow_override_args_in_task: Optional[bool] = None,
        suppress_success_alerts: Optional[bool] = None,
        app: Optional[str] = None,
        git_branch: Optional[str] = None,
        survey_vars: Optional[list[dict[str, Any]]] = None,
        vaults: Optional[list[dict[str, Any]]] = None,
        template_type: Optional[str] = None,
        start_version: Optional[str] = None,
        build_template_id: Optional[int] = None,
        autorun: Optional[bool] = None,
        view_id: Optional[int] = None,
        task_params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Update an existing template.

        Args:
            project_id: ID of the project
            template_id: ID of the template to update
            name: Template name (optional)
            playbook: Playbook file path (optional)
            inventory_id: Inventory ID (optional)
            repository_id: Repository ID (optional)
            environment_id: Environment ID (optional)
            description: Template description (optional)
            arguments: Extra arguments (optional)
            allow_override_args_in_task: Allow overriding arguments (optional)
            suppress_success_alerts: Suppress success alerts (optional)
            app: Application type (optional)
            git_branch: Git branch (optional)
            survey_vars: Survey variables (optional)
            vaults: Vault configurations (optional)
            template_type: Template type (optional)
            start_version: Start version (optional)
            build_template_id: Build template ID (optional)
            autorun: Enable autorun (optional)
            view_id: View ID (optional)
            task_params: App-specific task parameters (optional). For Ansible templates:
                - allow_override_limit: Allow task-level --limit override (required for run_task limit)
                - allow_override_inventory: Allow task-level inventory override
                - allow_override_tags: Allow task-level --tags override
                - allow_override_skip_tags: Allow task-level --skip-tags override
                - limit: Default limit (list of hosts/groups)
                - tags: Default tags (list)
                - skip_tags: Default skip tags (list)

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.update_template(
                project_id=project_id,
                template_id=template_id,
                name=name,
                playbook=playbook,
                inventory_id=inventory_id,
                repository_id=repository_id,
                environment_id=environment_id,
                description=description,
                arguments=arguments,
                allow_override_args_in_task=allow_override_args_in_task,
                suppress_success_alerts=suppress_success_alerts,
                app=app,
                git_branch=git_branch,
                survey_vars=survey_vars,
                vaults=vaults,
                template_type=template_type,
                start_version=start_version,
                build_template_id=build_template_id,
                autorun=autorun,
                view_id=view_id,
                task_params=task_params,
            )
        except Exception as e:
            self.handle_error(e, f"updating template {template_id}")

    async def delete_template(
        self, project_id: int, template_id: int
    ) -> dict[str, Any]:
        """Delete a template.

        Args:
            project_id: ID of the project
            template_id: ID of the template to delete

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.delete_template(project_id, template_id)
        except Exception as e:
            self.handle_error(e, f"deleting template {template_id}")

    async def stop_all_template_tasks(
        self, project_id: int, template_id: int
    ) -> dict[str, Any]:
        """Stop all running tasks for a template.

        Args:
            project_id: ID of the project
            template_id: ID of the template

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.stop_all_template_tasks(project_id, template_id)
        except Exception as e:
            self.handle_error(e, f"stopping all tasks for template {template_id}")
