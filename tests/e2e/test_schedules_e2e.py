"""E2E tests for schedule tools."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


def future_run_at() -> str:
    """Return an RFC3339 UTC timestamp safely in the future."""
    return (
        (datetime.now(timezone.utc) + timedelta(days=1))
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class TestSchedulesE2E:
    """E2E tests for schedule CRUD operations."""

    def test_list_schedules(self, inspector: MCPInspector, created_project: dict):
        """Test listing schedules for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_schedules", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "schedules" in data
        assert isinstance(data["schedules"], list)

    def test_validate_schedule_cron_format(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test validating a cron schedule expression."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "validate_schedule_cron_format",
            {"project_id": project_id, "cron_format": "0 0 * * *"},
        )

        assert result is not None

    def test_cron_schedule_crud_workflow(
        self, inspector: MCPInspector, created_template: tuple
    ):
        """Test creating, reading, updating, listing, disabling, and deleting a cron schedule."""
        template, project_id = created_template

        create_result = inspector.call_tool(
            "create_schedule",
            {
                "project_id": project_id,
                "template_id": template["id"],
                "name": "E2E Cron Schedule",
                "cron_format": "0 0 1 1 *",
                "active": False,
                "task_params": {"message": "scheduled e2e run"},
            },
        )
        schedule = parse_mcp_response(create_result)
        assert isinstance(schedule, dict), schedule
        schedule_id = schedule["id"]

        try:
            assert schedule["name"] == "E2E Cron Schedule"
            assert schedule["template_id"] == template["id"]
            assert schedule["cron_format"] == "0 0 1 1 *"
            assert schedule["active"] is False

            get_result = inspector.call_tool(
                "get_schedule",
                {"project_id": project_id, "schedule_id": schedule_id},
            )
            read_schedule = parse_mcp_response(get_result)
            assert read_schedule["id"] == schedule_id

            inspector.call_tool(
                "update_schedule",
                {
                    "project_id": project_id,
                    "schedule_id": schedule_id,
                    "name": "E2E Updated Cron Schedule",
                    "cron_format": "30 2 1 1 *",
                },
            )

            get_result = inspector.call_tool(
                "get_schedule",
                {"project_id": project_id, "schedule_id": schedule_id},
            )
            updated = parse_mcp_response(get_result)
            assert updated["name"] == "E2E Updated Cron Schedule"
            assert updated["cron_format"] == "30 2 1 1 *"

            list_result = inspector.call_tool(
                "list_schedules", {"project_id": project_id}
            )
            schedules = parse_mcp_response(list_result)["schedules"]
            assert schedule_id in [item["id"] for item in schedules]

            template_schedules_result = inspector.call_tool(
                "list_template_schedules",
                {"project_id": project_id, "template_id": template["id"]},
            )
            template_schedules = parse_mcp_response(template_schedules_result)[
                "schedules"
            ]
            assert isinstance(template_schedules, list)

            toggle_result = inspector.call_tool(
                "set_schedule_active",
                {
                    "project_id": project_id,
                    "schedule_id": schedule_id,
                    "active": False,
                },
            )
            assert toggle_result is not None

        finally:
            inspector.call_tool(
                "delete_schedule",
                {"project_id": project_id, "schedule_id": schedule_id},
            )

    @pytest.mark.skip(
        reason=(
            "semaphoreui/semaphore:latest still validates run_at schedules as cron "
            "schedules and returns 'Cron: empty spec string'"
        )
    )
    def test_run_at_schedule_create_and_delete(
        self, inspector: MCPInspector, created_template: tuple
    ):
        """Test creating and deleting a one-time run_at schedule."""
        template, project_id = created_template

        create_result = inspector.call_tool(
            "create_schedule",
            {
                "project_id": project_id,
                "template_id": template["id"],
                "name": "E2E Run Once Schedule",
                "active": False,
                "schedule_type": "run_at",
                "run_at": future_run_at(),
                "delete_after_run": True,
            },
        )
        schedule = parse_mcp_response(create_result)
        assert isinstance(schedule, dict), schedule
        schedule_id = schedule["id"]

        try:
            assert schedule["name"] == "E2E Run Once Schedule"
            assert schedule["type"] == "run_at"
            assert schedule["active"] is False
            assert "run_at" in schedule
        finally:
            inspector.call_tool(
                "delete_schedule",
                {"project_id": project_id, "schedule_id": schedule_id},
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
