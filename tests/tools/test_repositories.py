"""
Tests for the RepositoryTools class functionality.

Tests cover repository operations with comprehensive CRUD testing
including error handling scenarios.
"""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from semaphore_mcp.tools.repositories import RepositoryTools


class TestRepositoryTools:
    """Test suite for RepositoryTools class methods."""

    @pytest_asyncio.fixture
    async def repository_tools(self):
        """Create a RepositoryTools instance with a mock API client."""
        mock_client = MagicMock()
        return RepositoryTools(mock_client)

    @pytest.mark.asyncio
    async def test_list_repositories(self, repository_tools):
        """Test list_repositories method."""
        # Define mock return value
        project_id = 1
        mock_repositories = [
            {
                "id": 1,
                "name": "Demo",
                "project_id": project_id,
                "git_url": "https://github.com/semaphoreui/semaphore-demo.git",
                "git_branch": "main",
                "ssh_key_id": 1,
            },
            {
                "id": 2,
                "name": "Production",
                "project_id": project_id,
                "git_url": "https://github.com/example/production.git",
                "git_branch": "master",
                "ssh_key_id": 2,
            },
        ]
        repository_tools.semaphore.list_repositories.return_value = mock_repositories

        # Call the method
        result = await repository_tools.list_repositories(project_id)

        # Verify the result - expect wrapped response
        assert result == {"repositories": mock_repositories}
        repository_tools.semaphore.list_repositories.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_repository(self, repository_tools):
        """Test get_repository method."""
        # Define mock return value
        project_id = 1
        repository_id = 42
        mock_repository = {
            "id": repository_id,
            "name": "Demo",
            "project_id": project_id,
            "git_url": "https://github.com/semaphoreui/semaphore-demo.git",
            "git_branch": "main",
            "ssh_key_id": 1,
        }
        repository_tools.semaphore.get_repository.return_value = mock_repository

        # Call the method
        result = await repository_tools.get_repository(project_id, repository_id)

        # Verify the result
        assert result == mock_repository
        repository_tools.semaphore.get_repository.assert_called_once_with(
            project_id, repository_id
        )

    @pytest.mark.asyncio
    async def test_create_repository(self, repository_tools):
        """Test create_repository method."""
        # Define parameters
        project_id = 1
        name = "Test Repo"
        git_url = "https://github.com/test/repo.git"
        git_branch = "develop"
        ssh_key_id = 3
        mock_created = {
            "id": 3,
            "name": name,
            "project_id": project_id,
            "git_url": git_url,
            "git_branch": git_branch,
            "ssh_key_id": ssh_key_id,
        }
        repository_tools.semaphore.create_repository.return_value = mock_created

        # Call the method
        result = await repository_tools.create_repository(
            project_id, name, git_url, git_branch, ssh_key_id
        )

        # Verify the result
        assert result == mock_created
        repository_tools.semaphore.create_repository.assert_called_once_with(
            project_id, name, git_url, git_branch, ssh_key_id
        )

    @pytest.mark.asyncio
    async def test_update_repository(self, repository_tools):
        """Test update_repository method."""
        # Define parameters
        project_id = 1
        repository_id = 42
        name = "Updated Repo"
        git_url = "https://github.com/test/updated-repo.git"
        git_branch = "staging"
        ssh_key_id = 5
        mock_updated = {
            "id": repository_id,
            "name": name,
            "project_id": project_id,
            "git_url": git_url,
            "git_branch": git_branch,
            "ssh_key_id": ssh_key_id,
        }
        repository_tools.semaphore.update_repository.return_value = mock_updated

        # Call the method
        result = await repository_tools.update_repository(
            project_id, repository_id, name, git_url, git_branch, ssh_key_id
        )

        # Verify the result
        assert result == mock_updated
        repository_tools.semaphore.update_repository.assert_called_once_with(
            project_id, repository_id, name, git_url, git_branch, ssh_key_id
        )

    @pytest.mark.asyncio
    async def test_delete_repository(self, repository_tools):
        """Test delete_repository method."""
        # Define mock return value
        project_id = 1
        repository_id = 42
        mock_result = {"message": "Repository deleted"}
        repository_tools.semaphore.delete_repository.return_value = mock_result

        # Call the method
        result = await repository_tools.delete_repository(project_id, repository_id)

        # Verify the result
        assert result == mock_result
        repository_tools.semaphore.delete_repository.assert_called_once_with(
            project_id, repository_id
        )

    # Error handling tests

    @pytest.mark.asyncio
    async def test_list_repositories_error(self, repository_tools):
        """Test list_repositories method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        repository_tools.semaphore.list_repositories.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await repository_tools.list_repositories(project_id)

        # Verify the error message
        assert "Error during listing repositories" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_create_repository_error(self, repository_tools):
        """Test create_repository method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        name = "Test Repo"
        git_url = "https://github.com/test/repo.git"
        git_branch = "main"
        ssh_key_id = 1
        repository_tools.semaphore.create_repository.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await repository_tools.create_repository(
                project_id, name, git_url, git_branch, ssh_key_id
            )

        # Verify the error message
        assert "Error during creating repository 'Test Repo'" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_repository_error(self, repository_tools):
        """Test get_repository method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        repository_id = 42
        repository_tools.semaphore.get_repository.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await repository_tools.get_repository(project_id, repository_id)

        # Verify the error message
        assert "Error during getting repository 42" in str(excinfo.value)

    # Partial update tests

    @pytest.mark.asyncio
    async def test_update_repository_partial_name(self, repository_tools):
        """Test update_repository method with partial update (name only)."""
        # Define parameters
        project_id = 1
        repository_id = 42
        name = "Updated Name Only"
        mock_updated = {
            "id": repository_id,
            "name": name,
            "project_id": project_id,
        }
        repository_tools.semaphore.update_repository.return_value = mock_updated

        # Call the method with only name
        result = await repository_tools.update_repository(
            project_id, repository_id, name=name
        )

        # Verify the result
        assert result == mock_updated
        repository_tools.semaphore.update_repository.assert_called_once_with(
            project_id, repository_id, name, None, None, None
        )

    @pytest.mark.asyncio
    async def test_update_repository_partial_branch(self, repository_tools):
        """Test update_repository method with partial update (branch only)."""
        # Define parameters
        project_id = 1
        repository_id = 42
        git_branch = "feature/new-branch"
        mock_updated = {
            "id": repository_id,
            "project_id": project_id,
            "git_branch": git_branch,
        }
        repository_tools.semaphore.update_repository.return_value = mock_updated

        # Call the method with only git_branch
        result = await repository_tools.update_repository(
            project_id, repository_id, git_branch=git_branch
        )

        # Verify the result
        assert result == mock_updated
        repository_tools.semaphore.update_repository.assert_called_once_with(
            project_id, repository_id, None, None, git_branch, None
        )

    @pytest.mark.asyncio
    async def test_delete_repository_error(self, repository_tools):
        """Test delete_repository method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        repository_id = 42
        repository_tools.semaphore.delete_repository.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await repository_tools.delete_repository(project_id, repository_id)

        # Verify the error message
        assert "Error during deleting repository 42" in str(excinfo.value)
