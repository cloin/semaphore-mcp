"""Tests for EventTools."""

import pytest


class TestEventTools:
    """Test suite for event tool methods."""

    @pytest.mark.asyncio
    async def test_list_events(self, event_tools, sample_events):
        """Test list_events method."""
        event_tools.semaphore.list_events.return_value = sample_events

        result = await event_tools.list_events()

        assert result == {"events": sample_events}
        event_tools.semaphore.list_events.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_list_events_with_limit(self, event_tools, sample_events):
        """Test list_events trims to most recent events."""
        event_tools.semaphore.list_events.return_value = sample_events

        result = await event_tools.list_events(limit=2)

        assert result == {"events": sample_events[-2:]}

    @pytest.mark.asyncio
    async def test_get_last_events(self, event_tools, sample_events):
        """Test get_last_events method."""
        event_tools.semaphore.get_last_events.return_value = sample_events

        result = await event_tools.get_last_events(limit=1)

        assert result == {"events": sample_events[-1:]}
        event_tools.semaphore.get_last_events.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_list_project_events(self, event_tools, sample_events):
        """Test list_project_events method."""
        event_tools.semaphore.list_project_events.return_value = sample_events

        result = await event_tools.list_project_events(1, limit=2)

        assert result == {"events": sample_events[-2:]}
        event_tools.semaphore.list_project_events.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_summarize_project_activity(self, event_tools, sample_events):
        """Test summarize_project_activity method."""
        event_tools.semaphore.list_project_events.return_value = sample_events

        result = await event_tools.summarize_project_activity(
            1, limit=3, recent_limit=2
        )

        assert result["project_id"] == 1
        assert result["event_count"] == 3
        assert result["total_available"] == 3
        assert result["counts_by_object_type"] == {
            "project": 1,
            "template": 1,
            "task": 1,
        }
        assert result["counts_by_description"]["Project created"] == 1
        assert result["counts_by_user_id"] == {"1": 2, "2": 1}
        assert result["recent_events"] == sample_events[-2:]

    @pytest.mark.asyncio
    async def test_summarize_project_activity_requires_positive_limit(
        self, event_tools
    ):
        """Test summarize_project_activity validates limit."""
        with pytest.raises(RuntimeError) as excinfo:
            await event_tools.summarize_project_activity(1, limit=0)

        assert "limit must be 1 or greater" in str(excinfo.value)
        event_tools.semaphore.list_project_events.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_events_rejects_negative_limit(self, event_tools):
        """Test list_events validates negative limit."""
        event_tools.semaphore.list_events.return_value = []

        with pytest.raises(RuntimeError) as excinfo:
            await event_tools.list_events(limit=-1)

        assert "limit must be 0 or greater" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_list_events_error(self, event_tools):
        """Test list_events method with error."""
        event_tools.semaphore.list_events.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as excinfo:
            await event_tools.list_events()

        assert "Error during listing events" in str(excinfo.value)
