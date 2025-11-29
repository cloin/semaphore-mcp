"""
Tests for the AccessKeyTools class functionality.

Tests cover access key operations for list and create methods.
Note: get, update, and delete operations are intentionally not exposed
as MCP tools for security reasons (prevent credential exposure and
accidental destructive operations).
"""

import pytest


class TestAccessKeyTools:
    """Test suite for AccessKeyTools class methods."""

    # Note: access_key_tools fixture is provided by conftest.py

    @pytest.mark.asyncio
    async def test_list_access_keys(self, access_key_tools):
        """Test list_access_keys method."""
        project_id = 1
        mock_keys = [
            {"id": 1, "name": "None Key", "project_id": project_id, "type": "none"},
            {"id": 2, "name": "SSH Key", "project_id": project_id, "type": "ssh"},
        ]
        access_key_tools.semaphore.list_access_keys.return_value = mock_keys

        result = await access_key_tools.list_access_keys(project_id)

        assert result == {"access_keys": mock_keys}
        access_key_tools.semaphore.list_access_keys.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_list_access_keys_empty(self, access_key_tools):
        """Test list_access_keys method with empty result."""
        project_id = 1
        access_key_tools.semaphore.list_access_keys.return_value = []

        result = await access_key_tools.list_access_keys(project_id)

        assert result == {"access_keys": []}

    # Create key tests for each type

    @pytest.mark.asyncio
    async def test_create_access_key_none_type(self, access_key_tools):
        """Test create_access_key method with 'none' type (for public repos)."""
        project_id = 1
        name = "Public Repo Key"
        key_type = "none"
        mock_created = {
            "id": 1,
            "name": name,
            "project_id": project_id,
            "type": key_type,
        }
        access_key_tools.semaphore.create_access_key.return_value = mock_created

        result = await access_key_tools.create_access_key(project_id, name, key_type)

        assert result == mock_created
        access_key_tools.semaphore.create_access_key.assert_called_once_with(
            project_id, name, key_type, None, None, None
        )

    @pytest.mark.asyncio
    async def test_create_access_key_ssh_type(self, access_key_tools):
        """Test create_access_key method with 'ssh' type."""
        project_id = 1
        name = "SSH Deploy Key"
        key_type = "ssh"
        login = "git"
        private_key = (
            "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----"
        )
        mock_created = {
            "id": 2,
            "name": name,
            "project_id": project_id,
            "type": key_type,
        }
        access_key_tools.semaphore.create_access_key.return_value = mock_created

        result = await access_key_tools.create_access_key(
            project_id, name, key_type, login=login, private_key=private_key
        )

        assert result == mock_created
        access_key_tools.semaphore.create_access_key.assert_called_once_with(
            project_id, name, key_type, login, None, private_key
        )

    @pytest.mark.asyncio
    async def test_create_access_key_login_password_type(self, access_key_tools):
        """Test create_access_key method with 'login_password' type."""
        project_id = 1
        name = "Service Account"
        key_type = "login_password"
        login = "service_user"
        password = "secret123"
        mock_created = {
            "id": 3,
            "name": name,
            "project_id": project_id,
            "type": key_type,
        }
        access_key_tools.semaphore.create_access_key.return_value = mock_created

        result = await access_key_tools.create_access_key(
            project_id, name, key_type, login=login, password=password
        )

        assert result == mock_created
        access_key_tools.semaphore.create_access_key.assert_called_once_with(
            project_id, name, key_type, login, password, None
        )

    # Error handling tests

    @pytest.mark.asyncio
    async def test_list_access_keys_error(self, access_key_tools):
        """Test list_access_keys method with error."""
        project_id = 1
        access_key_tools.semaphore.list_access_keys.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as excinfo:
            await access_key_tools.list_access_keys(project_id)

        assert "Error during listing access keys" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_create_access_key_error(self, access_key_tools):
        """Test create_access_key method with error."""
        project_id = 1
        name = "Test Key"
        key_type = "none"
        access_key_tools.semaphore.create_access_key.side_effect = Exception(
            "API error"
        )

        with pytest.raises(RuntimeError) as excinfo:
            await access_key_tools.create_access_key(project_id, name, key_type)

        assert "Error during creating access key 'Test Key'" in str(excinfo.value)
