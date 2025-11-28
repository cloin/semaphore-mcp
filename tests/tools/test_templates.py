"""
Tests for the TemplateTools class functionality.
"""

import pytest


class TestTemplateTools:
    """Test suite for TemplateTools class methods."""

    # Note: template_tools fixture is provided by conftest.py

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

        # Verify the result - expect wrapped response
        assert result == {"templates": mock_templates}
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

    @pytest.mark.asyncio
    async def test_create_template(self, template_tools):
        """Test create_template method."""
        # Define mock return value for the create_template API call
        project_id = 1
        mock_template = {
            "id": 1,
            "name": "New Template",
            "project_id": project_id,
            "playbook": "playbook.yml",
            "inventory_id": 1,
            "repository_id": 1,
            "environment_id": 1,
        }
        template_tools.semaphore.create_template.return_value = mock_template

        # Call the method
        result = await template_tools.create_template(
            project_id=project_id,
            name="New Template",
            playbook="playbook.yml",
            inventory_id=1,
            repository_id=1,
            environment_id=1,
        )

        # Verify the result
        assert result == mock_template
        template_tools.semaphore.create_template.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_template_error(self, template_tools):
        """Test create_template method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_tools.semaphore.create_template.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.create_template(
                project_id=project_id,
                name="Test Template",
                playbook="test.yml",
                inventory_id=1,
                repository_id=1,
                environment_id=1,
            )

        # Verify the error message
        assert "Error during creating template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_template(self, template_tools):
        """Test update_template method."""
        # Define mock return value for the update_template API call
        project_id = 1
        template_id = 1
        template_tools.semaphore.update_template.return_value = {}

        # Call the method with partial update
        result = await template_tools.update_template(
            project_id=project_id,
            template_id=template_id,
            name="Updated Template",
            playbook="updated.yml",
        )

        # Verify the result
        assert result == {}
        template_tools.semaphore.update_template.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_template_error(self, template_tools):
        """Test update_template method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_id = 1
        template_tools.semaphore.update_template.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.update_template(
                project_id=project_id,
                template_id=template_id,
                name="Test",
            )

        # Verify the error message
        assert "Error during updating template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_delete_template(self, template_tools):
        """Test delete_template method."""
        # Define mock return value for the delete_template API call
        project_id = 1
        template_id = 1
        template_tools.semaphore.delete_template.return_value = {}

        # Call the method
        result = await template_tools.delete_template(project_id, template_id)

        # Verify the result
        assert result == {}
        template_tools.semaphore.delete_template.assert_called_once_with(
            project_id, template_id
        )

    @pytest.mark.asyncio
    async def test_delete_template_error(self, template_tools):
        """Test delete_template method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_id = 1
        template_tools.semaphore.delete_template.side_effect = Exception("API error")

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.delete_template(project_id, template_id)

        # Verify the error message
        assert "Error during deleting template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_stop_all_template_tasks(self, template_tools):
        """Test stop_all_template_tasks method."""
        # Define mock return value for the stop_all_template_tasks API call
        project_id = 1
        template_id = 1
        template_tools.semaphore.stop_all_template_tasks.return_value = {}

        # Call the method
        result = await template_tools.stop_all_template_tasks(project_id, template_id)

        # Verify the result
        assert result == {}
        template_tools.semaphore.stop_all_template_tasks.assert_called_once_with(
            project_id, template_id
        )

    @pytest.mark.asyncio
    async def test_stop_all_template_tasks_error(self, template_tools):
        """Test stop_all_template_tasks method with error."""
        # Set up the mock to raise an exception
        project_id = 1
        template_id = 1
        template_tools.semaphore.stop_all_template_tasks.side_effect = Exception(
            "API error"
        )

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.stop_all_template_tasks(project_id, template_id)

        # Verify the error message
        assert "Error during stopping all tasks for template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_template_404_fallback_found_in_list(self, template_tools):
        """Test get_template 404 fallback when template found in list."""
        project_id = 1
        template_id = 42

        # Set up get_template to raise 404
        template_tools.semaphore.get_template.side_effect = Exception("404 Not Found")

        # Set up list_templates to return the template
        mock_templates = [
            {"id": 41, "name": "Other Template"},
            {"id": 42, "name": "Target Template", "playbook": "playbook.yml"},
            {"id": 43, "name": "Another Template"},
        ]
        template_tools.semaphore.list_templates.return_value = mock_templates

        # Call the method
        result = await template_tools.get_template(project_id, template_id)

        # Verify the result - should return the template with a note
        assert result["template"]["id"] == 42
        assert result["template"]["name"] == "Target Template"
        assert "note" in result
        assert "individual endpoint unavailable" in result["note"]

    @pytest.mark.asyncio
    async def test_get_template_404_fallback_not_found_in_list(self, template_tools):
        """Test get_template 404 fallback when template not found in list."""
        project_id = 1
        template_id = 999

        # Set up get_template to raise 404
        template_tools.semaphore.get_template.side_effect = Exception("404 Not Found")

        # Set up list_templates to return templates without the target
        mock_templates = [
            {"id": 1, "name": "Template 1"},
            {"id": 2, "name": "Template 2"},
        ]
        template_tools.semaphore.list_templates.return_value = mock_templates

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.get_template(project_id, template_id)

        # Verify the error message mentions it may have been deleted
        assert "Error during getting template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_template_404_fallback_list_also_fails(self, template_tools):
        """Test get_template 404 fallback when list_templates also fails."""
        project_id = 1
        template_id = 42

        # Set up get_template to raise 404
        template_tools.semaphore.get_template.side_effect = Exception("404 Not Found")

        # Set up list_templates to also fail
        template_tools.semaphore.list_templates.side_effect = Exception(
            "Connection error"
        )

        # The method should raise a RuntimeError from the original 404
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.get_template(project_id, template_id)

        assert "Error during getting template" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_template_404_fallback_list_returns_dict(self, template_tools):
        """Test get_template 404 fallback when list returns non-list."""
        project_id = 1
        template_id = 42

        # Set up get_template to raise 404
        template_tools.semaphore.get_template.side_effect = Exception("404 Not Found")

        # Set up list_templates to return a dict (unexpected format)
        template_tools.semaphore.list_templates.return_value = {"error": "unexpected"}

        # The method should raise a RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            await template_tools.get_template(project_id, template_id)

        assert "Error during getting template" in str(excinfo.value)
