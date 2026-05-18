"""Tests for ScheduleTools."""

import pytest


class TestScheduleTools:
    """Test suite for schedule tool methods."""

    @pytest.mark.asyncio
    async def test_list_schedules(self, schedule_tools, sample_schedules):
        """Test list_schedules method."""
        project_id = 1
        schedule_tools.semaphore.list_schedules.return_value = sample_schedules

        result = await schedule_tools.list_schedules(project_id)

        assert result == {"schedules": sample_schedules}
        schedule_tools.semaphore.list_schedules.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_list_template_schedules(self, schedule_tools, sample_schedules):
        """Test list_template_schedules method."""
        project_id = 1
        template_id = 10
        schedule_tools.semaphore.list_template_schedules.return_value = [
            sample_schedules[0]
        ]

        result = await schedule_tools.list_template_schedules(project_id, template_id)

        assert result == {"schedules": [sample_schedules[0]]}
        schedule_tools.semaphore.list_template_schedules.assert_called_once_with(
            project_id, template_id
        )

    @pytest.mark.asyncio
    async def test_get_schedule(self, schedule_tools, sample_schedules):
        """Test get_schedule method."""
        project_id = 1
        schedule_id = 1
        schedule_tools.semaphore.get_schedule.return_value = sample_schedules[0]

        result = await schedule_tools.get_schedule(project_id, schedule_id)

        assert result == sample_schedules[0]
        schedule_tools.semaphore.get_schedule.assert_called_once_with(
            project_id, schedule_id
        )

    @pytest.mark.asyncio
    async def test_create_cron_schedule(self, schedule_tools, sample_schedules):
        """Test create_schedule method with a cron schedule."""
        project_id = 1
        template_id = 10
        name = "Nightly deploy"
        cron_format = "0 0 * * *"
        schedule_tools.semaphore.create_schedule.return_value = sample_schedules[0]

        result = await schedule_tools.create_schedule(
            project_id,
            template_id,
            name,
            cron_format=cron_format,
            active=False,
            task_params={"message": "scheduled run"},
        )

        assert result == sample_schedules[0]
        schedule_tools.semaphore.create_schedule.assert_called_once_with(
            project_id,
            template_id,
            name,
            cron_format,
            False,
            "",
            None,
            {"message": "scheduled run"},
            None,
            None,
        )

    @pytest.mark.asyncio
    async def test_create_run_at_schedule(self, schedule_tools, sample_schedules):
        """Test create_schedule method with a one-time run_at schedule."""
        project_id = 1
        template_id = 11
        name = "One-time maintenance"
        run_at = "2026-05-19T12:00:00Z"
        schedule_tools.semaphore.create_schedule.return_value = sample_schedules[1]

        result = await schedule_tools.create_schedule(
            project_id,
            template_id,
            name,
            active=False,
            schedule_type="run_at",
            run_at=run_at,
            delete_after_run=True,
        )

        assert result == sample_schedules[1]
        schedule_tools.semaphore.create_schedule.assert_called_once_with(
            project_id,
            template_id,
            name,
            None,
            False,
            "run_at",
            run_at,
            None,
            True,
            None,
        )

    @pytest.mark.asyncio
    async def test_create_cron_schedule_requires_cron_format(self, schedule_tools):
        """Test create_schedule validates missing cron_format."""
        with pytest.raises(RuntimeError) as excinfo:
            await schedule_tools.create_schedule(1, 10, "Missing cron")

        assert "cron_format is required" in str(excinfo.value)
        schedule_tools.semaphore.create_schedule.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_run_at_schedule_requires_run_at(self, schedule_tools):
        """Test create_schedule validates missing run_at."""
        with pytest.raises(RuntimeError) as excinfo:
            await schedule_tools.create_schedule(
                1, 10, "Missing run_at", schedule_type="run_at"
            )

        assert "run_at is required" in str(excinfo.value)
        schedule_tools.semaphore.create_schedule.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_schedule(self, schedule_tools):
        """Test update_schedule method."""
        project_id = 1
        schedule_id = 2
        mock_updated = {"id": schedule_id, "name": "Updated"}
        schedule_tools.semaphore.update_schedule.return_value = mock_updated

        result = await schedule_tools.update_schedule(
            project_id,
            schedule_id,
            name="Updated",
            active=True,
            cron_format="30 2 * * *",
        )

        assert result == mock_updated
        schedule_tools.semaphore.update_schedule.assert_called_once_with(
            project_id,
            schedule_id,
            None,
            "Updated",
            "30 2 * * *",
            True,
            None,
            None,
            None,
            None,
            None,
        )

    @pytest.mark.asyncio
    async def test_set_schedule_active(self, schedule_tools):
        """Test set_schedule_active method."""
        schedule_tools.semaphore.set_schedule_active.return_value = {}

        result = await schedule_tools.set_schedule_active(1, 2, False)

        assert result == {}
        schedule_tools.semaphore.set_schedule_active.assert_called_once_with(
            1, 2, False
        )

    @pytest.mark.asyncio
    async def test_delete_schedule(self, schedule_tools):
        """Test delete_schedule method."""
        schedule_tools.semaphore.delete_schedule.return_value = {}

        result = await schedule_tools.delete_schedule(1, 2)

        assert result == {}
        schedule_tools.semaphore.delete_schedule.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_validate_schedule_cron_format(self, schedule_tools):
        """Test validate_schedule_cron_format method."""
        schedule_tools.semaphore.validate_schedule_cron_format.return_value = {}

        result = await schedule_tools.validate_schedule_cron_format(1, "0 0 * * *")

        assert result == {}
        schedule_tools.semaphore.validate_schedule_cron_format.assert_called_once_with(
            1, "0 0 * * *"
        )

    @pytest.mark.asyncio
    async def test_list_schedules_error(self, schedule_tools):
        """Test list_schedules method with error."""
        schedule_tools.semaphore.list_schedules.side_effect = Exception("API error")

        with pytest.raises(RuntimeError) as excinfo:
            await schedule_tools.list_schedules(1)

        assert "Error during listing schedules" in str(excinfo.value)
