"""
Tests for the TemplateTools class functionality.
"""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from semaphore_mcp.tools.templates import TemplateTools


class TestTemplateTools:
    """Test suite for TemplateTools class methods."""

    @pytest_asyncio.fixture
    async def template_tools(self):
        """Create a TemplateTools instance with a mock API client."""
        mock_client = MagicMock()
        return TemplateTools(mock_client)

    @pytest.mark.asyncio
    async def test_list_templates(self, template_tools):
        """Test list_templates method."""
        # Define mock return value for the list_templates API call
        project_id = 1
        mock_templates = [
            {"id": 1, "name": "Template 1", "project_id": project_id},
            {"id": 2, "name": "Template 2", "project_id": project_id},
        ]
        template_tools.semaphore.list_templates.return_value = mock_templates

        # Call the method
        result = await template_tools.list_templates(project_id)

        # Verify the result
        assert result == mock_templates
        template_tools.semaphore.list_templates.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_list_templates_error(self, template_tools):
        """Test list_templates method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_tools.semaphore.list_templates.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.list_templates(project_id)

        # Verify the error message
        assert "Error during listing templates" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_template(self, template_tools):
        """Test get_template method."""
        # Define mock return value for the get_template API call
        project_id = 1
        template_id = 42
        mock_template = {
            "id": template_id,
            "name": "Test Template",
            "project_id": project_id,
            "playbook": "playbook.yml",
        }
        template_tools.semaphore.get_template.return_value = mock_template

        # Call the method
        result = await template_tools.get_template(project_id, template_id)

        # Verify the result
        assert result == mock_template
        template_tools.semaphore.get_template.assert_called_once_with(
            project_id, template_id
        )

    @pytest.mark.asyncio
    async def test_get_template_error(self, template_tools):
        """Test get_template method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_id = 42
        template_tools.semaphore.get_template.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.get_template(project_id, template_id)

        # Verify the error message
        assert "Error during getting template" in str(excinfo.value)
