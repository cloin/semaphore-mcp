"""Tests for ViewTools."""

import pytest


class TestViewTools:
    """Test suite for view tool methods."""

    @pytest.mark.asyncio
    async def test_list_views(self, view_tools, sample_views):
        """Test list_views method."""
        project_id = 1
        view_tools.semaphore.list_views.return_value = sample_views

        result = await view_tools.list_views(project_id)

        assert result == {"views": sample_views}
        view_tools.semaphore.list_views.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_view(self, view_tools, sample_views):
        """Test get_view method."""
        project_id = 1
        view_id = 1
        view_tools.semaphore.get_view.return_value = sample_views[0]

        result = await view_tools.get_view(project_id, view_id)

        assert result == sample_views[0]
        view_tools.semaphore.get_view.assert_called_once_with(project_id, view_id)

    @pytest.mark.asyncio
    async def test_create_view(self, view_tools, sample_views):
        """Test create_view method."""
        project_id = 1
        title = "Deployments"
        position = 1
        view_tools.semaphore.create_view.return_value = sample_views[0]

        result = await view_tools.create_view(project_id, title, position)

        assert result == sample_views[0]
        view_tools.semaphore.create_view.assert_called_once_with(
            project_id, title, position
        )

    @pytest.mark.asyncio
    async def test_update_view(self, view_tools):
        """Test update_view method."""
        project_id = 1
        view_id = 2
        mock_updated = {"id": view_id, "title": "Updated"}
        view_tools.semaphore.update_view.return_value = mock_updated

        result = await view_tools.update_view(
            project_id, view_id, title="Updated", position=3
        )

        assert result == mock_updated
        view_tools.semaphore.update_view.assert_called_once_with(
            project_id, view_id, "Updated", 3
        )

    @pytest.mark.asyncio
    async def test_delete_view(self, view_tools):
        """Test delete_view method."""
        view_tools.semaphore.delete_view.return_value = {}

        result = await view_tools.delete_view(1, 2)

        assert result == {}
        view_tools.semaphore.delete_view.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_list_views_error(self, view_tools):
        """Test list_views method with error."""
        view_tools.semaphore.list_views.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as excinfo:
            await view_tools.list_views(1)

        assert "Error during listing views" in str(excinfo.value)
