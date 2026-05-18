"""E2E tests for View tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestViewsE2E:
    """E2E tests for view CRUD operations."""

    def test_list_views(self, inspector: MCPInspector, created_project: dict):
        """Test listing views for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_views", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "views" in data
        assert isinstance(data["views"], list)

    def test_view_crud_workflow(self, inspector: MCPInspector, created_project: dict):
        """Test creating, reading, updating, listing, and deleting a view."""
        project_id = created_project["id"]

        create_result = inspector.call_tool(
            "create_view",
            {"project_id": project_id, "title": "E2E View", "position": 1},
        )
        view = parse_mcp_response(create_result)
        assert isinstance(view, dict), view
        view_id = view["id"]

        try:
            assert view["title"] == "E2E View"
            assert view["project_id"] == project_id

            get_result = inspector.call_tool(
                "get_view", {"project_id": project_id, "view_id": view_id}
            )
            read_view = parse_mcp_response(get_result)
            assert read_view["id"] == view_id

            inspector.call_tool(
                "update_view",
                {
                    "project_id": project_id,
                    "view_id": view_id,
                    "title": "E2E Updated View",
                    "position": 2,
                },
            )

            get_result = inspector.call_tool(
                "get_view", {"project_id": project_id, "view_id": view_id}
            )
            updated = parse_mcp_response(get_result)
            assert updated["title"] == "E2E Updated View"
            assert updated["position"] == 2

            list_result = inspector.call_tool("list_views", {"project_id": project_id})
            views = parse_mcp_response(list_result)["views"]
            assert view_id in [item["id"] for item in views]

        finally:
            inspector.call_tool(
                "delete_view", {"project_id": project_id, "view_id": view_id}
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
