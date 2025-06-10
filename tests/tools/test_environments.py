"""
Tests for the EnvironmentTools class functionality.

Note: These tests are skipped since environment and inventory operations
are currently disabled due to API compatibility issues.
"""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock
from semaphore_mcp.tools.environments import EnvironmentTools


class TestEnvironmentTools:
    """Test suite for EnvironmentTools class methods."""
    
    @pytest_asyncio.fixture
    async def environment_tools(self):
        """Create an EnvironmentTools instance with a mock API client."""
        mock_client = MagicMock()
        return EnvironmentTools(mock_client)
    
    @pytest.mark.skip(reason="Environment operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_list_environments(self, environment_tools):
        """Test list_environments method."""
        # Define mock return value
        project_id = 1
        mock_environments = [
            {"id": 1, "name": "Staging", "project_id": project_id},
            {"id": 2, "name": "Production", "project_id": project_id}
        ]
        environment_tools.semaphore.list_environments.return_value = mock_environments
        
        # Call the method
        result = await environment_tools.list_environments(project_id)
        
        # Verify the result
        assert result == mock_environments
        environment_tools.semaphore.list_environments.assert_called_once_with(project_id)
    
    @pytest.mark.skip(reason="Environment operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_get_environment(self, environment_tools):
        """Test get_environment method."""
        # Define mock return value
        project_id = 1
        environment_id = 42
        mock_environment = {"id": environment_id, "name": "Production", "project_id": project_id}
        environment_tools.semaphore.get_environment.return_value = mock_environment
        
        # Call the method
        result = await environment_tools.get_environment(project_id, environment_id)
        
        # Verify the result
        assert result == mock_environment
        environment_tools.semaphore.get_environment.assert_called_once_with(project_id, environment_id)
    
    @pytest.mark.skip(reason="Environment operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_create_environment(self, environment_tools):
        """Test create_environment method."""
        # Define mock return value
        project_id = 1
        environment_data = {"name": "Development", "json": "{\"var1\": \"value1\"}"}
        mock_created = {"id": 3, "name": "Development", "project_id": project_id}
        environment_tools.semaphore.create_environment.return_value = mock_created
        
        # Call the method
        result = await environment_tools.create_environment(project_id, environment_data)
        
        # Verify the result
        assert result == mock_created
        environment_tools.semaphore.create_environment.assert_called_once_with(project_id, environment_data)
    
    @pytest.mark.skip(reason="Environment operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_update_environment(self, environment_tools):
        """Test update_environment method."""
        # Define mock return value
        project_id = 1
        environment_id = 42
        environment_data = {"name": "Updated Env", "json": "{\"var1\": \"new-value\"}"}
        mock_updated = {"id": environment_id, "name": "Updated Env", "project_id": project_id}
        environment_tools.semaphore.update_environment.return_value = mock_updated
        
        # Call the method
        result = await environment_tools.update_environment(project_id, environment_id, environment_data)
        
        # Verify the result
        assert result == mock_updated
        environment_tools.semaphore.update_environment.assert_called_once_with(project_id, environment_id, environment_data)
    
    @pytest.mark.skip(reason="Environment operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_delete_environment(self, environment_tools):
        """Test delete_environment method."""
        # Define mock return value
        project_id = 1
        environment_id = 42
        mock_result = {"message": "Environment deleted"}
        environment_tools.semaphore.delete_environment.return_value = mock_result
        
        # Call the method
        result = await environment_tools.delete_environment(project_id, environment_id)
        
        # Verify the result
        assert result == mock_result
        environment_tools.semaphore.delete_environment.assert_called_once_with(project_id, environment_id)
    
    @pytest.mark.skip(reason="Inventory operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_list_inventory(self, environment_tools):
        """Test list_inventory method."""
        # Define mock return value
        project_id = 1
        mock_inventory = [
            {"id": 1, "name": "Web Servers", "project_id": project_id},
            {"id": 2, "name": "DB Servers", "project_id": project_id}
        ]
        environment_tools.semaphore.list_inventory.return_value = mock_inventory
        
        # Call the method
        result = await environment_tools.list_inventory(project_id)
        
        # Verify the result
        assert result == mock_inventory
        environment_tools.semaphore.list_inventory.assert_called_once_with(project_id)
    
    @pytest.mark.skip(reason="Inventory operations are disabled due to API compatibility issues")
    @pytest.mark.asyncio
    async def test_get_inventory(self, environment_tools):
        """Test get_inventory method."""
        # Define mock return value
        project_id = 1
        inventory_id = 42
        mock_inventory = {"id": inventory_id, "name": "Web Servers", "project_id": project_id}
        environment_tools.semaphore.get_inventory.return_value = mock_inventory
        
        # Call the method
        result = await environment_tools.get_inventory(project_id, inventory_id)
        
        # Verify the result
        assert result == mock_inventory
        environment_tools.semaphore.get_inventory.assert_called_once_with(project_id, inventory_id)
