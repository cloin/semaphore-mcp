"""
Tests for the ProjectTools class functionality.
"""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch
from semaphore_mcp.tools.projects import ProjectTools


class TestProjectTools:
    """Test suite for ProjectTools class methods."""
    
    @pytest_asyncio.fixture
    async def project_tools(self):
        """Create a ProjectTools instance with a mock API client."""
        mock_client = MagicMock()
        return ProjectTools(mock_client)
    
    @pytest.mark.asyncio
    async def test_list_projects(self, project_tools):
        """Test list_projects method."""
        # Define mock return value for the list_projects API call
        mock_projects = [{"id": 1, "name": "Test Project 1"}, {"id": 2, "name": "Test Project 2"}]
        project_tools.semaphore.list_projects.return_value = mock_projects
        
        # Call the method
        result = await project_tools.list_projects()
        
        # Verify the result
        assert result == mock_projects
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
        mock_project = {"id": project_id, "name": "Test Project", "description": "A test project"}
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
