"""
Environment and inventory-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore environments and inventory.
These tools support full CRUD operations for both environments and inventory items.
"""

import logging
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class EnvironmentTools(BaseTool):
    """Tools for working with Semaphore environments and inventory.

    Provides full CRUD operations for environments and inventory items in SemaphoreUI projects.
    All operations have been tested and verified to work with SemaphoreUI API.
    """

    # Environment-related tools

    async def list_environments(self, project_id: int) -> dict[str, Any]:
        """List all environments for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of environments for the project
        """
        try:
            environments = self.semaphore.list_environments(project_id)
            return {"environments": environments}
        except Exception as e:
            self.handle_error(e, f"listing environments for project {project_id}")

    async def get_environment(
        self, project_id: int, environment_id: int
    ) -> dict[str, Any]:
        """Get details of a specific environment.

        Args:
            project_id: ID of the project
            environment_id: ID of the environment to fetch

        Returns:
            Environment details
        """
        try:
            return self.semaphore.get_environment(project_id, environment_id)
        except Exception as e:
            self.handle_error(e, f"getting environment {environment_id}")

    async def create_environment(
        self, project_id: int, name: str, env_data: dict[str, str]
    ) -> dict[str, Any]:
        """Create a new environment.

        Args:
            project_id: ID of the project
            name: Environment name
            env_data: Environment variables as key-value pairs

        Returns:
            Created environment details
        """
        try:
            return self.semaphore.create_environment(project_id, name, env_data)
        except Exception as e:
            self.handle_error(
                e, f"creating environment '{name}' in project {project_id}"
            )

    async def update_environment(
        self,
        project_id: int,
        environment_id: int,
        name: Optional[str] = None,
        env_data: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Update an existing environment.

        Args:
            project_id: ID of the project
            environment_id: ID of the environment to update
            name: Environment name (optional)
            env_data: Environment variables as key-value pairs (optional)

        Returns:
            Updated environment details
        """
        try:
            return self.semaphore.update_environment(
                project_id, environment_id, name, env_data
            )
        except Exception as e:
            self.handle_error(e, f"updating environment {environment_id}")

    async def delete_environment(
        self, project_id: int, environment_id: int
    ) -> dict[str, Any]:
        """Delete an environment.

        Args:
            project_id: ID of the project
            environment_id: ID of the environment to delete

        Returns:
            Deletion result
        """
        try:
            return self.semaphore.delete_environment(project_id, environment_id)
        except Exception as e:
            self.handle_error(e, f"deleting environment {environment_id}")

    # Inventory-related tools

    async def list_inventory(self, project_id: int) -> dict[str, Any]:
        """List all inventory items for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of inventory items for the project
        """
        try:
            inventory = self.semaphore.list_inventory(project_id)
            return {"inventory": inventory}
        except Exception as e:
            self.handle_error(e, f"listing inventory for project {project_id}")

    async def get_inventory(self, project_id: int, inventory_id: int) -> dict[str, Any]:
        """Get details of a specific inventory item.

        Args:
            project_id: ID of the project
            inventory_id: ID of the inventory item to fetch

        Returns:
            Inventory item details
        """
        try:
            return self.semaphore.get_inventory(project_id, inventory_id)
        except Exception as e:
            self.handle_error(e, f"getting inventory {inventory_id}")

    async def create_inventory(
        self, project_id: int, name: str, inventory_data: str
    ) -> dict[str, Any]:
        """Create a new inventory item.

        Args:
            project_id: ID of the project
            name: Inventory name
            inventory_data: Inventory content (typically Ansible inventory format)

        Returns:
            Created inventory item details
        """
        try:
            return self.semaphore.create_inventory(project_id, name, inventory_data)
        except Exception as e:
            self.handle_error(e, f"creating inventory '{name}' in project {project_id}")

    async def update_inventory(
        self,
        project_id: int,
        inventory_id: int,
        name: Optional[str] = None,
        inventory_data: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing inventory item.

        Args:
            project_id: ID of the project
            inventory_id: ID of the inventory item to update
            name: Inventory name (optional)
            inventory_data: Inventory content (optional)

        Returns:
            Updated inventory item details
        """
        try:
            return self.semaphore.update_inventory(
                project_id, inventory_id, name, inventory_data
            )
        except Exception as e:
            self.handle_error(e, f"updating inventory {inventory_id}")

    async def delete_inventory(
        self, project_id: int, inventory_id: int
    ) -> dict[str, Any]:
        """Delete an inventory item.

        Args:
            project_id: ID of the project
            inventory_id: ID of the inventory item to delete

        Returns:
            Deletion result
        """
        try:
            return self.semaphore.delete_inventory(project_id, inventory_id)
        except Exception as e:
            self.handle_error(e, f"deleting inventory {inventory_id}")
