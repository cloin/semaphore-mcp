"""Tests for ProjectUserTools."""

import pytest


class TestProjectUserTools:
    """Test suite for project user tool methods."""

    @pytest.mark.asyncio
    async def test_get_project_role(self, project_user_tools):
        """Test get_project_role method."""
        project_user_tools.semaphore.get_project_role.return_value = {
            "role": "owner",
            "permissions": 0,
        }

        result = await project_user_tools.get_project_role(1)

        assert result == {"role": "owner", "permissions": 0}
        project_user_tools.semaphore.get_project_role.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_list_project_users(self, project_user_tools, sample_project_users):
        """Test list_project_users method."""
        project_user_tools.semaphore.list_project_users.return_value = (
            sample_project_users
        )

        result = await project_user_tools.list_project_users(
            1, sort="username", order="desc"
        )

        assert result == {"users": sample_project_users}
        project_user_tools.semaphore.list_project_users.assert_called_once_with(
            1, "username", "desc"
        )

    @pytest.mark.asyncio
    async def test_add_project_user(self, project_user_tools):
        """Test add_project_user method."""
        project_user_tools.semaphore.add_project_user.return_value = {}

        result = await project_user_tools.add_project_user(1, 2, "guest")

        assert result == {}
        project_user_tools.semaphore.add_project_user.assert_called_once_with(
            1, 2, "guest"
        )

    @pytest.mark.asyncio
    async def test_update_project_user(self, project_user_tools):
        """Test update_project_user method."""
        project_user_tools.semaphore.update_project_user.return_value = {}

        result = await project_user_tools.update_project_user(1, 2, "manager")

        assert result == {}
        project_user_tools.semaphore.update_project_user.assert_called_once_with(
            1, 2, "manager"
        )

    @pytest.mark.asyncio
    async def test_remove_project_user(self, project_user_tools):
        """Test remove_project_user method."""
        project_user_tools.semaphore.remove_project_user.return_value = {}

        result = await project_user_tools.remove_project_user(1, 2)

        assert result == {}
        project_user_tools.semaphore.remove_project_user.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_add_project_user_rejects_invalid_role(self, project_user_tools):
        """Test add_project_user validates role."""
        with pytest.raises(RuntimeError) as excinfo:
            await project_user_tools.add_project_user(1, 2, "admin")

        assert "role must be one of" in str(excinfo.value)
        project_user_tools.semaphore.add_project_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_project_users_rejects_invalid_sort(self, project_user_tools):
        """Test list_project_users validates sort."""
        with pytest.raises(RuntimeError) as excinfo:
            await project_user_tools.list_project_users(1, sort="created")

        assert "sort must be one of" in str(excinfo.value)
        project_user_tools.semaphore.list_project_users.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_project_users_error(self, project_user_tools):
        """Test list_project_users method with error."""
        project_user_tools.semaphore.list_project_users.side_effect = Exception(
            "API error"
        )

        with pytest.raises(RuntimeError) as excinfo:
            await project_user_tools.list_project_users(1)

        assert "Error during listing users" in str(excinfo.value)
