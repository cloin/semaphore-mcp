"""
Project user tools for Semaphore MCP.

This module provides tools for managing users linked to SemaphoreUI projects.
"""

import logging
from typing import Any

from .base import BaseTool

logger = logging.getLogger(__name__)

PROJECT_USER_ROLES = {"owner", "manager", "task_runner", "guest"}
PROJECT_USER_SORT_FIELDS = {"name", "username", "email", "role"}
SORT_ORDERS = {"asc", "desc"}


class ProjectUserTools(BaseTool):
    """Tools for managing users linked to Semaphore projects."""

    def _validate_role(self, role: str) -> None:
        if role not in PROJECT_USER_ROLES:
            allowed = ", ".join(sorted(PROJECT_USER_ROLES))
            raise ValueError(f"role must be one of: {allowed}")

    def _validate_list_options(self, sort: str, order: str) -> None:
        if sort not in PROJECT_USER_SORT_FIELDS:
            allowed = ", ".join(sorted(PROJECT_USER_SORT_FIELDS))
            raise ValueError(f"sort must be one of: {allowed}")
        if order not in SORT_ORDERS:
            allowed = ", ".join(sorted(SORT_ORDERS))
            raise ValueError(f"order must be one of: {allowed}")

    async def get_project_role(self, project_id: int) -> dict[str, Any]:
        """Get the current user's role and permissions for a project.

        Args:
            project_id: ID of the project

        Returns:
            Role and permissions for the current user
        """
        try:
            return self.semaphore.get_project_role(project_id)
        except Exception as e:
            self.handle_error(e, f"getting current role for project {project_id}")

    async def list_project_users(
        self,
        project_id: int,
        sort: str = "name",
        order: str = "asc",
    ) -> dict[str, Any]:
        """List users linked to a project.

        Args:
            project_id: ID of the project
            sort: Field to sort by: name, username, email, or role
            order: Sort order: asc or desc

        Returns:
            Dictionary containing the list of project users
        """
        try:
            self._validate_list_options(sort, order)
            users = self.semaphore.list_project_users(project_id, sort, order)
            return {"users": users}
        except Exception as e:
            self.handle_error(e, f"listing users for project {project_id}")

    async def add_project_user(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> dict[str, Any]:
        """Link a user to a project with a role.

        Args:
            project_id: ID of the project
            user_id: ID of the user to link
            role: Project role: owner, manager, task_runner, or guest

        Returns:
            Empty dict on success
        """
        try:
            self._validate_role(role)
            return self.semaphore.add_project_user(project_id, user_id, role)
        except Exception as e:
            self.handle_error(e, f"adding user {user_id} to project {project_id}")

    async def update_project_user(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> dict[str, Any]:
        """Update a linked user's project role.

        Args:
            project_id: ID of the project
            user_id: ID of the linked user
            role: Project role: owner, manager, task_runner, or guest

        Returns:
            Empty dict on success
        """
        try:
            self._validate_role(role)
            return self.semaphore.update_project_user(project_id, user_id, role)
        except Exception as e:
            self.handle_error(
                e, f"updating user {user_id} role for project {project_id}"
            )

    async def remove_project_user(
        self,
        project_id: int,
        user_id: int,
    ) -> dict[str, Any]:
        """Remove a user from a project.

        Args:
            project_id: ID of the project
            user_id: ID of the user to remove

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.remove_project_user(project_id, user_id)
        except Exception as e:
            self.handle_error(e, f"removing user {user_id} from project {project_id}")
