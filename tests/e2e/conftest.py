"""Shared pytest fixtures for E2E tests."""

import os
import sys
from pathlib import Path

import pytest

# Add e2e directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


@pytest.fixture(scope="session")
def mcp_server_url() -> str:
    """Get the MCP server URL from environment."""
    return os.getenv("MCP_SERVER_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def inspector(mcp_server_url: str) -> MCPInspector:
    """Create an MCP Inspector client for the session."""
    return MCPInspector(mcp_server_url)


@pytest.fixture
def created_project(inspector: MCPInspector):
    """Create a test project and clean up after the test.

    Yields:
        dict: The created project data including 'id'
    """
    result = inspector.call_tool("create_project", {"name": "E2E Test Project"})
    project = parse_mcp_response(result)

    yield project

    # Cleanup
    try:
        inspector.call_tool("delete_project", {"project_id": project["id"]})
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def created_access_key(inspector: MCPInspector, created_project: dict):
    """Create a 'none' type access key for test repositories.

    Uses 'none' type which is suitable for public repositories.

    Yields:
        tuple: (access_key_data, project_id)
    """
    project_id = created_project["id"]
    result = inspector.call_tool(
        "create_access_key",
        {
            "project_id": project_id,
            "name": "E2E Test Access Key",
            "key_type": "none",
        },
    )
    access_key = parse_mcp_response(result)

    yield access_key, project_id
    # No cleanup needed - access key deleted with project


@pytest.fixture
def created_environment(inspector: MCPInspector, created_project: dict):
    """Create a test environment and clean up after the test.

    Requires a project to exist first.

    Yields:
        tuple: (environment_data, project_id)
    """
    project_id = created_project["id"]
    result = inspector.call_tool(
        "create_environment",
        {
            "project_id": project_id,
            "name": "E2E Test Environment",
            "env_data": {"TEST_VAR": "test_value"},
        },
    )
    environment = parse_mcp_response(result)

    yield environment, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_environment",
            {"project_id": project_id, "environment_id": environment["id"]},
        )
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def created_inventory(inspector: MCPInspector, created_project: dict):
    """Create a test inventory and clean up after the test.

    Requires a project to exist first.

    Yields:
        tuple: (inventory_data, project_id)
    """
    project_id = created_project["id"]
    result = inspector.call_tool(
        "create_inventory",
        {
            "project_id": project_id,
            "name": "E2E Test Inventory",
            "inventory_data": "[all]\nlocalhost ansible_connection=local",
        },
    )
    inventory = parse_mcp_response(result)

    yield inventory, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_inventory",
            {"project_id": project_id, "inventory_id": inventory["id"]},
        )
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def created_repository(
    inspector: MCPInspector, created_project: dict, created_access_key: tuple
):
    """Create a test repository and clean up after the test.

    Uses the cloin/ansible-test public GitHub repository.

    Requires a project and access key to exist first.

    Yields:
        tuple: (repository_data, project_id)
    """
    project_id = created_project["id"]
    access_key, _ = created_access_key
    result = inspector.call_tool(
        "create_repository",
        {
            "project_id": project_id,
            "name": "E2E Test Repository",
            "git_url": "https://github.com/cloin/ansible-test",
            "git_branch": "main",
            "ssh_key_id": access_key["id"],
        },
    )
    repository = parse_mcp_response(result)

    yield repository, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_repository",
            {"project_id": project_id, "repository_id": repository["id"]},
        )
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def created_template(
    inspector: MCPInspector,
    created_project: dict,
    created_environment: tuple,
    created_inventory: tuple,
    created_repository: tuple,
):
    """Create a test template and clean up after the test.

    Uses the test.yml playbook from cloin/ansible-test repository.
    This playbook accepts sleep_seconds and body variables.

    Requires project, environment, inventory, and repository to exist first.

    Yields:
        tuple: (template_data, project_id)
    """
    project_id = created_project["id"]
    environment, _ = created_environment
    inventory, _ = created_inventory
    repository, _ = created_repository

    result = inspector.call_tool(
        "create_template",
        {
            "project_id": project_id,
            "name": "E2E Test Template",
            "playbook": "test.yml",
            "inventory_id": inventory["id"],
            "repository_id": repository["id"],
            "environment_id": environment["id"],
        },
    )
    template = parse_mcp_response(result)

    yield template, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_template",
            {"project_id": project_id, "template_id": template["id"]},
        )
    except Exception:
        pass  # Best effort cleanup


# ============================================================================
# Class-scoped fixtures for task execution tests
# These fixtures are shared across all tests in a class for efficiency
# ============================================================================


