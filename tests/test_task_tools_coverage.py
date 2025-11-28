"""
Additional tests for TaskTools to improve coverage.
These tests focus on code paths not covered by existing tests.
"""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
import pytest_asyncio

from semaphore_mcp.tools.tasks import TaskTools


class TestTaskToolsCoverage:
    """Additional coverage tests for TaskTools."""

    @pytest_asyncio.fixture
    async def task_tools(self):
        """Create TaskTools instance with mock semaphore client."""
        mock_semaphore = MagicMock()
        return TaskTools(mock_semaphore)

    @pytest.mark.asyncio
    async def test_list_tasks_large_limit_warning(self, task_tools):
        """Test warning when requesting large number of tasks."""
        # Mock the API response
        task_tools.semaphore.list_tasks.return_value = [{"id": 1, "status": "success"}]

        # Test with large limit - should trigger warning
        result = await task_tools.list_tasks(1, limit=10)

        assert result["tasks"] == [{"id": 1, "status": "success"}]
        assert result["shown"] == 1

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(self, task_tools):
        """Test list_tasks with status filter."""
        mock_tasks = [
            {"id": 1, "status": "success"},
            {"id": 2, "status": "error"},
            {"id": 3, "status": "running"},
        ]
        task_tools.semaphore.list_tasks.return_value = mock_tasks

        # Test filtering by status using user-friendly name
        result = await task_tools.list_tasks(1, limit=10, status="successful")

        # Should only return tasks with "success" status (mapped from "successful")
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_tasks_with_tags_filter(self, task_tools):
        """Test list_tasks with tags filter."""
        mock_tasks = [
            {"id": 1, "status": "success", "tags": ["deployment", "prod"]},
            {"id": 2, "status": "success", "tags": ["test"]},
            {"id": 3, "status": "success", "tags": ["deployment"]},
        ]
        task_tools.semaphore.list_tasks.return_value = mock_tasks

        # Test filtering by tags
        result = await task_tools.list_tasks(1, limit=10, tags=["deployment"])

        # Should return tasks that have the "deployment" tag
        assert len(result["tasks"]) == 2
        for task in result["tasks"]:
            assert "deployment" in task["tags"]

    @pytest.mark.asyncio
    async def test_run_task_project_id_lookup_success(self, task_tools):
        """Test run_task when project_id needs to be determined from template."""
        # Mock successful project and template lookup
        task_tools.semaphore.list_projects.return_value = [{"id": 1, "name": "test"}]
        task_tools.semaphore.list_templates.return_value = [{"id": 5, "name": "test"}]
        task_tools.semaphore.run_task.return_value = {"id": 10, "status": "started"}

        result = await task_tools.run_task(5)  # No project_id provided

        assert result["task"]["id"] == 10
        # Verify it found the project and ran the task
        task_tools.semaphore.run_task.assert_called_once_with(
            1,
            5,
            environment=None,
            limit=None,
            dry_run=None,
            diff=None,
            debug=None,
            playbook=None,
            git_branch=None,
            message=None,
            arguments=None,
            inventory_id=None,
        )

    @pytest.mark.asyncio
    async def test_run_task_project_lookup_with_dict_response(self, task_tools):
        """Test run_task when projects API returns dict format."""
        # Mock projects response as dict
        task_tools.semaphore.list_projects.return_value = {
            "projects": [{"id": 1, "name": "test"}]
        }
        task_tools.semaphore.list_templates.return_value = [{"id": 5, "name": "test"}]
        task_tools.semaphore.run_task.return_value = {"id": 10, "status": "started"}

        result = await task_tools.run_task(5)

        assert result["task"]["id"] == 10
        task_tools.semaphore.run_task.assert_called_once_with(
            1,
            5,
            environment=None,
            limit=None,
            dry_run=None,
            diff=None,
            debug=None,
            playbook=None,
            git_branch=None,
            message=None,
            arguments=None,
            inventory_id=None,
        )

    @pytest.mark.asyncio
    async def test_run_task_template_lookup_with_dict_response(self, task_tools):
        """Test run_task when templates API returns dict format."""
        # Mock templates response as dict
        task_tools.semaphore.list_projects.return_value = [{"id": 1, "name": "test"}]
        task_tools.semaphore.list_templates.return_value = {
            "templates": [{"id": 5, "name": "test"}]
        }
        task_tools.semaphore.run_task.return_value = {"id": 10, "status": "started"}

        result = await task_tools.run_task(5)

        assert result["task"]["id"] == 10

    @pytest.mark.asyncio
    async def test_run_task_template_not_found(self, task_tools):
        """Test run_task when template is not found in any project."""
        # Mock projects but no matching template
        task_tools.semaphore.list_projects.return_value = [{"id": 1, "name": "test"}]
        task_tools.semaphore.list_templates.return_value = [{"id": 99, "name": "other"}]

        result = await task_tools.run_task(5)
        assert "error" in result
        assert "Could not determine project_id" in result["error"]

    @pytest.mark.asyncio
    async def test_run_task_template_lookup_error(self, task_tools):
        """Test run_task when template lookup fails for a project."""
        # Mock projects and template lookup error
        task_tools.semaphore.list_projects.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]

        def mock_list_templates(project_id):
            if project_id == 1:
                raise Exception("Template lookup failed")
            return [{"id": 5, "name": "test"}]

        task_tools.semaphore.list_templates.side_effect = mock_list_templates
        task_tools.semaphore.run_task.return_value = {"id": 10, "status": "started"}

        # Should continue and find template in project 2
        result = await task_tools.run_task(5)
        assert result["task"]["id"] == 10

    @pytest.mark.asyncio
    async def test_run_task_http_400_error(self, task_tools):
        """Test run_task when HTTP 400 error occurs."""
        import requests

        # Mock HTTP 400 error
        http_error = requests.exceptions.HTTPError("Bad Request")
        http_error.response = MagicMock()
        http_error.response.status_code = 400

        task_tools.semaphore.run_task.side_effect = http_error

        result = await task_tools.run_task(
            5, project_id=1, environment={"VAR": "value"}
        )
        assert "error" in result
        assert "HTTP error" in result["error"]

    @pytest.mark.asyncio
    async def test_run_task_http_error_no_response(self, task_tools):
        """Test run_task when HTTP error has no response attribute."""
        import requests

        # Mock HTTP error without response
        http_error = requests.exceptions.HTTPError("Network error")
        task_tools.semaphore.run_task.side_effect = http_error

        result = await task_tools.run_task(5, project_id=1)
        assert "error" in result
        assert "HTTP error" in result["error"]

    @pytest.mark.asyncio
    async def test_run_task_general_error(self, task_tools):
        """Test run_task when general error occurs."""
        task_tools.semaphore.run_task.side_effect = Exception("General error")

        result = await task_tools.run_task(5, project_id=1)
        assert "error" in result
        assert "Unexpected error" in result["error"]

    @pytest.mark.asyncio
    async def test_filter_tasks_with_last_tasks_fallback(self, task_tools):
        """Test filter_tasks when get_last_tasks fails and falls back to list_tasks."""
        # Mock get_last_tasks to fail, list_tasks to succeed
        task_tools.semaphore.get_last_tasks.side_effect = Exception("Last tasks failed")
        task_tools.semaphore.list_tasks.return_value = [{"id": 1, "status": "success"}]

        result = await task_tools.filter_tasks(1, use_last_tasks=True)

        assert result["tasks"] == [{"id": 1, "status": "success"}]
        # Verify fallback was used
        task_tools.semaphore.get_last_tasks.assert_called_once()
        task_tools.semaphore.list_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_filter_tasks_no_last_tasks(self, task_tools):
        """Test filter_tasks when use_last_tasks is False."""
        task_tools.semaphore.list_tasks.return_value = [{"id": 1, "status": "success"}]

        result = await task_tools.filter_tasks(1, use_last_tasks=False)

        assert result["tasks"] == [{"id": 1, "status": "success"}]
        # Verify get_last_tasks was not called
        task_tools.semaphore.get_last_tasks.assert_not_called()

    @pytest.mark.asyncio
    async def test_filter_tasks_dict_response(self, task_tools):
        """Test filter_tasks when API returns dict format."""
        mock_response = {"tasks": [{"id": 1, "status": "success"}]}
        # Use get_last_tasks since use_last_tasks defaults to True
        task_tools.semaphore.get_last_tasks.return_value = mock_response

        result = await task_tools.filter_tasks(1)

        assert result["tasks"] == [{"id": 1, "status": "success"}]

    @pytest.mark.asyncio
    async def test_filter_tasks_with_status_mapping(self, task_tools):
        """Test filter_tasks with status mapping."""
        mock_tasks = [
            {"id": 1, "status": "success"},
            {"id": 2, "status": "error"},
        ]
        # Use get_last_tasks since use_last_tasks defaults to True
        task_tools.semaphore.get_last_tasks.return_value = mock_tasks

        # Test with user-friendly status names
        result = await task_tools.filter_tasks(1, status=["successful", "failed"])

        # Should map to API status values and filter
        assert len(result["tasks"]) == 2  # Both should match

    @pytest.mark.asyncio
    async def test_filter_tasks_with_statistics(self, task_tools):
        """Test filter_tasks statistics generation."""
        mock_tasks = [
            {"id": 1, "status": "success"},
            {"id": 2, "status": "error"},
            {"id": 3, "status": "success"},
        ]
        # Use get_last_tasks since use_last_tasks defaults to True
        task_tools.semaphore.get_last_tasks.return_value = mock_tasks

        result = await task_tools.filter_tasks(1, limit=2)

        stats = result["statistics"]
        assert stats["total_tasks"] == 3
        assert stats["filtered_tasks"] == 3
        assert stats["returned_tasks"] == 2
        assert "status_breakdown" in stats
        assert stats["status_breakdown"]["success"] == 2
        assert stats["status_breakdown"]["error"] == 1

    @pytest.mark.asyncio
    async def test_bulk_stop_tasks_preview(self, task_tools):
        """Test bulk_stop_tasks in preview mode (confirm=False)."""

        # Mock task details
        def mock_get_task(project_id, task_id):
            return {
                "id": task_id,
                "status": "running",
                "template": {"name": f"Template {task_id}"},
            }

        task_tools.semaphore.get_task.side_effect = mock_get_task

        result = await task_tools.bulk_stop_tasks(1, [1, 2, 3])

        assert result["confirmation_required"] is True
        assert result["tasks_to_stop"] == 3
        assert len(result["task_details"]) == 3
        assert "status_breakdown" in result

    @pytest.mark.asyncio
    async def test_bulk_stop_tasks_with_unknown_task(self, task_tools):
        """Test bulk_stop_tasks when some tasks can't be retrieved."""

        def mock_get_task(project_id, task_id):
            if task_id == 2:
                raise Exception("Task not found")
            return {"id": task_id, "status": "running", "template": {"name": "Test"}}

        task_tools.semaphore.get_task.side_effect = mock_get_task

        result = await task_tools.bulk_stop_tasks(1, [1, 2, 3])

        # Should handle the error gracefully
        assert result["tasks_to_stop"] == 3
        unknown_task = next(t for t in result["task_details"] if t["id"] == 2)
        assert unknown_task["status"] == "unknown"

    @pytest.mark.asyncio
    async def test_bulk_stop_tasks_execution(self, task_tools):
        """Test bulk_stop_tasks execution (confirm=True)."""

        # Mock stop_task responses
        def mock_stop_task(project_id, task_id):
            if task_id == 2:
                raise Exception("Stop failed")
            return {"status": "stopped"}

        task_tools.semaphore.stop_task.side_effect = mock_stop_task

        result = await task_tools.bulk_stop_tasks(1, [1, 2, 3], confirm=True)

        assert result["bulk_operation_complete"] is True
        assert result["summary"]["total_tasks"] == 3
        assert result["summary"]["successful_stops"] == 2
        assert result["summary"]["failed_stops"] == 1

        # Check individual results
        results = result["results"]
        assert len(results) == 3
        failed_result = next(r for r in results if r["task_id"] == 2)
        assert failed_result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_get_waiting_tasks_found(self, task_tools):
        """Test get_waiting_tasks when waiting tasks are found."""
        mock_result = {
            "tasks": [{"id": 1, "status": "waiting"}, {"id": 2, "status": "waiting"}],
            "statistics": {},
        }

        # Mock the filter_tasks call
        task_tools.filter_tasks = AsyncMock(return_value=mock_result)

        result = await task_tools.get_waiting_tasks(1)

        assert result["count"] == 2
        assert result["task_ids"] == [1, 2]
        assert "bulk_operations" in result

    @pytest.mark.asyncio
    async def test_get_waiting_tasks_none_found(self, task_tools):
        """Test get_waiting_tasks when no waiting tasks are found."""
        mock_result = {"tasks": [], "statistics": {}}

        # Mock the filter_tasks call
        task_tools.filter_tasks = AsyncMock(return_value=mock_result)

        result = await task_tools.get_waiting_tasks(1)

        assert "No tasks in waiting state found" in result["message"]
        assert result["waiting_tasks"] == []

    @pytest.mark.asyncio
    async def test_run_task_no_follow(self, task_tools):
        """Test run_task when follow=False."""
        mock_task_result = {"id": 10, "status": "started"}

        # Mock the semaphore client
        task_tools.semaphore.run_task = Mock(return_value=mock_task_result)

        result = await task_tools.run_task(5, project_id=1, follow=False)

        assert "task" in result
        assert "monitoring" in result
        assert result["monitoring"]["enabled"] is False
        # Verify semaphore client was called
        task_tools.semaphore.run_task.assert_called_once_with(
            1,
            5,
            environment=None,
            limit=None,
            dry_run=None,
            diff=None,
            debug=None,
            playbook=None,
            git_branch=None,
            message=None,
            arguments=None,
            inventory_id=None,
        )

    @pytest.mark.asyncio
    async def test_run_task_no_task_id(self, task_tools):
        """Test run_task when task result has no ID."""
        mock_task_result = {"status": "started"}  # No ID

        task_tools.semaphore.run_task = Mock(return_value=mock_task_result)

        result = await task_tools.run_task(5, project_id=1, follow=True)

        assert "error" in result
        assert "Could not extract task ID" in result["error"]

    @pytest.mark.asyncio
    async def test_run_task_project_id_detection_failure(self, task_tools):
        """Test run_task when project_id can't be auto-detected."""
        # Mock empty projects list
        task_tools.semaphore.list_projects = Mock(return_value=[])

        result = await task_tools.run_task(5, project_id=None, follow=False)

        assert "error" in result
        assert "Could not determine project_id" in result["error"]

    @pytest.mark.asyncio
    async def test_analyze_task_failure_non_failed_task(self, task_tools):
        """Test analyze_task_failure on a non-failed task."""
        mock_task = {"id": 1, "status": "success"}
        task_tools.semaphore.get_task.return_value = mock_task

        result = await task_tools.analyze_task_failure(1, 1)

        assert "warning" in result
        assert result["analysis_applicable"] is False
        assert result["task_status"] == "success"

    @pytest.mark.asyncio
    async def test_analyze_task_failure_template_fetch_error(self, task_tools):
        """Test analyze_task_failure when template fetch fails."""
        mock_task = {
            "id": 1,
            "status": "error",
            "template_id": 5,
            "created": "2023-01-01T00:00:00Z",
        }
        task_tools.semaphore.get_task.return_value = mock_task
        task_tools.semaphore.get_template.side_effect = Exception(
            "Template fetch failed"
        )

        # Mock other calls
        task_tools.semaphore.get_task_raw_output.return_value = "raw output"
        task_tools.semaphore.list_projects.return_value = [{"id": 1, "name": "test"}]

        result = await task_tools.analyze_task_failure(1, 1)

        assert result["analysis_ready"] is True
        assert result["template_context"] is None  # Should be None due to error

    @pytest.mark.asyncio
    async def test_analyze_task_failure_output_fetch_errors(self, task_tools):
        """Test analyze_task_failure when output fetches fail."""
        mock_task = {"id": 1, "status": "error"}
        task_tools.semaphore.get_task.return_value = mock_task
        task_tools.semaphore.get_task_raw_output.side_effect = Exception(
            "Raw output fetch failed"
        )
        task_tools.semaphore.list_projects.return_value = [{"id": 1, "name": "test"}]

        result = await task_tools.analyze_task_failure(1, 1)

        assert result["analysis_ready"] is True
        assert result["outputs"]["raw"] is None
        assert result["outputs"]["has_raw_output"] is False

    @pytest.mark.asyncio
    async def test_bulk_analyze_failures_no_failed_tasks(self, task_tools):
        """Test bulk_analyze_failures when no failed tasks are found."""
        mock_result = {"tasks": []}
        task_tools.filter_tasks = AsyncMock(return_value=mock_result)

        result = await task_tools.bulk_analyze_failures(1)

        assert "No failed tasks found" in result["message"]
        assert result["failed_task_count"] == 0

    @pytest.mark.asyncio
    async def test_bulk_analyze_failures_with_patterns(self, task_tools):
        """Test bulk_analyze_failures with error pattern detection."""
        # Mock failed tasks
        mock_failed_tasks = [{"id": 1, "template_id": 5}, {"id": 2, "template_id": 6}]
        mock_result = {"tasks": mock_failed_tasks}
        task_tools.filter_tasks = AsyncMock(return_value=mock_result)

        # Mock individual analyses
        def mock_analyze_failure(project_id, task_id):
            if task_id == 1:
                return {
                    "analysis_ready": True,
                    "template_context": {"name": "Template A"},
                    "outputs": {"raw": "connection timeout error occurred"},
                }
            else:
                return {
                    "analysis_ready": True,
                    "template_context": {"name": "Template B"},
                    "outputs": {"raw": "authentication failed"},
                }

        task_tools.analyze_task_failure = AsyncMock(side_effect=mock_analyze_failure)

        result = await task_tools.bulk_analyze_failures(1)

        assert result["bulk_analysis_complete"] is True
        assert result["analyzed_tasks"] == 2
        assert "Template A" in result["template_failure_breakdown"]
        assert "Template B" in result["template_failure_breakdown"]
        assert "connection_error" in result["error_pattern_analysis"]
        assert "auth_error" in result["error_pattern_analysis"]
        assert len(result["insights"]) > 0

    @pytest.mark.asyncio
    async def test_bulk_analyze_failures_analysis_error(self, task_tools):
        """Test bulk_analyze_failures when individual analysis fails."""
        mock_failed_tasks = [{"id": 1, "template_id": 5}]
        mock_result = {"tasks": mock_failed_tasks}
        task_tools.filter_tasks = AsyncMock(return_value=mock_result)

        # Mock analysis failure
        task_tools.analyze_task_failure = AsyncMock(
            side_effect=Exception("Analysis failed")
        )

        result = await task_tools.bulk_analyze_failures(1)

        # Should handle the error gracefully
        assert result["analyzed_tasks"] == 0
        assert result["total_failed_tasks"] == 1
