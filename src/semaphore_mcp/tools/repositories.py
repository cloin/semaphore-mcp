"""
Repository-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore repositories.
These tools support full CRUD operations for repositories.
"""

import logging
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class RepositoryTools(BaseTool):
    """Tools for working with Semaphore repositories.

    Provides full CRUD operations for repositories in SemaphoreUI projects.
    All operations have been tested and verified to work with SemaphoreUI API.
    """

    async def list_repositories(self, project_id: int) -> dict[str, Any]:
        """List all repositories for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of repositories for the project
        """
        try:
            repositories = self.semaphore.list_repositories(project_id)
            return {"repositories": repositories}
        except Exception as e:
            self.handle_error(e, f"listing repositories for project {project_id}")

    async def get_repository(
        self, project_id: int, repository_id: int
    ) -> dict[str, Any]:
        """Get details of a specific repository.

        Args:
            project_id: ID of the project
            repository_id: ID of the repository to fetch

        Returns:
            Repository details
        """
        try:
            return self.semaphore.get_repository(project_id, repository_id)
        except Exception as e:
            self.handle_error(e, f"getting repository {repository_id}")

    async def create_repository(
        self,
        project_id: int,
        name: str,
        git_url: str,
        git_branch: str,
        ssh_key_id: int,
    ) -> dict[str, Any]:
        """Create a new repository.

        Args:
            project_id: ID of the project
            name: Repository name
            git_url: Git repository URL
            git_branch: Git branch to use
            ssh_key_id: SSH key ID for authentication

        Returns:
            Created repository details
        """
        try:
            return self.semaphore.create_repository(
                project_id, name, git_url, git_branch, ssh_key_id
            )
        except Exception as e:
            self.handle_error(
                e, f"creating repository '{name}' in project {project_id}"
            )

    async def update_repository(
        self,
        project_id: int,
        repository_id: int,
        name: Optional[str] = None,
        git_url: Optional[str] = None,
        git_branch: Optional[str] = None,
        ssh_key_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update an existing repository.

        Args:
            project_id: ID of the project
            repository_id: ID of the repository to update
            name: Repository name (optional)
            git_url: Git repository URL (optional)
            git_branch: Git branch to use (optional)
            ssh_key_id: SSH key ID for authentication (optional)

        Returns:
            Updated repository details
        """
        try:
            return self.semaphore.update_repository(
                project_id, repository_id, name, git_url, git_branch, ssh_key_id
            )
        except Exception as e:
            self.handle_error(e, f"updating repository {repository_id}")

    async def delete_repository(
        self, project_id: int, repository_id: int
    ) -> dict[str, Any]:
        """Delete a repository.

        Args:
            project_id: ID of the project
            repository_id: ID of the repository to delete

        Returns:
            Deletion result
        """
        try:
            return self.semaphore.delete_repository(project_id, repository_id)
        except Exception as e:
            self.handle_error(e, f"deleting repository {repository_id}")
