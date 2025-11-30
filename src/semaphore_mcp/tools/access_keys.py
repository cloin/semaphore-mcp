"""Access key tools for Semaphore MCP.

Provides tools for managing access keys (key store) in SemaphoreUI projects.
Access keys are used for repository authentication and can be of type:
- "none": For public repositories (no credentials needed)
- "ssh": For SSH key authentication
- "login_password": For username/password authentication
"""

from typing import Any, Optional

from .base import BaseTool


class AccessKeyTools(BaseTool):
    """Tools for managing Semaphore access keys (key store)."""

    async def list_access_keys(self, project_id: int) -> dict[str, Any]:
        """List all access keys for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing list of access keys
        """
        try:
            keys = self.semaphore.list_access_keys(project_id)
            return {"access_keys": keys}
        except Exception as e:
            self.handle_error(e, f"listing access keys for project {project_id}")

    async def create_access_key(
        self,
        project_id: int,
        name: str,
        key_type: str,
        login: Optional[str] = None,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new access key.

        Args:
            project_id: ID of the project
            name: Name for the access key
            key_type: Type of key - one of:
                - "none": For public repositories (no credentials needed)
                - "ssh": For SSH key authentication
                - "login_password": For username/password authentication
            login: Username (for ssh or login_password types)
            password: Password (for login_password type)
            private_key: Private key content (for ssh type)

        Returns:
            Created access key details
        """
        try:
            return self.semaphore.create_access_key(
                project_id, name, key_type, login, password, private_key
            )
        except Exception as e:
            self.handle_error(
                e, f"creating access key '{name}' in project {project_id}"
            )
