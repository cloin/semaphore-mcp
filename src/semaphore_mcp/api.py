"""
Semaphore API client module.

This module provides a client for interacting with SemaphoreUI's API.
"""

import json
import os
from typing import Any, Dict, List, Optional

import requests


class SemaphoreAPIClient:
    """Client for interacting with the SemaphoreUI API."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initialize the SemaphoreUI API client.

        Args:
            base_url: Base URL of the SemaphoreUI API (e.g., "http://localhost:3000")
            token: Optional API token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.token = token or os.environ.get("SEMAPHORE_API_TOKEN")
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the SemaphoreUI API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without leading slash)
            **kwargs: Additional arguments to pass to requests

        Returns:
            API response as dictionary

        Raises:
            requests.exceptions.HTTPError: If the request fails
        """
        url = f"{self.base_url}/api/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()

        if response.content:
            return response.json()
        return {}

    # Project endpoints
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        result = self._request("GET", "projects")
        return result if isinstance(result, list) else []

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get a project by ID."""
        return self._request("GET", f"project/{project_id}")

    # Template endpoints
    def list_templates(self, project_id: int) -> List[Dict[str, Any]]:
        """List all templates for a project."""
        result = self._request("GET", f"project/{project_id}/templates")
        return result if isinstance(result, list) else []

    def get_template(self, project_id: int, template_id: int) -> Dict[str, Any]:
        """Get a template by ID."""
        return self._request("GET", f"project/{project_id}/template/{template_id}")

    # Task endpoints
    def list_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """List all tasks for a project."""
        result = self._request("GET", f"project/{project_id}/tasks")
        return result if isinstance(result, list) else []

    def get_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Get a task by ID."""
        return self._request("GET", f"project/{project_id}/task/{task_id}")

    def run_task(
        self,
        project_id: int,
        template_id: int,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Run a task using a template.

        Args:
            project_id: Project ID
            template_id: Template ID
            environment: Optional environment variables for the task

        Returns:
            Task information
        """
        payload: Dict[str, Any] = {"template_id": template_id}
        if environment:
            payload["environment"] = environment

        return self._request("POST", f"project/{project_id}/tasks", json=payload)

    def get_task_output(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Get the output of a task."""
        return self._request("GET", f"project/{project_id}/task/{task_id}/output")

    def stop_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Stop a running task."""
        return self._request("POST", f"project/{project_id}/tasks/{task_id}/stop")

    def get_last_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """Get last 200 tasks for a project (more efficient than full list)."""
        result = self._request("GET", f"project/{project_id}/tasks/last")
        return result if isinstance(result, list) else []

    def get_task_raw_output(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Get raw task output."""
        return self._request("GET", f"project/{project_id}/tasks/{task_id}/raw_output")

    def delete_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Delete task and its output."""
        return self._request("DELETE", f"project/{project_id}/tasks/{task_id}")

    def restart_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Restart a task (typically used for failed or stopped tasks)."""
        # Note: This endpoint may need to be verified with SemaphoreUI API docs
        # It might be POST /project/{project_id}/tasks/{task_id}/restart
        return self._request("POST", f"project/{project_id}/tasks/{task_id}/restart")

    # Environment endpoints
    def list_environments(self, project_id: int) -> List[Dict[str, Any]]:
        """List all environments for a project."""
        result = self._request("GET", f"project/{project_id}/environment")
        return result if isinstance(result, list) else []

    def get_environment(self, project_id: int, environment_id: int) -> Dict[str, Any]:
        """Get an environment by ID."""
        return self._request(
            "GET", f"project/{project_id}/environment/{environment_id}"
        )

    def create_environment(
        self, project_id: int, name: str, env_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create a new environment for a project.

        Args:
            project_id: Project ID
            name: Environment name
            env_data: Environment variables as key-value pairs

        Returns:
            Created environment information
        """
        # Include project_id in payload to match SemaphoreUI API requirements
        payload = {"name": name, "project_id": project_id}

        # Encode environment variables
        if env_data:
            # Use JSON string format (modern SemaphoreUI versions)
            payload["json"] = json.dumps(env_data)

        return self._request("POST", f"project/{project_id}/environment", json=payload)

    def update_environment(
        self,
        project_id: int,
        environment_id: int,
        name: Optional[str] = None,
        env_data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing environment.

        Args:
            project_id: Project ID
            environment_id: Environment ID
            name: Environment name (optional)
            env_data: Environment variables as key-value pairs (optional)

        Returns:
            Updated environment information
        """
        # Include project_id and environment_id in payload to match SemaphoreUI API requirements
        payload: Dict[str, Any] = {"project_id": project_id, "id": environment_id}

        # Only update what's specified
        if name is not None:
            payload["name"] = name

        # Encode environment variables if provided
        if env_data is not None:
            # Use JSON format (modern SemaphoreUI versions)
            payload["json"] = json.dumps(env_data)

        return self._request(
            "PUT", f"project/{project_id}/environment/{environment_id}", json=payload
        )

    def delete_environment(
        self, project_id: int, environment_id: int
    ) -> Dict[str, Any]:
        """Delete an environment by ID."""
        return self._request(
            "DELETE", f"project/{project_id}/environment/{environment_id}"
        )

    # Inventory endpoints
    def list_inventory(self, project_id: int) -> List[Dict[str, Any]]:
        """List all inventory items for a project."""
        result = self._request("GET", f"project/{project_id}/inventory")
        return result if isinstance(result, list) else []

    def get_inventory(self, project_id: int, inventory_id: int) -> Dict[str, Any]:
        """Get an inventory item by ID."""
        return self._request("GET", f"project/{project_id}/inventory/{inventory_id}")

    def create_inventory(
        self, project_id: int, name: str, inventory_data: str
    ) -> Dict[str, Any]:
        """Create a new inventory item for a project.

        Args:
            project_id: Project ID
            name: Inventory name
            inventory_data: Inventory content (typically Ansible inventory format)

        Returns:
            Created inventory information
        """
        # Include project_id in payload to match SemaphoreUI API requirements
        payload = {"name": name, "type": "file", "project_id": project_id}

        # Add inventory content
        if inventory_data:
            payload["inventory"] = inventory_data

        return self._request("POST", f"project/{project_id}/inventory", json=payload)

    def update_inventory(
        self,
        project_id: int,
        inventory_id: int,
        name: Optional[str] = None,
        inventory_data: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing inventory item.

        Args:
            project_id: Project ID
            inventory_id: Inventory ID
            name: Inventory name (optional)
            inventory_data: Inventory content (optional)

        Returns:
            Updated inventory information
        """
        # Include project_id and inventory_id in payload to match SemaphoreUI API requirements
        payload = {"type": "file", "project_id": project_id, "id": inventory_id}

        # Only update what's specified
        if name is not None:
            payload["name"] = name

        # Add inventory content if provided
        if inventory_data is not None:
            payload["inventory"] = inventory_data

        return self._request(
            "PUT", f"project/{project_id}/inventory/{inventory_id}", json=payload
        )

    def delete_inventory(self, project_id: int, inventory_id: int) -> Dict[str, Any]:
        """Delete an inventory item by ID."""
        return self._request("DELETE", f"project/{project_id}/inventory/{inventory_id}")


# Convenience factory function
def create_client(
    base_url: Optional[str] = None, token: Optional[str] = None
) -> SemaphoreAPIClient:
    """
    Create a SemaphoreUI API client.

    Uses environment variables if parameters are not provided:
    - SEMAPHORE_URL: Base URL of the SemaphoreUI API
    - SEMAPHORE_API_TOKEN: API token for authentication

    Args:
        base_url: Base URL of the SemaphoreUI API (default: from environment)
        token: API token for authentication (default: from environment)

    Returns:
        Configured SemaphoreAPIClient
    """
    resolved_base_url = base_url or os.environ.get(
        "SEMAPHORE_URL", "http://localhost:3000"
    )
    assert resolved_base_url is not None  # Should never be None due to fallback
    return SemaphoreAPIClient(resolved_base_url, token)
