"""
Tests for the EnvironmentTools class functionality.

Tests cover both environment and inventory operations with comprehensive
CRUD testing including error handling scenarios.
"""

import pytest

from semaphore_mcp.tools.environments import EnvironmentTools


class TestEnvironmentTools:
    """Test suite for EnvironmentTools class methods."""

    # Note: environment_tools fixture is provided by conftest.py

    @pytest.mark.asyncio
    async def test_list_environments(self, environment_tools):
        """Test list_environments method."""
        # Define mock return value
        project_id = 1
        mock_environments = [
            {
                "id": 1,
                "name": "Staging",
                "project_id": project_id,
                "json": '{"STAGE": "staging"}',
            },
            {
                "id": 2,
                "name": "Production",
                "project_id": project_id,
                "json": '{"STAGE": "production"}',
            },
        ]
        environment_tools.semaphore.list_environments.return_value = mock_environments

        # Call the method
        result = await environment_tools.list_environments(project_id)

        # Verify the result - expect wrapped response
        assert result == {"environments": mock_environments}
        environment_tools.semaphore.list_environments.assert_called_once_with(
            project_id
        )

    @pytest.mark.asyncio
    async def test_get_environment(self, environment_tools):
        """Test get_environment method."""
        # Define mock return value
        project_id = 1
        environment_id = 42
        mock_environment = {
            "id": environment_id,
            "name": "Production",
            "project_id": project_id,
            "json": '{"STAGE": "production", "DEBUG": "false"}',
        }
        environment_tools.semaphore.get_environment.return_value = mock_environment

        # Call the method
        result = await environment_tools.get_environment(project_id, environment_id)

        # Verify the result
        assert result == mock_environment
        environment_tools.semaphore.get_environment.assert_called_once_with(
            project_id, environment_id
        )

    @pytest.mark.asyncio
    async def test_create_environment(self, environment_tools):
        """Test create_environment method."""
        # Define parameters
        project_id = 1
        name = "Development"
        env_data = {"STAGE": "development", "DEBUG": "true"}
        mock_created = {
            "id": 3,
            "name": "Development",
            "project_id": project_id,
            "json": '{"STAGE": "development", "DEBUG": "true"}',
        }
        environment_tools.semaphore.create_environment.return_value = mock_created

        # Call the method
        result = await environment_tools.create_environment(project_id, name, env_data)

        # Verify the result
        assert result == mock_created
        environment_tools.semaphore.create_environment.assert_called_once_with(
            project_id, name, env_data
        )

    @pytest.mark.asyncio
    async def test_update_environment(self, environment_tools):
        """Test update_environment method."""
        # Define parameters
        project_id = 1
        environment_id = 42
        name = "Updated Env"
        env_data = {"STAGE": "updated", "NEW_VAR": "new-value"}
        mock_updated = {
            "id": environment_id,
            "name": "Updated Env",
            "project_id": project_id,
            "json": '{"STAGE": "updated", "NEW_VAR": "new-value"}',
        }
        environment_tools.semaphore.update_environment.return_value = mock_updated

        # Call the method
        result = await environment_tools.update_environment(
            project_id, environment_id, name, env_data
        )

        # Verify the result
        assert result == mock_updated
        environment_tools.semaphore.update_environment.assert_called_once_with(
            project_id, environment_id, name, env_data
        )

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
        environment_tools.semaphore.delete_environment.assert_called_once_with(
            project_id, environment_id
        )

    @pytest.mark.asyncio
    async def test_list_inventory(self, environment_tools):
        """Test list_inventory method."""
        # Define mock return value
        project_id = 1
        mock_inventory = [
            {
                "id": 1,
                "name": "Web Servers",
                "project_id": project_id,
                "type": "file",
                "inventory": "[webservers]\n192.168.1.10\n192.168.1.11",
            },
            {
                "id": 2,
                "name": "DB Servers",
                "project_id": project_id,
                "type": "file",
                "inventory": "[databases]\n192.168.1.20\n192.168.1.21",
            },
        ]
        environment_tools.semaphore.list_inventory.return_value = mock_inventory

        # Call the method
        result = await environment_tools.list_inventory(project_id)

        # Verify the result - expect wrapped response
        assert result == {"inventory": mock_inventory}
        environment_tools.semaphore.list_inventory.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_inventory(self, environment_tools):
        """Test get_inventory method."""
        # Define mock return value
        project_id = 1
        inventory_id = 42
        mock_inventory = {
            "id": inventory_id,
            "name": "Web Servers",
            "project_id": project_id,
            "type": "file",
            "inventory": "[webservers]\n192.168.1.10\n192.168.1.11\n\n[databases]\n192.168.1.20",
        }
        environment_tools.semaphore.get_inventory.return_value = mock_inventory

        # Call the method
        result = await environment_tools.get_inventory(project_id, inventory_id)

        # Verify the result
        assert result == mock_inventory
        environment_tools.semaphore.get_inventory.assert_called_once_with(
            project_id, inventory_id
        )

    @pytest.mark.asyncio
    async def test_create_inventory(self, environment_tools):
        """Test create_inventory method."""
        # Define parameters
        project_id = 1
        name = "Test Inventory"
        inventory_data = (
            "[webservers]\n192.168.1.10\n192.168.1.11\n\n[databases]\n192.168.1.20"
        )
        mock_created = {
            "id": 3,
            "name": "Test Inventory",
            "project_id": project_id,
            "type": "file",
            "inventory": inventory_data,
        }
        environment_tools.semaphore.create_inventory.return_value = mock_created

        # Call the method
        result = await environment_tools.create_inventory(
            project_id, name, inventory_data
        )

        # Verify the result
        assert result == mock_created
        environment_tools.semaphore.create_inventory.assert_called_once_with(
            project_id, name, inventory_data
        )

    @pytest.mark.asyncio
    async def test_update_inventory(self, environment_tools):
        """Test update_inventory method."""
        # Define parameters
        project_id = 1
        inventory_id = 42
        name = "Updated Inventory"
        inventory_data = (
            "[updated-webservers]\nlocalhost\n\n[updated-databases]\n127.0.0.1"
        )
        mock_updated = {
            "id": inventory_id,
            "name": "Updated Inventory",
            "project_id": project_id,
            "type": "file",
            "inventory": inventory_data,
        }
        environment_tools.semaphore.update_inventory.return_value = mock_updated

        # Call the method
        result = await environment_tools.update_inventory(
            project_id, inventory_id, name, inventory_data
        )

        # Verify the result
        assert result == mock_updated
        environment_tools.semaphore.update_inventory.assert_called_once_with(
            project_id, inventory_id, name, inventory_data
        )

    @pytest.mark.asyncio
    async def test_delete_inventory(self, environment_tools):
        """Test delete_inventory method."""
        # Define mock return value
        project_id = 1
        inventory_id = 42
        mock_result = {"message": "Inventory deleted"}
        environment_tools.semaphore.delete_inventory.return_value = mock_result

        # Call the method
        result = await environment_tools.delete_inventory(project_id, inventory_id)

        # Verify the result
        assert result == mock_result
        environment_tools.semaphore.delete_inventory.assert_called_once_with(
            project_id, inventory_id
        )

    # Error handling tests

    @pytest.mark.asyncio
    async def test_list_environments_error(self, environment_tools):
        """Test list_environments method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        environment_tools.semaphore.list_environments.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await environment_tools.list_environments(project_id)

        # Verify the error message
        assert "Error during listing environments" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_create_environment_error(self, environment_tools):
        """Test create_environment method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        name = "Test Env"
        env_data = {"VAR": "value"}
        environment_tools.semaphore.create_environment.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await environment_tools.create_environment(project_id, name, env_data)

        # Verify the error message
        assert "Error during creating environment 'Test Env'" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_environment_partial(self, environment_tools):
        """Test update_environment method with partial update (name only)."""
        # Define parameters
        project_id = 1
        environment_id = 42
        name = "Updated Name Only"
        mock_updated = {
            "id": environment_id,
            "name": "Updated Name Only",
            "project_id": project_id,
        }
        environment_tools.semaphore.update_environment.return_value = mock_updated

        # Call the method with only name
        result = await environment_tools.update_environment(
            project_id, environment_id, name=name
        )

        # Verify the result
        assert result == mock_updated
        environment_tools.semaphore.update_environment.assert_called_once_with(
            project_id, environment_id, name, None
        )

    @pytest.mark.asyncio
    async def test_update_inventory_partial(self, environment_tools):
        """Test update_inventory method with partial update (inventory data only)."""
        # Define parameters
        project_id = 1
        inventory_id = 42
        inventory_data = "[updated]\nlocalhost"
        mock_updated = {
            "id": inventory_id,
            "project_id": project_id,
            "inventory": inventory_data,
        }
        environment_tools.semaphore.update_inventory.return_value = mock_updated

        # Call the method with only inventory data
        result = await environment_tools.update_inventory(
            project_id, inventory_id, inventory_data=inventory_data
        )

        # Verify the result
        assert result == mock_updated
        environment_tools.semaphore.update_inventory.assert_called_once_with(
            project_id, inventory_id, None, inventory_data
        )

    @pytest.mark.asyncio
    async def test_list_inventory_error(self, environment_tools):
        """Test list_inventory method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        environment_tools.semaphore.list_inventory.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await environment_tools.list_inventory(project_id)

        # Verify the error message
        assert "Error during listing inventory" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_create_inventory_error(self, environment_tools):
        """Test create_inventory method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        name = "Test Inventory"
        inventory_data = "[test]\nlocalhost"
        environment_tools.semaphore.create_inventory.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await environment_tools.create_inventory(project_id, name, inventory_data)

        # Verify the error message
        assert "Error during creating inventory 'Test Inventory'" in str(excinfo.value)
