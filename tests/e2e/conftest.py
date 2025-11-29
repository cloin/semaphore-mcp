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
