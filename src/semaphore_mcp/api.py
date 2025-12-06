"""
Semaphore API client module.

This module provides a client for interacting with SemaphoreUI's API.
"""

import json
import os
from typing import Any, Optional

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

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
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

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Enhance 404 error messages with more context
            if response.status_code == 404:
                raise requests.exceptions.HTTPError(
                    f"Resource not found (404): {url}. "
                    f"The requested resource may have been deleted or the ID may be incorrect.",
                    response=response,
                ) from e
            raise

        if response.content:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                # Handle cases where response is not valid JSON
                raise ValueError(
                    f"Invalid JSON response from {url}: {response.text[:200]}..."
                ) from e
        return {}

    # Project endpoints
    def list_projects(self) -> list[dict[str, Any]]:
        """List all projects."""
        result = self._request("GET", "projects")
        return result if isinstance(result, list) else []

    def get_project(self, project_id: int) -> dict[str, Any]:
        """Get a project by ID."""
        return self._request("GET", f"project/{project_id}")

    def create_project(
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
            alert: Enable alerts
            alert_chat: Chat channel for alerts
            max_parallel_tasks: Maximum parallel tasks (0 = unlimited)
            project_type: Project type
            demo: Create demo resources

        Returns:
            Created project information
        """
        payload: dict[str, Any] = {
            "name": name,
            "alert": alert,
            "max_parallel_tasks": max_parallel_tasks,
            "demo": demo,
        }

        if alert_chat is not None:
            payload["alert_chat"] = alert_chat
        if project_type is not None:
            payload["type"] = project_type

        return self._request("POST", "projects", json=payload)

    def update_project(
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
            project_id: Project ID
            name: Project name (optional)
            alert: Enable alerts (optional)
            alert_chat: Chat channel for alerts (optional)
            max_parallel_tasks: Maximum parallel tasks (optional)
            project_type: Project type (optional)

        Returns:
            Empty dict on success (204 response)
        """
        payload: dict[str, Any] = {"id": project_id}

        if name is not None:
            payload["name"] = name
        if alert is not None:
            payload["alert"] = alert
        if alert_chat is not None:
            payload["alert_chat"] = alert_chat
        if max_parallel_tasks is not None:
            payload["max_parallel_tasks"] = max_parallel_tasks
        if project_type is not None:
            payload["type"] = project_type

        return self._request("PUT", f"project/{project_id}", json=payload)

    def delete_project(self, project_id: int) -> dict[str, Any]:
        """Delete a project by ID.

        Args:
            project_id: Project ID

        Returns:
            Empty dict on success (204 response)
        """
        return self._request("DELETE", f"project/{project_id}")

    # Template endpoints
    def list_templates(self, project_id: int) -> list[dict[str, Any]]:
        """List all templates for a project."""
        result = self._request("GET", f"project/{project_id}/templates")
        return result if isinstance(result, list) else []

    def get_template(self, project_id: int, template_id: int) -> dict[str, Any]:
        """Get a template by ID."""
        return self._request("GET", f"project/{project_id}/templates/{template_id}")

    def create_template(
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
        """Create a new template for a project.

        Args:
            project_id: Project ID
            name: Template name
            playbook: Playbook file path (e.g., "playbook.yml")
            inventory_id: Inventory ID
            repository_id: Repository ID
            environment_id: Environment ID
            description: Template description
            arguments: Extra arguments (JSON string, e.g., "[]")
            allow_override_args_in_task: Allow overriding arguments in task
            suppress_success_alerts: Suppress success alerts
            app: Application type (default: "ansible")
            git_branch: Git branch to use
            survey_vars: Survey variables for prompting
            vaults: Vault configurations
            template_type: Template type ("", "build", or "deploy")
            start_version: Start version
            build_template_id: Build template ID (for deploy templates)
            autorun: Enable autorun
            view_id: View ID
            task_params: App-specific task parameters. For Ansible templates:
                - allow_override_limit: Allow task-level --limit override
                - allow_override_inventory: Allow task-level inventory override
                - allow_override_tags: Allow task-level --tags override
                - allow_override_skip_tags: Allow task-level --skip-tags override
                - limit: Default limit (list of hosts/groups)
                - tags: Default tags (list)
                - skip_tags: Default skip tags (list)

        Returns:
            Created template information
        """
        payload: dict[str, Any] = {
            "project_id": project_id,
            "name": name,
            "playbook": playbook,
            "inventory_id": inventory_id,
            "repository_id": repository_id,
            "environment_id": environment_id,
            "allow_override_args_in_task": allow_override_args_in_task,
            "suppress_success_alerts": suppress_success_alerts,
            "app": app,
            "autorun": autorun,
        }

        if description is not None:
            payload["description"] = description
        if arguments is not None:
            payload["arguments"] = arguments
        if git_branch is not None:
            payload["git_branch"] = git_branch
        if survey_vars is not None:
            payload["survey_vars"] = survey_vars
        if vaults is not None:
            payload["vaults"] = vaults
        if template_type is not None:
            payload["type"] = template_type
        if start_version is not None:
            payload["start_version"] = start_version
        if build_template_id is not None:
            payload["build_template_id"] = build_template_id
        if view_id is not None:
            payload["view_id"] = view_id
        if task_params is not None:
            payload["task_params"] = task_params

        return self._request("POST", f"project/{project_id}/templates", json=payload)

    def update_template(
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
            project_id: Project ID
            template_id: Template ID
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
            task_params: App-specific task parameters (optional). For Ansible:
                - allow_override_limit: Allow task-level --limit override
                - allow_override_inventory: Allow task-level inventory override
                - allow_override_tags: Allow task-level --tags override
                - allow_override_skip_tags: Allow task-level --skip-tags override
                - limit: Default limit (list of hosts/groups)
                - tags: Default tags (list)
                - skip_tags: Default skip tags (list)

        Returns:
            Empty dict on success (204 response)
        """
        # Fetch existing template to preserve unmodified fields
        existing = self.get_template(project_id, template_id)

        # Build payload starting from existing values
        payload: dict[str, Any] = {
            "id": template_id,
            "project_id": project_id,
            "name": existing.get("name", ""),
            "playbook": existing.get("playbook", ""),
            "inventory_id": existing.get("inventory_id", 0),
            "repository_id": existing.get("repository_id", 0),
            "environment_id": existing.get("environment_id", 0),
            "description": existing.get("description", ""),
            "arguments": existing.get("arguments", ""),
            "allow_override_args_in_task": existing.get(
                "allow_override_args_in_task", False
            ),
            "suppress_success_alerts": existing.get("suppress_success_alerts", False),
            "app": existing.get("app", ""),
            "git_branch": existing.get("git_branch", ""),
            "survey_vars": existing.get("survey_vars", []),
            "vaults": existing.get("vaults", []),
            "type": existing.get("type", ""),
            "start_version": existing.get("start_version", ""),
            "build_template_id": existing.get("build_template_id"),
            "autorun": existing.get("autorun", False),
            "view_id": existing.get("view_id"),
            "task_params": existing.get("task_params", {}),
        }

        # Override with specified updates
        if name is not None:
            payload["name"] = name
        if playbook is not None:
            payload["playbook"] = playbook
        if inventory_id is not None:
            payload["inventory_id"] = inventory_id
        if repository_id is not None:
            payload["repository_id"] = repository_id
        if environment_id is not None:
            payload["environment_id"] = environment_id
        if description is not None:
            payload["description"] = description
        if arguments is not None:
            payload["arguments"] = arguments
        if allow_override_args_in_task is not None:
            payload["allow_override_args_in_task"] = allow_override_args_in_task
        if suppress_success_alerts is not None:
            payload["suppress_success_alerts"] = suppress_success_alerts
        if app is not None:
            payload["app"] = app
        if git_branch is not None:
            payload["git_branch"] = git_branch
        if survey_vars is not None:
            payload["survey_vars"] = survey_vars
        if vaults is not None:
            payload["vaults"] = vaults
        if template_type is not None:
            payload["type"] = template_type
        if start_version is not None:
            payload["start_version"] = start_version
        if build_template_id is not None:
            payload["build_template_id"] = build_template_id
        if autorun is not None:
            payload["autorun"] = autorun
        if view_id is not None:
            payload["view_id"] = view_id
        if task_params is not None:
            payload["task_params"] = task_params

        return self._request(
            "PUT", f"project/{project_id}/templates/{template_id}", json=payload
        )

    def delete_template(self, project_id: int, template_id: int) -> dict[str, Any]:
        """Delete a template by ID.

        Args:
            project_id: Project ID
            template_id: Template ID

        Returns:
            Empty dict on success (204 response)
        """
        return self._request("DELETE", f"project/{project_id}/templates/{template_id}")

    def stop_all_template_tasks(
        self, project_id: int, template_id: int
    ) -> dict[str, Any]:
        """Stop all running tasks for a template.

        Args:
            project_id: Project ID
            template_id: Template ID

        Returns:
            Empty dict on success (204 response)
        """
        return self._request(
            "POST", f"project/{project_id}/templates/{template_id}/stop_all_tasks"
        )

    # Task endpoints
    def list_tasks(self, project_id: int) -> list[dict[str, Any]]:
        """List all tasks for a project."""
        result = self._request("GET", f"project/{project_id}/tasks")
        return result if isinstance(result, list) else []

    def get_task(self, project_id: int, task_id: int) -> dict[str, Any]:
        """Get a task by ID."""
        return self._request("GET", f"project/{project_id}/task/{task_id}")

    def run_task(
        self,
        project_id: int,
        template_id: int,
        environment: Optional[dict[str, str]] = None,
        limit: Optional[str] = None,
        dry_run: Optional[bool] = None,
        diff: Optional[bool] = None,
        debug: Optional[bool] = None,
        playbook: Optional[str] = None,
        git_branch: Optional[str] = None,
        message: Optional[str] = None,
        arguments: Optional[str] = None,
        inventory_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Run a task using a template.

        Args:
            project_id: Project ID
            template_id: Template ID
            environment: Optional environment variables for the task
            limit: Restrict execution to specific hosts/groups (Ansible --limit)
            dry_run: Run without making changes (Ansible --check)
            diff: Show differences when changing files (Ansible --diff)
            debug: Enable verbose debug output
            playbook: Override playbook file path
            git_branch: Override git branch to use
            message: Task description/message
            arguments: Additional CLI arguments
            inventory_id: Override inventory to use

        Returns:
            Task information
        """
        payload: dict[str, Any] = {"template_id": template_id}
        if environment:
            # Semaphore API expects environment as a JSON string, not a dict
            payload["environment"] = json.dumps(environment)
        if limit:
            payload["limit"] = limit
        if dry_run is not None:
            payload["dry_run"] = dry_run
        if diff is not None:
            payload["diff"] = diff
        if debug is not None:
            payload["debug"] = debug
        if playbook:
            payload["playbook"] = playbook
        if git_branch:
            payload["git_branch"] = git_branch
        if message:
            payload["message"] = message
        if arguments:
            payload["arguments"] = arguments
        if inventory_id is not None:
            payload["inventory_id"] = inventory_id

        return self._request("POST", f"project/{project_id}/tasks", json=payload)

    def stop_task(self, project_id: int, task_id: int) -> dict[str, Any]:
        """Stop a running task."""
        return self._request("POST", f"project/{project_id}/tasks/{task_id}/stop")

    def get_last_tasks(self, project_id: int) -> list[dict[str, Any]]:
        """Get last 200 tasks for a project (more efficient than full list)."""
        result = self._request("GET", f"project/{project_id}/tasks/last")
        return result if isinstance(result, list) else []

    def get_task_raw_output(self, project_id: int, task_id: int) -> str:
        """Get raw task output."""
        url = f"{self.base_url}/api/project/{project_id}/tasks/{task_id}/raw_output"
        response = self.session.request("GET", url)
        response.raise_for_status()

        # Return raw text content instead of trying to parse as JSON
        return response.text

    def delete_task(self, project_id: int, task_id: int) -> dict[str, Any]:
        """Delete task and its output."""
        return self._request("DELETE", f"project/{project_id}/tasks/{task_id}")

    def restart_task(self, project_id: int, task_id: int) -> dict[str, Any]:
        """Restart a task (typically used for failed or stopped tasks)."""
        # Note: This endpoint may need to be verified with SemaphoreUI API docs
        # It might be POST /project/{project_id}/tasks/{task_id}/restart
        return self._request("POST", f"project/{project_id}/tasks/{task_id}/restart")

    # Environment endpoints
    def list_environments(self, project_id: int) -> list[dict[str, Any]]:
        """List all environments for a project."""
        result = self._request("GET", f"project/{project_id}/environment")
        return result if isinstance(result, list) else []

    def get_environment(self, project_id: int, environment_id: int) -> dict[str, Any]:
        """Get an environment by ID."""
        return self._request(
            "GET", f"project/{project_id}/environment/{environment_id}"
        )

    def create_environment(
        self, project_id: int, name: str, env_data: dict[str, str]
    ) -> dict[str, Any]:
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
        env_data: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
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
        payload: dict[str, Any] = {"project_id": project_id, "id": environment_id}

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
    ) -> dict[str, Any]:
        """Delete an environment by ID."""
        return self._request(
            "DELETE", f"project/{project_id}/environment/{environment_id}"
        )

    # Inventory endpoints
    def list_inventory(self, project_id: int) -> list[dict[str, Any]]:
        """List all inventory items for a project."""
        result = self._request("GET", f"project/{project_id}/inventory")
        return result if isinstance(result, list) else []

    def get_inventory(self, project_id: int, inventory_id: int) -> dict[str, Any]:
        """Get an inventory item by ID."""
        return self._request("GET", f"project/{project_id}/inventory/{inventory_id}")

    def create_inventory(
        self, project_id: int, name: str, inventory_data: str
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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

    def delete_inventory(self, project_id: int, inventory_id: int) -> dict[str, Any]:
        """Delete an inventory item by ID."""
        return self._request("DELETE", f"project/{project_id}/inventory/{inventory_id}")

    # Repository endpoints
    def list_repositories(self, project_id: int) -> list[dict[str, Any]]:
        """List all repositories for a project."""
        result = self._request("GET", f"project/{project_id}/repositories")
        return result if isinstance(result, list) else []

    def get_repository(self, project_id: int, repository_id: int) -> dict[str, Any]:
        """Get a repository by ID."""
        return self._request(
            "GET", f"project/{project_id}/repositories/{repository_id}"
        )

    def create_repository(
        self,
        project_id: int,
        name: str,
        git_url: str,
        git_branch: str,
        ssh_key_id: int,
    ) -> dict[str, Any]:
        """Create a new repository for a project.

        Args:
            project_id: Project ID
            name: Repository name
            git_url: Git repository URL
            git_branch: Git branch to use
            ssh_key_id: SSH key ID for authentication

        Returns:
            Created repository information
        """
        payload = {
            "project_id": project_id,
            "name": name,
            "git_url": git_url,
            "git_branch": git_branch,
            "ssh_key_id": ssh_key_id,
        }

        return self._request("POST", f"project/{project_id}/repositories", json=payload)

    def update_repository(
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
            project_id: Project ID
            repository_id: Repository ID
            name: Repository name (optional)
            git_url: Git repository URL (optional)
            git_branch: Git branch to use (optional)
            ssh_key_id: SSH key ID for authentication (optional)

        Returns:
            Updated repository information
        """
        # Fetch existing repository to preserve unmodified fields
        existing = self.get_repository(project_id, repository_id)

        # Build payload starting from existing values
        payload: dict[str, Any] = {
            "id": repository_id,
            "project_id": project_id,
            "name": existing.get("name", ""),
            "git_url": existing.get("git_url", ""),
            "git_branch": existing.get("git_branch", ""),
            "ssh_key_id": existing.get("ssh_key_id", 0),
        }

        # Override with specified updates
        if name is not None:
            payload["name"] = name
        if git_url is not None:
            payload["git_url"] = git_url
        if git_branch is not None:
            payload["git_branch"] = git_branch
        if ssh_key_id is not None:
            payload["ssh_key_id"] = ssh_key_id

        return self._request(
            "PUT", f"project/{project_id}/repositories/{repository_id}", json=payload
        )

    def delete_repository(self, project_id: int, repository_id: int) -> dict[str, Any]:
        """Delete a repository by ID."""
        return self._request(
            "DELETE", f"project/{project_id}/repositories/{repository_id}"
        )

    # Access Key endpoints
    def list_access_keys(self, project_id: int) -> list[dict[str, Any]]:
        """List all access keys for a project."""
        result = self._request("GET", f"project/{project_id}/keys")
        return result if isinstance(result, list) else []

    def get_access_key(self, project_id: int, key_id: int) -> dict[str, Any]:
        """Get an access key by ID."""
        return self._request("GET", f"project/{project_id}/keys/{key_id}")

    def create_access_key(
        self,
        project_id: int,
        name: str,
        key_type: str,
        login: Optional[str] = None,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new access key for a project.

        Args:
            project_id: Project ID
            name: Access key name
            key_type: Type of key ("none", "ssh", or "login_password")
            login: Username for ssh or login_password types
            password: Password for login_password type
            private_key: Private key content for ssh type

        Returns:
            Created access key information
        """
        payload: dict[str, Any] = {
            "project_id": project_id,
            "name": name,
            "type": key_type,
        }

        # Add type-specific fields
        if key_type == "login_password" and login:
            payload["login_password"] = {"login": login, "password": password or ""}
        elif key_type == "ssh" and private_key:
            payload["ssh"] = {"login": login or "", "private_key": private_key}

        return self._request("POST", f"project/{project_id}/keys", json=payload)

    def update_access_key(
        self,
        project_id: int,
        key_id: int,
        name: Optional[str] = None,
        key_type: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing access key.

        Args:
            project_id: Project ID
            key_id: Access key ID
            name: Access key name (optional)
            key_type: Type of key (optional)
            login: Username (optional)
            password: Password (optional)
            private_key: Private key content (optional)

        Returns:
            Updated access key information
        """
        payload: dict[str, Any] = {"id": key_id, "project_id": project_id}

        if name is not None:
            payload["name"] = name
        if key_type is not None:
            payload["type"] = key_type
        if key_type == "login_password" and login:
            payload["login_password"] = {"login": login, "password": password or ""}
        elif key_type == "ssh" and private_key:
            payload["ssh"] = {"login": login or "", "private_key": private_key}

        return self._request("PUT", f"project/{project_id}/keys/{key_id}", json=payload)

    def delete_access_key(self, project_id: int, key_id: int) -> dict[str, Any]:
        """Delete an access key by ID."""
        return self._request("DELETE", f"project/{project_id}/keys/{key_id}")


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
