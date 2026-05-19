"""
Tests for the ProjectTools class functionality.
"""

import pytest


class TestProjectTools:
    """Test suite for ProjectTools class methods."""

    # Note: project_tools fixture is provided by conftest.py

    @pytest.mark.asyncio
    async def test_list_projects(self, project_tools):
        """Test list_projects method."""
        # Define mock return value for the list_projects API call
        mock_projects = [
            {"id": 1, "name": "Test Project 1"},
            {"id": 2, "name": "Test Project 2"},
        ]
        project_tools.semaphore.list_projects.return_value = mock_projects

        # Call the method
        result = await project_tools.list_projects()

        # Verify the result - expect wrapped response
        assert result == {"projects": mock_projects}
        project_tools.semaphore.list_projects.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_projects_error(self, project_tools):
        """Test list_projects method with error."""
        # Set up the mock to raise an exception
        project_tools.semaphore.list_projects.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.list_projects()

        # Verify the error message
        assert "Error during listing projects" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_project(self, project_tools):
        """Test get_project method."""
        # Define mock return value for the get_project API call
        project_id = 42
        mock_project = {
            "id": project_id,
            "name": "Test Project",
            "description": "A test project",
        }
        project_tools.semaphore.get_project.return_value = mock_project

        # Call the method
        result = await project_tools.get_project(project_id)

        # Verify the result
        assert result == mock_project
        project_tools.semaphore.get_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_error(self, project_tools):
        """Test get_project method with error."""
        # Set up the mock to raise an exception
        project_id = 42
        project_tools.semaphore.get_project.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.get_project(project_id)

        # Verify the error message
        assert "Error during getting project" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_create_project(self, project_tools):
        """Test create_project method."""
        # Define mock return value for the create_project API call
        mock_project = {
            "id": 1,
            "name": "New Project",
            "alert": False,
            "max_parallel_tasks": 0,
        }
        project_tools.semaphore.create_project.return_value = mock_project

        # Call the method
        result = await project_tools.create_project(
            name="New Project",
            alert=False,
            max_parallel_tasks=0,
        )

        # Verify the result
        assert result == mock_project
        project_tools.semaphore.create_project.assert_called_once_with(
            name="New Project",
            alert=False,
            alert_chat=None,
            max_parallel_tasks=0,
            project_type=None,
            demo=False,
        )

    @pytest.mark.asyncio
    async def test_create_project_error(self, project_tools):
        """Test create_project method with error."""
        # Set up the mock to raise an exception
        project_tools.semaphore.create_project.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.create_project(name="Test Project")

        # Verify the error message
        assert "Error during creating project" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_project(self, project_tools):
        """Test update_project method."""
        # Define mock return value for the update_project API call
        project_id = 1
        project_tools.semaphore.update_project.return_value = {}

        # Call the method with partial update
        result = await project_tools.update_project(
            project_id=project_id,
            name="Updated Project",
            max_parallel_tasks=5,
        )

        # Verify the result
        assert result == {}
        project_tools.semaphore.update_project.assert_called_once_with(
            project_id=project_id,
            name="Updated Project",
            alert=None,
            alert_chat=None,
            max_parallel_tasks=5,
            project_type=None,
        )

    @pytest.mark.asyncio
    async def test_update_project_error(self, project_tools):
        """Test update_project method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        project_tools.semaphore.update_project.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.update_project(project_id=project_id, name="Test")

        # Verify the error message
        assert "Error during updating project" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_delete_project(self, project_tools):
        """Test delete_project method."""
        # Define mock return value for the delete_project API call
        project_id = 1
        project_tools.semaphore.delete_project.return_value = {}

        # Call the method
        result = await project_tools.delete_project(project_id)

        # Verify the result
        assert result == {}
        project_tools.semaphore.delete_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_delete_project_error(self, project_tools):
        """Test delete_project method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        project_tools.semaphore.delete_project.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.delete_project(project_id)

        # Verify the error message
        assert "Error during deleting project" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_backup_project(self, project_tools, sample_project_backup):
        """Test backup_project method."""
        project_id = 1
        project_tools.semaphore.backup_project.return_value = sample_project_backup

        result = await project_tools.backup_project(project_id)

        assert result["project_id"] == project_id
        assert result["backup"] == sample_project_backup
        assert result["summary"]["project_name"] == "Source Project"
        assert result["summary"]["sections"]["templates"] == 1
        project_tools.semaphore.backup_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_backup_project_error(self, project_tools):
        """Test backup_project method with error."""
        project_tools.semaphore.backup_project.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.backup_project(1)

        assert "Error during backing up project" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_restore_project_backup_with_name_override(
        self, project_tools, sample_project_backup
    ):
        """Test restore_project_backup with project name override."""
        project_tools.semaphore.restore_project_backup.return_value = {
            "id": 2,
            "name": "Restored Project",
        }

        result = await project_tools.restore_project_backup(
            sample_project_backup,
            project_name="Restored Project",
        )

        assert result["project"] == {"id": 2, "name": "Restored Project"}
        assert result["summary"]["project_name"] == "Restored Project"
        assert sample_project_backup["meta"]["name"] == "Source Project"
        called_backup = project_tools.semaphore.restore_project_backup.call_args.args[0]
        assert called_backup["meta"]["name"] == "Restored Project"

    @pytest.mark.asyncio
    async def test_restore_project_backup_validation_error(
        self, project_tools, sample_project_backup
    ):
        """Test restore_project_backup rejects invalid references."""
        sample_project_backup["templates"][0]["repository"] = "Missing Repo"

        with pytest.raises(RuntimeError) as excinfo:
            await project_tools.restore_project_backup(sample_project_backup)

        assert "Invalid Semaphore project backup" in str(excinfo.value)
        project_tools.semaphore.restore_project_backup.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_project_backup(self, project_tools, sample_project_backup):
        """Test validate_project_backup method."""
        result = await project_tools.validate_project_backup(sample_project_backup)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["summary"]["names"]["templates"] == ["Deploy"]

    @pytest.mark.asyncio
    async def test_validate_project_backup_invalid_reference(
        self, project_tools, sample_project_backup
    ):
        """Test validate_project_backup reports invalid references."""
        sample_project_backup["inventories"][0]["ssh_key"] = "Missing Key"

        result = await project_tools.validate_project_backup(sample_project_backup)

        assert result["valid"] is False
        assert (
            "inventories[0].ssh_key references missing key 'Missing Key'"
            in result["errors"]
        )

    @pytest.mark.asyncio
    async def test_summarize_project_backup(self, project_tools, sample_project_backup):
        """Test summarize_project_backup method."""
        result = await project_tools.summarize_project_backup(sample_project_backup)

        assert result["project_name"] == "Source Project"
        assert result["sections"]["templates"] == 1
        assert result["sections"]["repositories"] == 1
        assert result["total_resources"] == 6
        assert result["contains_secret_references"] is False

    @pytest.mark.asyncio
    async def test_clone_project(self, project_tools, sample_project_backup):
        """Test clone_project backs up and restores with a new name."""
        project_tools.semaphore.backup_project.return_value = sample_project_backup
        project_tools.semaphore.restore_project_backup.return_value = {
            "id": 2,
            "name": "Cloned Project",
        }

        result = await project_tools.clone_project(1, "Cloned Project")

        assert result["source_project_id"] == 1
        assert result["project"]["name"] == "Cloned Project"
        assert result["summary"]["project_name"] == "Cloned Project"
        assert sample_project_backup["meta"]["name"] == "Source Project"
        project_tools.semaphore.backup_project.assert_called_once_with(1)
        called_backup = project_tools.semaphore.restore_project_backup.call_args.args[0]
        assert called_backup["meta"]["name"] == "Cloned Project"
