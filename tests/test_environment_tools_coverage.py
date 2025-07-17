"""
Additional tests for EnvironmentTools to improve coverage.
These tests focus on error paths and edge cases.
"""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from semaphore_mcp.tools.environments import EnvironmentTools


class TestEnvironmentToolsCoverage:
    """Additional coverage tests for EnvironmentTools."""

    @pytest_asyncio.fixture
    async def env_tools(self):
        """Create EnvironmentTools instance with mock semaphore client."""
        mock_semaphore = MagicMock()
        return EnvironmentTools(mock_semaphore)

    @pytest.mark.asyncio
    async def test_list_environments_error_handling(self, env_tools):
        """Test list_environments error handling."""
        env_tools.semaphore.list_environments.side_effect = RuntimeError("API Error")

        with pytest.raises(RuntimeError):
            await env_tools.list_environments(1)

    @pytest.mark.asyncio
    async def test_get_environment_error_handling(self, env_tools):
        """Test get_environment error handling."""
        env_tools.semaphore.get_environment.side_effect = RuntimeError(
            "Environment not found"
        )

        with pytest.raises(RuntimeError):
            await env_tools.get_environment(1, 1)

    @pytest.mark.asyncio
    async def test_create_environment_error_handling(self, env_tools):
        """Test create_environment error handling."""
        env_tools.semaphore.create_environment.side_effect = RuntimeError(
            "Creation failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.create_environment(1, "test", {"VAR": "value"})

    @pytest.mark.asyncio
    async def test_update_environment_name_only_error(self, env_tools):
        """Test update_environment error handling with name only."""
        env_tools.semaphore.update_environment.side_effect = RuntimeError(
            "Update failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.update_environment(1, 1, "new_name")

    @pytest.mark.asyncio
    async def test_update_environment_data_only_error(self, env_tools):
        """Test update_environment error handling with data only."""
        env_tools.semaphore.update_environment.side_effect = RuntimeError(
            "Update failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.update_environment(1, 1, env_data={"VAR": "value"})

    @pytest.mark.asyncio
    async def test_update_environment_both_error(self, env_tools):
        """Test update_environment error handling with both name and data."""
        env_tools.semaphore.update_environment.side_effect = RuntimeError(
            "Update failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.update_environment(1, 1, "new_name", {"VAR": "value"})

    @pytest.mark.asyncio
    async def test_delete_environment_error_handling(self, env_tools):
        """Test delete_environment error handling."""
        env_tools.semaphore.delete_environment.side_effect = RuntimeError(
            "Deletion failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.delete_environment(1, 1)

    @pytest.mark.asyncio
    async def test_list_inventory_error_handling(self, env_tools):
        """Test list_inventory error handling."""
        env_tools.semaphore.list_inventory.side_effect = RuntimeError("API Error")

        with pytest.raises(RuntimeError):
            await env_tools.list_inventory(1)

    @pytest.mark.asyncio
    async def test_get_inventory_error_handling(self, env_tools):
        """Test get_inventory error handling."""
        env_tools.semaphore.get_inventory.side_effect = RuntimeError(
            "Inventory not found"
        )

        with pytest.raises(RuntimeError):
            await env_tools.get_inventory(1, 1)

    @pytest.mark.asyncio
    async def test_create_inventory_error_handling(self, env_tools):
        """Test create_inventory error handling."""
        env_tools.semaphore.create_inventory.side_effect = RuntimeError(
            "Creation failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.create_inventory(1, "test", "[webservers]\nlocalhost")

    @pytest.mark.asyncio
    async def test_update_inventory_name_only_error(self, env_tools):
        """Test update_inventory error handling with name only."""
        env_tools.semaphore.update_inventory.side_effect = RuntimeError("Update failed")

        with pytest.raises(RuntimeError):
            await env_tools.update_inventory(1, 1, "new_name")

    @pytest.mark.asyncio
    async def test_update_inventory_data_only_error(self, env_tools):
        """Test update_inventory error handling with data only."""
        env_tools.semaphore.update_inventory.side_effect = RuntimeError("Update failed")

        with pytest.raises(RuntimeError):
            await env_tools.update_inventory(
                1, 1, inventory_data="[webservers]\nlocalhost"
            )

    @pytest.mark.asyncio
    async def test_update_inventory_both_error(self, env_tools):
        """Test update_inventory error handling with both name and data."""
        env_tools.semaphore.update_inventory.side_effect = RuntimeError("Update failed")

        with pytest.raises(RuntimeError):
            await env_tools.update_inventory(
                1, 1, "new_name", "[webservers]\nlocalhost"
            )

    @pytest.mark.asyncio
    async def test_delete_inventory_error_handling(self, env_tools):
        """Test delete_inventory error handling."""
        env_tools.semaphore.delete_inventory.side_effect = RuntimeError(
            "Deletion failed"
        )

        with pytest.raises(RuntimeError):
            await env_tools.delete_inventory(1, 1)

    @pytest.mark.asyncio
    async def test_update_environment_optional_parameters_none(self, env_tools):
        """Test update_environment with None parameters (edge case)."""
        env_tools.semaphore.update_environment.return_value = {"id": 1, "name": "test"}

        result = await env_tools.update_environment(1, 1, None, None)

        assert result["id"] == 1
        # Verify the call was made with None values
        env_tools.semaphore.update_environment.assert_called_once_with(1, 1, None, None)

    @pytest.mark.asyncio
    async def test_update_inventory_optional_parameters_none(self, env_tools):
        """Test update_inventory with None parameters (edge case)."""
        env_tools.semaphore.update_inventory.return_value = {"id": 1, "name": "test"}

        result = await env_tools.update_inventory(1, 1, None, None)

        assert result["id"] == 1
        # Verify the call was made with None values
        env_tools.semaphore.update_inventory.assert_called_once_with(1, 1, None, None)

    @pytest.mark.asyncio
    async def test_create_environment_empty_data(self, env_tools):
        """Test create_environment with empty env_data."""
        env_tools.semaphore.create_environment.return_value = {"id": 1, "name": "test"}

        result = await env_tools.create_environment(1, "test", {})

        assert result["id"] == 1
        env_tools.semaphore.create_environment.assert_called_once_with(1, "test", {})

    @pytest.mark.asyncio
    async def test_create_inventory_empty_data(self, env_tools):
        """Test create_inventory with empty inventory_data."""
        env_tools.semaphore.create_inventory.return_value = {"id": 1, "name": "test"}

        result = await env_tools.create_inventory(1, "test", "")

        assert result["id"] == 1
        env_tools.semaphore.create_inventory.assert_called_once_with(1, "test", "")

    @pytest.mark.asyncio
    async def test_environment_tools_inheritance(self, env_tools):
        """Test that EnvironmentTools properly inherits from BaseTool."""
        # Verify the handle_error method exists and is callable
        assert hasattr(env_tools, "handle_error")
        assert callable(env_tools.handle_error)

        # Verify semaphore client is stored
        assert hasattr(env_tools, "semaphore")
        assert env_tools.semaphore is not None

    @pytest.mark.asyncio
    async def test_successful_operations_coverage(self, env_tools):
        """Test successful operations to ensure all code paths are covered."""
        # Test successful environment operations
        env_tools.semaphore.list_environments.return_value = [{"id": 1, "name": "test"}]
        env_tools.semaphore.get_environment.return_value = {"id": 1, "name": "test"}
        env_tools.semaphore.create_environment.return_value = {"id": 1, "name": "test"}
        env_tools.semaphore.update_environment.return_value = {
            "id": 1,
            "name": "updated",
        }
        env_tools.semaphore.delete_environment.return_value = {"status": "deleted"}

        # Test successful inventory operations
        env_tools.semaphore.list_inventory.return_value = [{"id": 1, "name": "test"}]
        env_tools.semaphore.get_inventory.return_value = {"id": 1, "name": "test"}
        env_tools.semaphore.create_inventory.return_value = {"id": 1, "name": "test"}
        env_tools.semaphore.update_inventory.return_value = {"id": 1, "name": "updated"}
        env_tools.semaphore.delete_inventory.return_value = {"status": "deleted"}

        # Execute all operations to ensure they work
        await env_tools.list_environments(1)
        await env_tools.get_environment(1, 1)
        await env_tools.create_environment(1, "test", {"VAR": "value"})
        await env_tools.update_environment(1, 1, "updated", {"VAR": "new_value"})
        await env_tools.delete_environment(1, 1)

        await env_tools.list_inventory(1)
        await env_tools.get_inventory(1, 1)
        await env_tools.create_inventory(1, "test", "[webservers]\nlocalhost")
        await env_tools.update_inventory(
            1, 1, "updated", "[webservers]\nlocalhost\nserver2"
        )
        await env_tools.delete_inventory(1, 1)

        # Verify all calls were made
        env_tools.semaphore.list_environments.assert_called_once()
        env_tools.semaphore.get_environment.assert_called_once()
        env_tools.semaphore.create_environment.assert_called_once()
        env_tools.semaphore.update_environment.assert_called_once()
        env_tools.semaphore.delete_environment.assert_called_once()

        env_tools.semaphore.list_inventory.assert_called_once()
        env_tools.semaphore.get_inventory.assert_called_once()
        env_tools.semaphore.create_inventory.assert_called_once()
        env_tools.semaphore.update_inventory.assert_called_once()
        env_tools.semaphore.delete_inventory.assert_called_once()
