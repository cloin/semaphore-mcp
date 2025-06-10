"""
Tests for the TaskTools class functionality.
"""
import json
import pytest
import pytest_asyncio
import requests
from unittest.mock import MagicMock, patch
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
        task_id = 42
        mock_output = {"output": "Task output", "status": "success"}
        task_tools.semaphore.get_task_output.return_value = mock_output
        
        # Call the method
        result = await task_tools.get_task_output(task_id)
        
        # Verify the result is JSON formatted
        assert result == json.dumps(mock_output, indent=2)
        task_tools.semaphore.get_task_output.assert_called_once_with(task_id)
        
    @pytest.mark.asyncio
    async def test_get_task_output_error(self, task_tools):
        """Test get_task_output method with error."""
        # Set up the mock to raise an exception
        task_id = 42
        task_tools.semaphore.get_task_output.side_effect = Exception("API error")
        
        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await task_tools.get_task_output(task_id)
        
        # Verify the error message
        assert "Error during getting output for task" in str(excinfo.value)
