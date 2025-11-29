"""E2E tests for Task tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestTasksE2E:
    """E2E tests for task operations.

    Task operations are primarily read-only (list, get, filter) or require
    existing templates to run. Most mutating operations are skipped because
    they require a complete project setup with templates.
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
        # Optionally check stats if returned
        if "stats" in data:
            assert isinstance(data["stats"], dict)

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

    @pytest.mark.skip(reason="Requires template to be created first")
    def test_run_task(self, inspector: MCPInspector, created_project: dict):
        """Test running a task from a template.

        This test is skipped because it requires a template to exist.
        """
        template_id = 1  # Would need to create first

        result = inspector.call_tool(
            "run_task",
            {"template_id": template_id, "message": "E2E test run"},
        )
        data = parse_mcp_response(result)

        assert "id" in data or "task_id" in data

    @pytest.mark.skip(reason="Requires running task to exist")
    def test_get_task(self, inspector: MCPInspector, created_project: dict):
        """Test getting a specific task."""
        project_id = created_project["id"]
        task_id = 1  # Would need to have a task first

        result = inspector.call_tool(
            "get_task", {"project_id": project_id, "task_id": task_id}
        )
        data = parse_mcp_response(result)

        assert data["id"] == task_id

    @pytest.mark.skip(reason="Requires running task to exist")
    def test_stop_task(self, inspector: MCPInspector, created_project: dict):
        """Test stopping a running task."""
        project_id = created_project["id"]
        task_id = 1  # Would need a running task

        result = inspector.call_tool(
            "stop_task", {"project_id": project_id, "task_id": task_id}
        )
        assert result is not None

    @pytest.mark.skip(reason="Requires running tasks to exist")
    def test_bulk_stop_tasks(self, inspector: MCPInspector, created_project: dict):
        """Test stopping multiple tasks."""
        project_id = created_project["id"]
        task_ids = [1, 2, 3]  # Would need running tasks

        result = inspector.call_tool(
            "bulk_stop_tasks",
            {"project_id": project_id, "task_ids": task_ids, "confirm": True},
        )
        assert result is not None

    @pytest.mark.skip(reason="Requires completed task to exist")
    def test_get_task_raw_output(self, inspector: MCPInspector, created_project: dict):
        """Test getting raw output from a task."""
        project_id = created_project["id"]
        task_id = 1  # Would need a completed task

        result = inspector.call_tool(
            "get_task_raw_output",
            {"project_id": project_id, "task_id": task_id},
        )
        data = parse_mcp_response(result)

        # Should return raw output text
        assert data is not None

    @pytest.mark.skip(reason="Requires failed task to exist")
    def test_analyze_task_failure(self, inspector: MCPInspector, created_project: dict):
        """Test analyzing a failed task."""
        project_id = created_project["id"]
        task_id = 1  # Would need a failed task

        result = inspector.call_tool(
            "analyze_task_failure",
            {"project_id": project_id, "task_id": task_id},
        )
        data = parse_mcp_response(result)

        # Should return analysis data
        assert data is not None

    @pytest.mark.skip(reason="Requires failed tasks to exist")
    def test_bulk_analyze_failures(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test analyzing multiple failed tasks."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "bulk_analyze_failures",
            {"project_id": project_id, "limit": 5},
        )
        data = parse_mcp_response(result)

        # Should return bulk analysis data
        assert data is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
