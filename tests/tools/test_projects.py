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
