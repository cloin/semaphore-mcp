"""
Tests for the MCP server implementation.

These tests verify that the MCP server correctly integrates with SemaphoreUI.
"""

import json
import os
import pytest
import pytest_asyncio
from semaphore_mcp.server import SemaphoreMCPServer


class TestMCPServer:
    """Test suite for MCP server functionality."""

    @pytest_asyncio.fixture
    async def server(self):
        """Create an MCP server instance for testing."""
        base_url = os.environ.get("SEMAPHORE_URL", "http://localhost:3000")
        token = os.environ.get("SEMAPHORE_API_TOKEN")
        
        if not token:
            pytest.skip("No API token available for testing")
            
        return SemaphoreMCPServer(base_url, token)

    @pytest.mark.asyncio
    async def test_tools_list(self, server):
        """Test the tools list."""
        # We've now switched to FastMCP which handles message formatting internally
        # Let's test if the tool methods exist on the server object
        
        # Verify the expected tools are available
        expected_tools = [
            'list_projects',
            'get_project',
            'list_templates',
            'get_template',
            'list_tasks',
            'get_task',
            'run_task',
            'get_task_output',
            'get_latest_failed_task'
        ]
        
        # Check if each expected tool is a callable method on the server
        for tool_name in expected_tools:
            assert hasattr(server, tool_name), f"Tool {tool_name} not found"
            assert callable(getattr(server, tool_name)), f"Tool {tool_name} is not callable"
        
        # Note: Environment and inventory tools are currently disabled in our FastMCP implementation

    @pytest.mark.asyncio
    async def test_call_list_projects(self, server):
        """Test calling the list_projects tool."""
        # With FastMCP, we can test the tool function directly
        
        try:
            # Call the list_projects function on the server
            result = await server.list_projects()
            
            # Verify we got a successful response
            assert isinstance(result, dict) or isinstance(result, list), "Expected result to be a dict or list"
            
            # We should at least have an empty list if no projects exist
            if isinstance(result, list):
                # This could be empty if no projects exist
                pass
            else:
                # Ensure we have some expected keys in the response
                assert any(key in result for key in ['id', 'projects', 'items']), "Expected project data not found in response"                
        except Exception as e:
            pytest.fail(f"Tool execution failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_call_invalid_tool(self, server):
        """Test calling an invalid tool."""
        # With FastMCP, calling non-existent tools should raise an AttributeError
        with pytest.raises((AttributeError, ValueError)):
            # Try to access a non-existent tool
            await getattr(server, "invalid_tool")()
            
    @pytest.mark.asyncio
    async def test_list_tasks_default_limit(self, server):
        """Test list_tasks with default limit of 5."""
        try:
            # Get a project ID to work with
            projects = await server.list_projects()
            if not projects or (isinstance(projects, list) and not projects):
                pytest.skip("No projects available for task tests")
                
            project_id = projects[0]["id"] if isinstance(projects, list) else projects.get("projects", [])[0]["id"] if "projects" in projects else None
            if not project_id:
                pytest.skip("Could not determine project ID")
                
            # Call the list_tasks function with default limit
            result = await server.list_tasks(project_id)
            
            # Verify the response structure
            assert isinstance(result, dict), "Expected result to be a dict"
            assert "tasks" in result, "Expected 'tasks' key in response"
            assert "total" in result, "Expected 'total' key in response"
            assert "shown" in result, "Expected 'shown' key in response"
            assert "note" in result, "Expected 'note' key in response"
            
            # Verify limit is enforced
            assert len(result["tasks"]) <= 5, "Expected at most 5 tasks with default limit"
            
            # Verify shown and total counts
            assert result["shown"] == len(result["tasks"]), "'shown' count should match actual tasks returned"
            assert result["total"] >= result["shown"], "'total' should be at least 'shown'"
            
        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_list_tasks_custom_limit(self, server):
        """Test list_tasks with custom limit."""
        try:
            # Get a project ID to work with
            projects = await server.list_projects()
            if not projects or (isinstance(projects, list) and not projects):
                pytest.skip("No projects available for task tests")
                
            project_id = projects[0]["id"] if isinstance(projects, list) else projects.get("projects", [])[0]["id"] if "projects" in projects else None
            if not project_id:
                pytest.skip("Could not determine project ID")
                
            # Call the list_tasks function with custom limit of 2
            custom_limit = 2
            result = await server.list_tasks(project_id, limit=custom_limit)
            
            # Verify the response structure
            assert isinstance(result, dict), "Expected result to be a dict"
            assert "tasks" in result, "Expected 'tasks' key in response"
            
            # Verify custom limit is enforced
            assert len(result["tasks"]) <= custom_limit, f"Expected at most {custom_limit} tasks"
            
        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_get_latest_failed_task(self, server):
        """Test get_latest_failed_task."""
        try:
            # Get a project ID to work with
            projects = await server.list_projects()
            if not projects or (isinstance(projects, list) and not projects):
                pytest.skip("No projects available for task tests")
                
            project_id = projects[0]["id"] if isinstance(projects, list) else projects.get("projects", [])[0]["id"] if "projects" in projects else None
            if not project_id:
                pytest.skip("Could not determine project ID")
                
            # Call the get_latest_failed_task function
            result = await server.get_latest_failed_task(project_id)
            
            # Verify the response structure
            assert isinstance(result, dict), "Expected result to be a dict"
            
            # Should either have a task or a message saying no failed tasks
            assert "task" in result or "message" in result, "Expected 'task' or 'message' key in response"
            
            # If there's a task, verify it has expected fields
            if "task" in result:
                task = result["task"]
                assert isinstance(task, dict), "Task should be a dictionary"
                assert "status" in task, "Task should have a status field"
                assert task["status"] == "error", "Task status should be 'error'"
                
            # If there's a message, verify it
            if "message" in result:
                assert "No failed tasks found" in result["message"], "Message should indicate no failed tasks found"
                
        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Environment API integration currently unstable")
    async def test_environment_tools(self, server):
        """Test environment management tools."""
        # Get a project ID to work with using the new FastMCP approach
        try:
            projects = await server.list_projects()
            
            # Skip test if we couldn't get projects
            if not projects:
                pytest.skip("No projects available for environment tests")
                
            project_id = projects[0]["id"] if isinstance(projects, list) else projects.get("id")
            
            # Since we're skipping this test anyway, we don't need to implement the rest
            pytest.skip("Environment API tests are currently disabled")
            
        except Exception as e:
            pytest.fail(f"Failed to list projects: {str(e)}")
        
        # Environment tests are already skipped, no need to implement yet
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Inventory API integration currently unstable")
    async def test_inventory_tools(self, server):
        """Test inventory management tools."""
        # Get a project ID to work with using the new FastMCP approach
        try:
            projects = await server.list_projects()
            
            # Skip test if we couldn't get projects
            if not projects:
                pytest.skip("No projects available for inventory tests")
                
            project_id = projects[0]["id"] if isinstance(projects, list) else projects.get("id")
            
            # Since we're skipping this test anyway, we don't need to implement the rest
            pytest.skip("Inventory API tests are currently disabled")
            
        except Exception as e:
            pytest.fail(f"Failed to list projects: {str(e)}")
