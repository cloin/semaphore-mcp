"""E2E tests for event tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestEventsE2E:
    """E2E tests for event and observability operations."""

    def test_list_events(self, inspector: MCPInspector):
        """Test listing global events."""
        result = inspector.call_tool("list_events", {"limit": 5})
        data = parse_mcp_response(result)

        assert "events" in data
        assert isinstance(data["events"], list)
        assert len(data["events"]) <= 5

    def test_get_last_events(self, inspector: MCPInspector):
        """Test listing the last global events."""
        result = inspector.call_tool("get_last_events", {"limit": 5})
        data = parse_mcp_response(result)

        assert "events" in data
        assert isinstance(data["events"], list)
        assert len(data["events"]) <= 5

    def test_project_events_and_summary(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test listing and summarizing project events."""
        project_id = created_project["id"]

        inspector.call_tool(
            "update_project",
            {"project_id": project_id, "name": "E2E Events Updated Project"},
        )

        events_result = inspector.call_tool(
            "list_project_events", {"project_id": project_id, "limit": 10}
        )
        events_data = parse_mcp_response(events_result)

        assert "events" in events_data
        assert isinstance(events_data["events"], list)
        assert len(events_data["events"]) <= 10

        summary_result = inspector.call_tool(
            "summarize_project_activity",
            {"project_id": project_id, "limit": 10, "recent_limit": 3},
        )
        summary = parse_mcp_response(summary_result)

        assert summary["project_id"] == project_id
        assert summary["event_count"] <= 10
        assert summary["total_available"] >= summary["event_count"]
        assert "counts_by_object_type" in summary
        assert "counts_by_description" in summary
        assert "counts_by_user_id" in summary
        assert len(summary["recent_events"]) <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
