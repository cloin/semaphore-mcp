"""
Tests for the MCP server implementation.

These tests verify that the MCP server correctly integrates with SemaphoreUI.
"""

import json
import os
import pytest
import pytest_asyncio
from semaphore_mcp.server import MCPServer


class TestMCPServer:
    """Test suite for MCP server functionality."""

    @pytest_asyncio.fixture
    async def server(self):
        """Create an MCP server instance for testing."""
        base_url = os.environ.get("SEMAPHORE_URL", "http://localhost:3000")
        token = os.environ.get("SEMAPHORE_API_TOKEN")
        
        if not token:
            pytest.skip("No API token available for testing")
            
        return MCPServer(base_url, token)

    @pytest.mark.asyncio
    async def test_tools_list(self, server):
        """Test the tools/list endpoint."""
        # Create a tools/list request
        request = {
            "type": "request",
            "method": "tools/list",
            "id": "test-1"
        }
        
        # Send the request to the server
        response_str = await server.handle_message(json.dumps(request))
        response = json.loads(response_str)
        
        # Verify the response structure
        assert response["type"] == "response"
        assert response["success"] is True
        assert response["id"] == "test-1"
        assert "tools" in response["result"]
        assert isinstance(response["result"]["tools"], list)
        
        # Verify that all expected tools are in the response
        tool_names = response["result"]["tools"]
        expected_tools = {
            # Core tools
            "list_projects", 
            "get_project", 
            "list_templates", 
            "get_template",
            "list_tasks", 
            "get_task", 
            "run_task", 
            "get_task_output",
            # Environment tools
            "list_environments",
            "get_environment",
            "create_environment",
            "update_environment",
            "delete_environment",
            # Inventory tools
            "list_inventory",
            "get_inventory",
            "create_inventory",
            "update_inventory",
            "delete_inventory"
        }
        
        assert all(tool in tool_names for tool in expected_tools)

    @pytest.mark.asyncio
    async def test_call_list_projects(self, server):
        """Test calling the list_projects tool."""
        # Create a tools/call request for list_projects
        request = {
            "type": "request",
            "method": "tools/call",
            "id": "test-2",
            "params": {
                "name": "list_projects",
                "arguments": {}
            }
        }
        
        # Send the request to the server
        response_str = await server.handle_message(json.dumps(request))
        response = json.loads(response_str)
        
        # Verify the response structure
        assert response["type"] == "response"
        assert response["success"] is True
        assert response["id"] == "test-2"
        assert "content" in response["result"]
        
        # Get the content as JSON
        content_text = response["result"]["content"][0]["text"]
        projects_data = json.loads(content_text)
        
        # Verify it's a list (even if empty)
        assert isinstance(projects_data, list)

    @pytest.mark.asyncio
    async def test_invalid_tool_call(self, server):
        """Test calling a nonexistent tool."""
        # Create a tools/call request for a nonexistent tool
        request = {
            "type": "request",
            "method": "tools/call",
            "id": "test-3",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
        
        # Send the request to the server
        response_str = await server.handle_message(json.dumps(request))
        response = json.loads(response_str)
        
        # Verify the error response structure
        assert response["type"] == "response"
        assert response["success"] is False
        assert response["id"] == "test-3"
        assert "error" in response
        assert "code" in response["error"]
        assert "message" in response["error"]
        assert "invalid_params" == response["error"]["code"]
        
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Environment API integration currently unstable")
    async def test_environment_tools(self, server):
        """Test environment management tools."""
        # First get a project ID to work with
        projects_request = {
            "type": "request",
            "method": "tools/call",
            "id": "env-test-1",
            "params": {
                "name": "list_projects",
                "arguments": {}
            }
        }
        
        projects_response_str = await server.handle_message(json.dumps(projects_request))
        projects_response = json.loads(projects_response_str)
        
        if not projects_response["success"]:
            pytest.skip("Failed to get projects")
            
        # Extract the content as JSON
        content_text = projects_response["result"]["content"][0]["text"]
        projects_data = json.loads(content_text)
        
        if not projects_data:
            pytest.skip("No projects available for environment tests")
        
        project_id = projects_data[0]["id"]
        
        # Test list_environments
        list_env_request = {
            "type": "request",
            "method": "tools/call",
            "id": "env-test-2",
            "params": {
                "name": "list_environments",
                "arguments": {"project_id": project_id}
            }
        }
        
        list_env_response_str = await server.handle_message(json.dumps(list_env_request))
        list_env_response = json.loads(list_env_response_str)
        
        assert list_env_response["success"] is True
        
        # Test create_environment
        import uuid
        test_env_name = f"test-env-{uuid.uuid4().hex[:8]}"
        test_env_data = {"TEST_VAR": "test_value"}
        
        create_env_request = {
            "type": "request",
            "method": "tools/call",
            "id": "env-test-3",
            "params": {
                "name": "create_environment",
                "arguments": {
                    "project_id": project_id,
                    "name": test_env_name,
                    "env_data": test_env_data
                }
            }
        }
        
        create_env_response_str = await server.handle_message(json.dumps(create_env_request))
        create_env_response = json.loads(create_env_response_str)
        
        assert create_env_response["success"] is True
        content_text = create_env_response["result"]["content"][0]["text"]
        env_data = json.loads(content_text)
        env_id = env_data["id"]
        
        # Test get_environment
        get_env_request = {
            "type": "request",
            "method": "tools/call",
            "id": "env-test-4",
            "params": {
                "name": "get_environment",
                "arguments": {
                    "project_id": project_id,
                    "environment_id": env_id
                }
            }
        }
        
        get_env_response_str = await server.handle_message(json.dumps(get_env_request))
        get_env_response = json.loads(get_env_response_str)
        
        assert get_env_response["success"] is True
        
        # Cleanup: Delete the test environment
        delete_env_request = {
            "type": "request",
            "method": "tools/call",
            "id": "env-test-5",
            "params": {
                "name": "delete_environment",
                "arguments": {
                    "project_id": project_id,
                    "environment_id": env_id
                }
            }
        }
        
        delete_env_response_str = await server.handle_message(json.dumps(delete_env_request))
        delete_env_response = json.loads(delete_env_response_str)
        
        assert delete_env_response["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Inventory API integration currently unstable")
    async def test_inventory_tools(self, server):
        """Test inventory management tools."""
        # First get a project ID to work with
        projects_request = {
            "type": "request",
            "method": "tools/call",
            "id": "inv-test-1",
            "params": {
                "name": "list_projects",
                "arguments": {}
            }
        }
        
        projects_response_str = await server.handle_message(json.dumps(projects_request))
        projects_response = json.loads(projects_response_str)
        
        if not projects_response["success"]:
            pytest.skip("Failed to get projects")
            
        # Extract the content as JSON
        content_text = projects_response["result"]["content"][0]["text"]
        projects_data = json.loads(content_text)
        
        if not projects_data:
            pytest.skip("No projects available for inventory tests")
        
        project_id = projects_data[0]["id"]
        
        # Test list_inventory
        list_inv_request = {
            "type": "request",
            "method": "tools/call",
            "id": "inv-test-2",
            "params": {
                "name": "list_inventory",
                "arguments": {"project_id": project_id}
            }
        }
        
        list_inv_response_str = await server.handle_message(json.dumps(list_inv_request))
        list_inv_response = json.loads(list_inv_response_str)
        
        assert list_inv_response["success"] is True
        
        # Test create_inventory
        import uuid
        test_inv_name = f"test-inv-{uuid.uuid4().hex[:8]}"
        test_inv_data = "[webservers]\nlocalhost ansible_connection=local"
        
        create_inv_request = {
            "type": "request",
            "method": "tools/call",
            "id": "inv-test-3",
            "params": {
                "name": "create_inventory",
                "arguments": {
                    "project_id": project_id,
                    "name": test_inv_name,
                    "inventory_data": test_inv_data
                }
            }
        }
        
        create_inv_response_str = await server.handle_message(json.dumps(create_inv_request))
        create_inv_response = json.loads(create_inv_response_str)
        
        assert create_inv_response["success"] is True
        content_text = create_inv_response["result"]["content"][0]["text"]
        inv_data = json.loads(content_text)
        inv_id = inv_data["id"]
        
        # Test get_inventory
        get_inv_request = {
            "type": "request",
            "method": "tools/call",
            "id": "inv-test-4",
            "params": {
                "name": "get_inventory",
                "arguments": {
                    "project_id": project_id,
                    "inventory_id": inv_id
                }
            }
        }
        
        get_inv_response_str = await server.handle_message(json.dumps(get_inv_request))
        get_inv_response = json.loads(get_inv_response_str)
        
        assert get_inv_response["success"] is True
        
        # Cleanup: Delete the test inventory
        delete_inv_request = {
            "type": "request",
            "method": "tools/call",
            "id": "inv-test-5",
            "params": {
                "name": "delete_inventory",
                "arguments": {
                    "project_id": project_id,
                    "inventory_id": inv_id
                }
            }
        }
        
        delete_inv_response_str = await server.handle_message(json.dumps(delete_inv_request))
        delete_inv_response = json.loads(delete_inv_response_str)
        
        assert delete_inv_response["success"] is True
