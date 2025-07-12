"""
Tests for the TaskTools class functionality.
"""
import json
import pytest
import pytest_asyncio
import requests
from unittest.mock import MagicMock, patch, AsyncMock
from semaphore_mcp.tools.tasks import TaskTools


class TestTaskTools:
    """Test suite for TaskTools class methods."""
    
    @pytest_asyncio.fixture
    async def task_tools(self):
        """Create a TaskTools instance with a mock API client."""
        mock_client = MagicMock()
        return TaskTools(mock_client)
    
    @pytest.mark.asyncio
    async def test_list_tasks(self, task_tools):
        """Test list_tasks method with list response."""
        # Define mock return value for the list_tasks API call
        project_id = 1
        limit = 3
        mock_tasks = [
            {"id": 1, "created": "2023-06-01", "status": "success"},
            {"id": 2, "created": "2023-06-02", "status": "error"},
            {"id": 3, "created": "2023-06-03", "status": "success"},
            {"id": 4, "created": "2023-06-04", "status": "running"},
            {"id": 5, "created": "2023-06-05", "status": "waiting"}
        ]
        task_tools.semaphore.list_tasks.return_value = mock_tasks
        
        # Call the method
        result = await task_tools.list_tasks(project_id, limit)
        
        # Verify the result
        assert result["total"] == 5
        assert result["shown"] == 3
        assert len(result["tasks"]) == 3
        # Verify tasks are in reverse chronological order
        assert result["tasks"][0]["id"] == 5
        assert result["tasks"][1]["id"] == 4
        assert result["tasks"][2]["id"] == 3
        
        task_tools.semaphore.list_tasks.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_list_tasks_dict_response(self, task_tools):
        """Test list_tasks method with dict response format."""
        # Define mock return value as a dict with 'tasks' key
        project_id = 1
        mock_tasks_dict = {
            "tasks": [
                {"id": 1, "created": "2023-06-01", "status": "success"},
                {"id": 2, "created": "2023-06-02", "status": "error"}
            ]
        }
        task_tools.semaphore.list_tasks.return_value = mock_tasks_dict
        
        # Call the method
        result = await task_tools.list_tasks(project_id)
        
        # Verify the result
        assert result["total"] == 2
        assert result["shown"] == 2
        assert len(result["tasks"]) == 2
    
    @pytest.mark.asyncio
    async def test_list_tasks_error(self, task_tools):
        """Test list_tasks method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        task_tools.semaphore.list_tasks.side_effect = Exception("API error")
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.list_tasks(project_id)
        
        # Verify the error message
        assert "Error during listing tasks" in str(excinfo.value)
        
    @pytest.mark.asyncio
    async def test_get_latest_failed_task(self, task_tools):
        """Test get_latest_failed_task method."""
        # Define mock return value for the list_tasks API call
        project_id = 1
        mock_tasks = [
            {"id": 1, "created": "2023-06-01", "status": "success"},
            {"id": 2, "created": "2023-06-02", "status": "error"},
            {"id": 3, "created": "2023-06-03", "status": "success"},
            {"id": 4, "created": "2023-06-04", "status": "error"}
        ]
        task_tools.semaphore.list_tasks.return_value = mock_tasks
        
        # Call the method
        result = await task_tools.get_latest_failed_task(project_id)
        
        # Verify the result
        assert "task" in result
        assert result["task"]["id"] == 4
        
        task_tools.semaphore.list_tasks.assert_called_once_with(project_id)
        
    @pytest.mark.asyncio
    async def test_get_latest_failed_task_none_found(self, task_tools):
        """Test get_latest_failed_task method when no failed tasks exist."""
        # Define mock return value with no failed tasks
        project_id = 1
        mock_tasks = [
            {"id": 1, "created": "2023-06-01", "status": "success"},
            {"id": 3, "created": "2023-06-03", "status": "success"}
        ]
        task_tools.semaphore.list_tasks.return_value = mock_tasks
        
        # Call the method
        result = await task_tools.get_latest_failed_task(project_id)
        
        # Verify the result contains a message
        assert "message" in result
        assert "No failed tasks found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_task(self, task_tools):
        """Test get_task method."""
        # Define mock return value
        project_id = 1
        task_id = 42
        mock_task = {"id": task_id, "status": "success", "output": "Task completed"}
        task_tools.semaphore.get_task.return_value = mock_task
        
        # Call the method
        result = await task_tools.get_task(project_id, task_id)
        
        # Verify the result
        assert result == mock_task
        task_tools.semaphore.get_task.assert_called_once_with(project_id, task_id)
        
    @pytest.mark.asyncio
    async def test_get_task_error(self, task_tools):
        """Test get_task method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        task_id = 42
        task_tools.semaphore.get_task.side_effect = Exception("API error")
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.get_task(project_id, task_id)
        
        # Verify the error message
        assert "Error during getting task" in str(excinfo.value)
        
    @pytest.mark.asyncio
    async def test_run_task_with_project_id(self, task_tools):
        """Test run_task method with provided project_id."""
        # Define mock return value
        project_id = 1
        template_id = 42
        environment = {"ENV_VAR": "value"}
        mock_result = {"id": 123, "status": "scheduled"}
        task_tools.semaphore.run_task.return_value = mock_result
        
        # Call the method
        result = await task_tools.run_task(template_id, project_id, environment)
        
        # Verify the result
        assert result == mock_result
        task_tools.semaphore.run_task.assert_called_once_with(project_id, template_id, environment=environment)
    
    @pytest.mark.asyncio
    async def test_run_task_without_project_id(self, task_tools):
        """Test run_task method without project_id (should look it up)."""
        # Set up mocks for project and template lookup
        template_id = 42
        project_id = 1
        
        # Mock list_projects
        mock_projects = [{"id": project_id, "name": "Test Project"}]
        task_tools.semaphore.list_projects.return_value = mock_projects
        
        # Mock list_templates
        mock_templates = [{"id": template_id, "name": "Test Template"}]
        task_tools.semaphore.list_templates.return_value = mock_templates
        
        # Mock run_task
        mock_result = {"id": 123, "status": "scheduled"}
        task_tools.semaphore.run_task.return_value = mock_result
        
        # Call the method without project_id
        result = await task_tools.run_task(template_id)
        
        # Verify the result
        assert result == mock_result
        task_tools.semaphore.list_projects.assert_called_once()
        task_tools.semaphore.list_templates.assert_called_once_with(project_id)
        task_tools.semaphore.run_task.assert_called_once_with(project_id, template_id, environment=None)
    
    @pytest.mark.asyncio
    async def test_run_task_http_error(self, task_tools):
        """Test run_task method with HTTP error."""
        # Set up the mock to raise an HTTP error
        project_id = 1
        template_id = 42
        environment = {"ENV_VAR": "value"}
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 400
        
        # Create an HTTPError with the mock response
        http_error = requests.exceptions.HTTPError("Bad request", response=mock_response)
        task_tools.semaphore.run_task.side_effect = http_error
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.run_task(template_id, project_id, environment)
        
        # Verify the error message
        assert "HTTP error 400" in str(excinfo.value)
        assert "environment variables" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_get_task_output(self, task_tools):
        """Test get_task_output method."""
        # Define mock return value
        project_id = 1
        task_id = 42
        mock_output = {"output": "Task output", "status": "success"}
        task_tools.semaphore.get_task_output.return_value = mock_output
        
        # Call the method
        result = await task_tools.get_task_output(project_id, task_id)
        
        # Verify the result is JSON formatted
        assert result == json.dumps(mock_output, indent=2)
        task_tools.semaphore.get_task_output.assert_called_once_with(project_id, task_id)
        
    @pytest.mark.asyncio
    async def test_get_task_output_error(self, task_tools):
        """Test get_task_output method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        task_id = 42
        task_tools.semaphore.get_task_output.side_effect = Exception("API error")
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.get_task_output(project_id, task_id)
        
        # Verify the error message
        assert "Error during getting output for task" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_filter_tasks(self, task_tools):
        """Test filtering tasks by status."""
        # Mock tasks with different statuses
        mock_tasks = [
            {"id": 1, "created": "2023-06-01", "status": "success"},
            {"id": 2, "created": "2023-06-02", "status": "error"},
            {"id": 3, "created": "2023-06-03", "status": "running"},
            {"id": 4, "created": "2023-06-04", "status": "waiting"},
            {"id": 5, "created": "2023-06-05", "status": "success"}
        ]
        # Mock both get_last_tasks and list_tasks since filter_tasks tries get_last_tasks first
        task_tools.semaphore.get_last_tasks.return_value = mock_tasks
        task_tools.semaphore.list_tasks.return_value = mock_tasks
        
        # Test filtering by success status
        result = await task_tools.filter_tasks(1, status=["successful"], limit=10)
        
        assert "tasks" in result
        assert "statistics" in result
        assert len(result["tasks"]) == 2  # Two successful tasks
        assert result["statistics"]["filtered_tasks"] == 2
        assert result["statistics"]["total_tasks"] == 5
        
        # Test with use_last_tasks=False to use list_tasks
        result2 = await task_tools.filter_tasks(1, status=["successful"], limit=10, use_last_tasks=False)
        assert len(result2["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_stop_task(self, task_tools):
        """Test stopping a task."""
        # Mock stop task response
        task_tools.semaphore.stop_task.return_value = {"status": "stopped", "message": "Task stopped"}
        
        result = await task_tools.stop_task(1, 123)
        
        assert "status" in result
        assert result["status"] == "stopped"
        task_tools.semaphore.stop_task.assert_called_once_with(1, 123)

    @pytest.mark.asyncio
    async def test_bulk_stop_tasks_confirmation(self, task_tools):
        """Test bulk stop tasks requires confirmation."""
        # Mock task details for confirmation
        mock_task = {"id": 123, "status": "running", "template": {"name": "test-template"}}
        task_tools.semaphore.get_task.return_value = mock_task
        
        # Test without confirmation
        result = await task_tools.bulk_stop_tasks(1, [123, 124], confirm=False)
        
        assert "confirmation_required" in result
        assert result["confirmation_required"] is True
        assert result["tasks_to_stop"] == 2

    @pytest.mark.asyncio
    async def test_bulk_stop_tasks_execution(self, task_tools):
        """Test bulk stop tasks execution with confirmation."""
        # Mock responses
        task_tools.semaphore.stop_task.return_value = {"status": "stopped"}
        
        # Test with confirmation
        result = await task_tools.bulk_stop_tasks(1, [123, 124], confirm=True)
        
        assert "bulk_operation_complete" in result
        assert result["bulk_operation_complete"] is True
        assert "summary" in result
        assert result["summary"]["total_tasks"] == 2

    @pytest.mark.asyncio
    async def test_get_waiting_tasks(self, task_tools):
        """Test getting waiting tasks for bulk operations."""
        # Mock the filter_tasks method instead of the underlying API call
        waiting_tasks = [
            {"id": 1, "created": "2023-06-01", "status": "waiting"},
            {"id": 3, "created": "2023-06-03", "status": "waiting"}
        ]
        filter_result = {
            "tasks": waiting_tasks,
            "statistics": {"total_tasks": 3},
            "note": "Test filter result"
        }
        
        # Create a mock for filter_tasks that returns our predefined result
        task_tools.filter_tasks = AsyncMock(return_value=filter_result)
        
        result = await task_tools.get_waiting_tasks(1)
        
        # Verify filter_tasks was called with the right parameters
        task_tools.filter_tasks.assert_called_once_with(1, status=["waiting"], limit=100)
        
        # Check the result contains the expected data
        assert "waiting_tasks" in result
        assert len(result["waiting_tasks"]) == 2
        assert result["count"] == 2
        assert "bulk_operations" in result

    @pytest.mark.asyncio
    async def test_run_task_with_monitoring_no_follow(self, task_tools):
        """Test running a task without monitoring."""
        # Mock task run result
        template_id = 5
        project_id = 1
        task_id = 42
        environment = {"KEY": "VALUE"}
        
        mock_task_result = {
            "id": task_id,
            "status": "waiting",
            "project_id": project_id
        }
        
        # Set up mocks
        task_tools.run_task = AsyncMock(return_value=mock_task_result)
        
        # Run task without monitoring (follow=False)
        result = await task_tools.run_task_with_monitoring(
            template_id=template_id,
            project_id=project_id,
            environment=environment,
            follow=False
        )
        
        # Verify run_task was called but _monitor_task_execution was not
        task_tools.run_task.assert_called_once_with(template_id, project_id, environment)
        assert result == mock_task_result

    @pytest.mark.asyncio
    async def test_run_task_with_monitoring_follow(self, task_tools):
        """Test running a task with monitoring."""
        # Mock task run result
        template_id = 5
        project_id = 1
        task_id = 42
        environment = {"KEY": "VALUE"}
        
        mock_task_result = {
            "id": task_id,
            "status": "waiting",
            "project_id": project_id
        }
        
        mock_monitoring_result = {
            "monitoring_complete": True,
            "total_polls": 3,
            "duration_seconds": 9.5,
            "final_status": "success",
            "status_updates": [
                {"status": "waiting", "timestamp": 1000},
                {"status": "running", "timestamp": 1003},
                {"status": "success", "timestamp": 1006}
            ]
        }
        
        # Set up mocks
        task_tools.run_task = AsyncMock(return_value=mock_task_result)
        task_tools._monitor_task_execution = AsyncMock(return_value=mock_monitoring_result)
        
        # Run task with monitoring (follow=True)
        result = await task_tools.run_task_with_monitoring(
            template_id=template_id,
            project_id=project_id,
            environment=environment,
            follow=True,
            poll_interval=2,
            max_poll_duration=60
        )
        
        # Verify run_task and _monitor_task_execution were called with correct params
        task_tools.run_task.assert_called_once_with(template_id, project_id, environment)
        task_tools._monitor_task_execution.assert_called_once_with(
            project_id, task_id, 2, 60
        )
        
        # Check the result contains both the task and monitoring data
        assert "task_started" in result
        assert "monitoring" in result
        assert result["task_started"] == mock_task_result
        assert result["monitoring"] == mock_monitoring_result

    @pytest.mark.asyncio
    async def test_run_task_with_monitoring_missing_project_id(self, task_tools):
        """Test monitoring with missing project_id in result."""
        # Mock task run result without project_id
        template_id = 5
        task_id = 42
        
        mock_task_result = {"id": task_id, "status": "waiting"}
        
        # Set up mock
        task_tools.run_task = AsyncMock(return_value=mock_task_result)
        
        # Run task with monitoring but no project_id
        result = await task_tools.run_task_with_monitoring(
            template_id=template_id,
            project_id=None, # Missing project_id
            follow=True
        )
        
        # Should return error
        assert "error" in result
        assert "project ID" in result["error"]
        assert "original_result" in result

    @pytest.mark.asyncio
    async def test_get_task_raw_output(self, task_tools):
        """Test get_task_raw_output method."""
        # Define mock return value
        project_id = 1
        task_id = 42
        mock_raw_output = "This is the raw task output\nwith multiple lines\nand error details"
        task_tools.semaphore.get_task_raw_output.return_value = mock_raw_output
        
        # Call the method
        result = await task_tools.get_task_raw_output(project_id, task_id)
        
        # Verify the result
        assert result == mock_raw_output
        task_tools.semaphore.get_task_raw_output.assert_called_once_with(project_id, task_id)

    @pytest.mark.asyncio
    async def test_get_task_raw_output_error(self, task_tools):
        """Test get_task_raw_output method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        task_id = 42
        task_tools.semaphore.get_task_raw_output.side_effect = Exception("API error")
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.get_task_raw_output(project_id, task_id)
        
        # Verify the error message
        assert "Error during getting raw output for task" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_analyze_task_failure(self, task_tools):
        """Test analyze_task_failure method for a failed task."""
        project_id = 1
        task_id = 42
        template_id = 5
        
        # Mock failed task details
        mock_task = {
            "id": task_id,
            "status": "error",
            "created": "2023-06-01T10:00:00Z",
            "started": "2023-06-01T10:01:00Z",
            "ended": "2023-06-01T10:05:00Z",
            "message": "Task failed",
            "template_id": template_id,
            "environment": {"VAR": "value"}
        }
        
        # Mock template context
        mock_template = {
            "id": template_id,
            "name": "Test Template",
            "playbook": "test.yml",
            "arguments": "--check",
            "description": "Test playbook"
        }
        
        # Mock project context
        mock_projects = [{"id": project_id, "name": "Test Project", "repository": "git@github.com/test/repo.git"}]
        
        # Mock outputs
        mock_structured_output = {"output": "Task failed", "status": "error"}
        mock_raw_output = "TASK [test] failed: host unreachable"
        
        # Set up mocks
        task_tools.semaphore.get_task.return_value = mock_task
        task_tools.semaphore.get_template.return_value = mock_template
        task_tools.semaphore.list_projects.return_value = mock_projects
        task_tools.semaphore.get_task_output.return_value = mock_structured_output
        task_tools.semaphore.get_task_raw_output.return_value = mock_raw_output
        
        # Call the method
        result = await task_tools.analyze_task_failure(project_id, task_id)
        
        # Verify the result structure
        assert result["analysis_ready"] is True
        assert result["task_details"]["id"] == task_id
        assert result["task_details"]["status"] == "error"
        assert result["task_details"]["template_id"] == template_id
        
        assert result["project_context"]["id"] == project_id
        assert result["project_context"]["name"] == "Test Project"
        
        assert result["template_context"]["id"] == template_id
        assert result["template_context"]["name"] == "Test Template"
        
        assert result["outputs"]["raw"] == mock_raw_output
        assert result["outputs"]["structured"] == mock_structured_output
        assert result["outputs"]["has_raw_output"] is True
        assert result["outputs"]["has_structured_output"] is True
        
        # Verify analysis guidance is included
        assert "analysis_guidance" in result
        assert "focus_areas" in result["analysis_guidance"]
        assert "common_failure_patterns" in result["analysis_guidance"]

    @pytest.mark.asyncio
    async def test_analyze_task_failure_non_failed_task(self, task_tools):
        """Test analyze_task_failure method for a non-failed task."""
        project_id = 1
        task_id = 42
        
        # Mock successful task
        mock_task = {
            "id": task_id,
            "status": "success",
            "created": "2023-06-01T10:00:00Z"
        }
        
        task_tools.semaphore.get_task.return_value = mock_task
        
        # Call the method
        result = await task_tools.analyze_task_failure(project_id, task_id)
        
        # Should return warning about non-failed task
        assert "warning" in result
        assert "success" in result["warning"]
        assert result["analysis_applicable"] is False

    @pytest.mark.asyncio
    async def test_bulk_analyze_failures(self, task_tools):
        """Test bulk_analyze_failures method."""
        project_id = 1
        
        # Mock failed tasks from filter_tasks
        failed_tasks = [
            {"id": 1, "status": "error"},
            {"id": 2, "status": "error"},
            {"id": 3, "status": "error"}
        ]
        filter_result = {
            "tasks": failed_tasks,
            "statistics": {"total_tasks": 10}
        }
        
        # Mock individual task analyses
        mock_analysis_1 = {
            "analysis_ready": True,
            "template_context": {"name": "Template A"},
            "outputs": {"raw": "connection timeout error"}
        }
        mock_analysis_2 = {
            "analysis_ready": True,
            "template_context": {"name": "Template A"},
            "outputs": {"raw": "authentication failed"}
        }
        mock_analysis_3 = {
            "analysis_ready": True,
            "template_context": {"name": "Template B"},
            "outputs": {"raw": "syntax error in playbook"}
        }
        
        # Set up mocks
        task_tools.filter_tasks = AsyncMock(return_value=filter_result)
        task_tools.analyze_task_failure = AsyncMock(side_effect=[
            mock_analysis_1, mock_analysis_2, mock_analysis_3
        ])
        
        # Call the method
        result = await task_tools.bulk_analyze_failures(project_id, limit=5)
        
        # Verify the result
        assert result["bulk_analysis_complete"] is True
        assert result["analyzed_tasks"] == 3
        assert result["total_failed_tasks"] == 3
        
        # Check template failure breakdown
        assert "template_failure_breakdown" in result
        assert result["template_failure_breakdown"]["Template A"] == 2
        assert result["template_failure_breakdown"]["Template B"] == 1
        
        # Check error pattern analysis
        assert "error_pattern_analysis" in result
        assert result["error_pattern_analysis"]["connection_error"] == 1
        assert result["error_pattern_analysis"]["auth_error"] == 1
        assert result["error_pattern_analysis"]["syntax_error"] == 1
        
        # Check insights
        assert "insights" in result
        assert len(result["insights"]) >= 1
        
        # Check recommendations
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_bulk_analyze_failures_no_failed_tasks(self, task_tools):
        """Test bulk_analyze_failures when no failed tasks exist."""
        project_id = 1
        
        # Mock empty result from filter_tasks
        filter_result = {
            "tasks": [],
            "statistics": {"total_tasks": 5}
        }
        
        task_tools.filter_tasks = AsyncMock(return_value=filter_result)
        
        # Call the method
        result = await task_tools.bulk_analyze_failures(project_id)
        
        # Should return message about no failed tasks
        assert "message" in result
        assert "No failed tasks found" in result["message"]
        assert result["failed_task_count"] == 0
