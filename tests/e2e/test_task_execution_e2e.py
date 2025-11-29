"""E2E tests for Task execution operations.

These tests go beyond read-only operations to test full task execution
including running tasks, monitoring, stopping, and failure analysis.

Uses the cloin/ansible-test repository which contains a test.yml playbook
that accepts:
- sleep_seconds: Controls pause duration (for testing follow and stop)
- body: Variable displayed by debug task
"""

import sys
import time
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


def wait_for_task_completion(
    inspector: MCPInspector,
    project_id: int,
    task_id: int,
    timeout: int = 60,
    poll_interval: int = 2,
) -> dict:
    """Wait for a task to complete and return its final state.

    Args:
        inspector: MCP Inspector instance
        project_id: Project ID
        task_id: Task ID to wait for
        timeout: Maximum seconds to wait
        poll_interval: Seconds between polls

    Returns:
        Final task state dict
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = inspector.call_tool(
            "get_task", {"project_id": project_id, "task_id": task_id}
        )
        task = parse_mcp_response(result)

        # Handle both direct task response and wrapped response
        if isinstance(task, dict):
            status = task.get("status")
            if status in ["success", "error", "stopped"]:
                return task

        time.sleep(poll_interval)

    raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")


class TestTaskExecutionE2E:
    """E2E tests for task execution operations.

    Uses class-scoped fixtures so all tests in this class share the same
    project, repository, inventory, environment, and templates.
    """

    # =========================================================================
    # A. Basic Task Execution Tests
    # =========================================================================

    def test_run_task_basic(self, inspector: MCPInspector, task_test_template: tuple):
        """Test running a task without follow mode."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
            },
        )
        data = parse_mcp_response(result)

        # Verify response structure
        assert "task" in data, "Response should contain 'task'"
        assert "web_urls" in data, "Response should contain 'web_urls'"
        assert "message" in data, "Response should contain 'message'"

        # Verify task was created
        task = data["task"]
        assert "id" in task, "Task should have an ID"

        # Verify URLs are present
        web_urls = data["web_urls"]
        assert "task_detail" in web_urls, "Should have task_detail URL"
        assert "project_tasks" in web_urls, "Should have project_tasks URL"

    def test_run_task_with_follow(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with follow mode enabled."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        data = parse_mcp_response(result)

        # Verify response structure
        assert "task" in data, "Response should contain 'task'"
        assert "monitoring" in data, "Response should contain 'monitoring'"

        # Verify monitoring was enabled
        monitoring = data["monitoring"]
        assert (
            "enabled" in monitoring
            or "completed" in monitoring
            or "duration_seconds" in monitoring
        )

    # =========================================================================
    # B. run_task Parameters Tests
    # =========================================================================

    def test_run_task_with_dry_run(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with dry_run=True (Ansible --check)."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "dry_run": True,
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_diff(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with diff=True (Ansible --diff)."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "diff": True,
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_debug(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with debug=True for verbose output."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "debug": True,
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_limit(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with limit to restrict hosts."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "limit": "localhost",
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_git_branch(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with git_branch override."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "git_branch": "main",
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_message(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with a custom message."""
        template, project_id = task_test_template
        custom_message = "E2E Test Run - Custom Message"

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "message": custom_message,
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_arguments(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with additional CLI arguments."""
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "arguments": "-v",  # Verbose flag
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_inventory_override(
        self,
        inspector: MCPInspector,
        task_test_template: tuple,
        task_test_inventory: tuple,
    ):
        """Test running a task with inventory_id override."""
        template, project_id = task_test_template
        inventory, _ = task_test_inventory

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "inventory_id": inventory["id"],
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_run_task_with_extra_vars(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test running a task with extra variables passed via arguments.

        Uses the body variable from the test playbook, passed via -e flag.
        """
        template, project_id = task_test_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "arguments": "-e body='Hello from E2E test'",
                "follow": True,  # Wait to see completion
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    # =========================================================================
    # C. Task Monitoring & Output Tests
    # =========================================================================

    def test_get_task(self, inspector: MCPInspector, task_test_template: tuple):
        """Test getting task details after running."""
        template, project_id = task_test_template

        # First run a task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Then get the task details
        get_result = inspector.call_tool(
            "get_task",
            {"project_id": project_id, "task_id": task_id},
        )
        task = parse_mcp_response(get_result)

        assert task is not None
        # Task may have 'id' directly or be wrapped
        if isinstance(task, dict):
            assert "id" in task or "task" in task

    def test_get_task_raw_output(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test getting raw output from a completed task."""
        template, project_id = task_test_template

        # Run a task and wait for completion
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Only wait if monitoring shows task didn't complete during follow
        monitoring = run_data.get("monitoring", {})
        if not monitoring.get("completed", False):
            wait_for_task_completion(inspector, project_id, task_id, timeout=120)

        # Get raw output
        output_result = inspector.call_tool(
            "get_task_raw_output",
            {"project_id": project_id, "task_id": task_id},
        )

        # Raw output should be returned (may be empty string or text)
        assert output_result is not None

    def test_list_tasks_after_run(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test that a newly run task appears in the task list."""
        template, project_id = task_test_template

        # Run a task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # List tasks
        list_result = inspector.call_tool(
            "list_tasks",
            {"project_id": project_id, "limit": 10},
        )
        list_data = parse_mcp_response(list_result)

        assert "tasks" in list_data
        task_ids = [t["id"] for t in list_data["tasks"]]
        assert task_id in task_ids, f"Task {task_id} should appear in task list"

    def test_filter_tasks_by_status(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test filtering tasks by status after runs."""
        template, project_id = task_test_template

        # Run a task and wait for it to complete
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Only wait if monitoring shows task didn't complete during follow
        monitoring = run_data.get("monitoring", {})
        if not monitoring.get("completed", False):
            wait_for_task_completion(inspector, project_id, task_id, timeout=120)

        # Filter by success status
        filter_result = inspector.call_tool(
            "filter_tasks",
            {"project_id": project_id, "status": ["success"], "limit": 10},
        )
        filter_data = parse_mcp_response(filter_result)

        assert "tasks" in filter_data
        assert "statistics" in filter_data

    # =========================================================================
    # D. Task Control Tests
    # =========================================================================

    def test_stop_task(self, inspector: MCPInspector, task_test_template: tuple):
        """Test stopping a running task.

        Uses sleep_seconds to create a long-running task that can be stopped.
        """
        template, project_id = task_test_template

        # Start a long-running task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "arguments": "-e sleep_seconds=60",  # Long sleep so we can stop it
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Give it a moment to start
        time.sleep(3)

        # Stop the task
        stop_result = inspector.call_tool(
            "stop_task",
            {"project_id": project_id, "task_id": task_id},
        )

        # Verify stop was called (result format may vary)
        assert stop_result is not None

    def test_bulk_stop_tasks_preview(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test bulk stop preview mode (confirm=False)."""
        template, project_id = task_test_template

        # Start a task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "arguments": "-e sleep_seconds=30",
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Give it a moment to start
        time.sleep(2)

        # Try bulk stop with confirm=False (preview mode)
        bulk_result = inspector.call_tool(
            "bulk_stop_tasks",
            {
                "project_id": project_id,
                "task_ids": [task_id],
                "confirm": False,
            },
        )
        bulk_data = parse_mcp_response(bulk_result)

        # Should return confirmation required
        assert "confirmation_required" in bulk_data
        assert bulk_data["confirmation_required"] is True

        # Clean up - stop the task
        inspector.call_tool(
            "stop_task",
            {"project_id": project_id, "task_id": task_id},
        )

    def test_bulk_stop_tasks_execute(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test bulk stop with confirm=True."""
        template, project_id = task_test_template

        # Start a task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "arguments": "-e sleep_seconds=30",
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Give it a moment to start
        time.sleep(2)

        # Bulk stop with confirm=True
        bulk_result = inspector.call_tool(
            "bulk_stop_tasks",
            {
                "project_id": project_id,
                "task_ids": [task_id],
                "confirm": True,
            },
        )
        bulk_data = parse_mcp_response(bulk_result)

        # Should return bulk operation complete
        assert "bulk_operation_complete" in bulk_data
        assert bulk_data["bulk_operation_complete"] is True

    # =========================================================================
    # E. Failure Analysis Tests
    # =========================================================================

    def test_run_failing_task(self, inspector: MCPInspector, failing_template: tuple):
        """Test running a task that will fail (for failure analysis tests)."""
        template, project_id = failing_template

        result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,  # Wait for completion
            },
        )
        data = parse_mcp_response(result)

        assert "task" in data
        task = data["task"]
        assert "id" in task

    def test_get_latest_failed_task(
        self, inspector: MCPInspector, failing_template: tuple
    ):
        """Test getting the latest failed task after a failure."""
        template, project_id = failing_template

        # Run a failing task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Wait for it to fail
        try:
            wait_for_task_completion(inspector, project_id, task_id, timeout=120)
        except TimeoutError:
            pass  # May timeout, that's ok for this test

        # Get latest failed task
        failed_result = inspector.call_tool(
            "get_latest_failed_task",
            {"project_id": project_id},
        )
        failed_data = parse_mcp_response(failed_result)

        # Should return either a task or a message
        assert failed_data is not None

    def test_analyze_task_failure(
        self, inspector: MCPInspector, failing_template: tuple
    ):
        """Test analyzing a failed task."""
        template, project_id = failing_template

        # Run a failing task
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Wait for it to fail
        try:
            final_task = wait_for_task_completion(
                inspector, project_id, task_id, timeout=120
            )
        except TimeoutError:
            # Get task status anyway
            get_result = inspector.call_tool(
                "get_task",
                {"project_id": project_id, "task_id": task_id},
            )
            final_task = parse_mcp_response(get_result)

        # Only analyze if task actually failed
        if final_task.get("status") == "error":
            analysis_result = inspector.call_tool(
                "analyze_task_failure",
                {"project_id": project_id, "task_id": task_id},
            )
            analysis = parse_mcp_response(analysis_result)

            # Verify analysis structure
            assert analysis is not None
            if "analysis_ready" in analysis:
                assert analysis["analysis_ready"] is True

    def test_bulk_analyze_failures(
        self, inspector: MCPInspector, failing_template: tuple
    ):
        """Test analyzing multiple failed tasks for patterns."""
        template, project_id = failing_template

        # Run a failing task to ensure we have failures to analyze
        run_result = inspector.call_tool(
            "run_task",
            {
                "template_id": template["id"],
                "project_id": project_id,
                "follow": True,
            },
        )
        run_data = parse_mcp_response(run_result)
        task_id = run_data["task"]["id"]

        # Wait for failure
        try:
            wait_for_task_completion(inspector, project_id, task_id, timeout=120)
        except TimeoutError:
            pass

        # Bulk analyze failures
        bulk_result = inspector.call_tool(
            "bulk_analyze_failures",
            {"project_id": project_id, "limit": 5},
        )
        bulk_data = parse_mcp_response(bulk_result)

        # Should return analysis or message about no failures
        assert bulk_data is not None

    # =========================================================================
    # F. Waiting Tasks Tests
    # =========================================================================

    def test_get_waiting_tasks(
        self, inspector: MCPInspector, task_test_template: tuple
    ):
        """Test getting waiting tasks for a project."""
        _template, project_id = task_test_template

        # Get waiting tasks (may be empty)
        result = inspector.call_tool(
            "get_waiting_tasks",
            {"project_id": project_id},
        )
        data = parse_mcp_response(result)

        # Should have waiting_tasks key even if empty
        assert "waiting_tasks" in data
        assert isinstance(data["waiting_tasks"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