@pytest.fixture(scope="class")
def task_test_project(inspector: MCPInspector):
    """Create a project for task execution tests - shared across class.

    Yields:
        dict: The created project data including 'id'
    """
    result = inspector.call_tool("create_project", {"name": "Task E2E Test Project"})
    project = parse_mcp_response(result)

    yield project

    # Cleanup at end of class
    try:
        inspector.call_tool("delete_project", {"project_id": project["id"]})
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture(scope="class")
def task_test_access_key(inspector: MCPInspector, task_test_project: dict):
    """Create a 'none' type access key for task test repositories - shared across class.

    Uses 'none' type which is suitable for public repositories.

    Yields:
        tuple: (access_key_data, project_id)
    """
    project_id = task_test_project["id"]
    result = inspector.call_tool(
        "create_access_key",
        {
            "project_id": project_id,
            "name": "Task Test Access Key",
            "key_type": "none",
        },
    )
    access_key = parse_mcp_response(result)

    yield access_key, project_id
    # No cleanup needed - access key deleted with project


@pytest.fixture(scope="class")
def task_test_environment(inspector: MCPInspector, task_test_project: dict):
    """Create an environment for task execution tests - shared across class.

    Yields:
        tuple: (environment_data, project_id)
    """
    project_id = task_test_project["id"]
    result = inspector.call_tool(
        "create_environment",
        {
            "project_id": project_id,
            "name": "Task Test Environment",
            "env_data": {"TEST_VAR": "test_value"},
        },
    )
    environment = parse_mcp_response(result)

    yield environment, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_environment",
            {"project_id": project_id, "environment_id": environment["id"]},
        )
    except Exception:
        pass


@pytest.fixture(scope="class")
def task_test_inventory(inspector: MCPInspector, task_test_project: dict):
    """Create an inventory for task execution tests - shared across class.

    Yields:
        tuple: (inventory_data, project_id)
    """
    project_id = task_test_project["id"]
    result = inspector.call_tool(
        "create_inventory",
        {
            "project_id": project_id,
            "name": "Task Test Inventory",
            "inventory_data": "[all]\nlocalhost ansible_connection=local",
        },
    )
    inventory = parse_mcp_response(result)

    yield inventory, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_inventory",
            {"project_id": project_id, "inventory_id": inventory["id"]},
        )
    except Exception:
        pass


@pytest.fixture(scope="class")
def task_test_repository(
    inspector: MCPInspector, task_test_project: dict, task_test_access_key: tuple
):
    """Create a repository for task execution tests - shared across class.

    Uses the cloin/ansible-test public GitHub repository.

    Yields:
        tuple: (repository_data, project_id)
    """
    project_id = task_test_project["id"]
    access_key, _ = task_test_access_key
    result = inspector.call_tool(
        "create_repository",
        {
            "project_id": project_id,
            "name": "Task Test Repository",
            "git_url": "https://github.com/cloin/ansible-test",
            "git_branch": "main",
            "ssh_key_id": access_key["id"],
        },
    )
    repository = parse_mcp_response(result)

    yield repository, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_repository",
            {"project_id": project_id, "repository_id": repository["id"]},
        )
    except Exception:
        pass


@pytest.fixture(scope="class")
def task_test_template(
    inspector: MCPInspector,
    task_test_project: dict,
    task_test_environment: tuple,
    task_test_inventory: tuple,
    task_test_repository: tuple,
):
    """Create a template for task execution tests - shared across class.

    Uses the test.yml playbook from cloin/ansible-test repository.
    This playbook accepts sleep_seconds and body variables.

    Yields:
        tuple: (template_data, project_id)
    """
    project_id = task_test_project["id"]
    environment, _ = task_test_environment
    inventory, _ = task_test_inventory
    repository, _ = task_test_repository

    result = inspector.call_tool(
        "create_template",
        {
            "project_id": project_id,
            "name": "Task Test Template",
            "playbook": "test.yml",
            "inventory_id": inventory["id"],
            "repository_id": repository["id"],
            "environment_id": environment["id"],
        },
    )
    template = parse_mcp_response(result)

    yield template, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_template",
            {"project_id": project_id, "template_id": template["id"]},
        )
    except Exception:
        pass


@pytest.fixture(scope="class")
def failing_template(
    inspector: MCPInspector,
    task_test_project: dict,
    task_test_environment: tuple,
    task_test_inventory: tuple,
    task_test_repository: tuple,
):
    """Create a template that will fail for testing failure analysis - shared across class.

    Uses a non-existent playbook to guarantee task failure.

    Yields:
        tuple: (template_data, project_id)
    """
    project_id = task_test_project["id"]
    environment, _ = task_test_environment
    inventory, _ = task_test_inventory
    repository, _ = task_test_repository

    result = inspector.call_tool(
        "create_template",
        {
            "project_id": project_id,
            "name": "Failing Test Template",
            "playbook": "nonexistent.yml",  # Will fail - playbook doesn't exist
            "inventory_id": inventory["id"],
            "repository_id": repository["id"],
            "environment_id": environment["id"],
        },
    )
    template = parse_mcp_response(result)

    yield template, project_id

    # Cleanup
    try:
        inspector.call_tool(
            "delete_template",
            {"project_id": project_id, "template_id": template["id"]},
        )
    except Exception:
        pass
