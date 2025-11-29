"""E2E tests for Task tools - Read-only operations.

This module tests read-only task operations that don't require existing
templates or running tasks. These tests work with any project.

For comprehensive task execution tests (run_task, stop_task, get_task,
failure analysis, etc.), see test_task_execution_e2e.py which uses the
cloin/ansible-test repository and proper fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestTasksE2E:
    """E2E tests for read-only task operations.

    These tests verify task listing, filtering, and querying operations
    that work without requiring existing templates or tasks.

    For task execution tests, see TestTaskExecutionE2E in test_task_execution_e2e.py.
    """

    def test_list_tasks(self, inspector: MCPInspector, created_project: dict):
        """Test listing tasks for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "list_tasks", {"project_id": project_id, "limit": 5}
        )
        data = parse_mcp_response(result)

        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_filter_tasks(self, inspector: MCPInspector, created_project: dict):
        """Test filtering tasks with various criteria."""
        project_id = created_project["id"]

        # Filter by status
        result = inspector.call_tool(
            "filter_tasks",
            {"project_id": project_id, "status": ["success", "error"], "limit": 10},
        )
        data = parse_mcp_response(result)

        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        # Check statistics are returned
        if "statistics" in data:
            assert isinstance(data["statistics"], dict)

    def test_get_latest_failed_task(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test getting the latest failed task for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "get_latest_failed_task", {"project_id": project_id}
        )
        data = parse_mcp_response(result)

        # May return a task or a message if no failed tasks exist
        assert data is not None

    def test_get_waiting_tasks(self, inspector: MCPInspector, created_project: dict):
        """Test getting all waiting tasks for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("get_waiting_tasks", {"project_id": project_id})
        data = parse_mcp_response(result)

        # Response contains waiting_tasks key
        assert "waiting_tasks" in data
        assert isinstance(data["waiting_tasks"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
