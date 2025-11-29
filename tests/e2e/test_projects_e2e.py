"""E2E tests for Project tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestProjectsE2E:
    """E2E tests for project CRUD operations."""

    def test_list_projects(self, inspector: MCPInspector):
        """Test listing all projects."""
        result = inspector.call_tool("list_projects")
        data = parse_mcp_response(result)

        assert "projects" in data
        assert isinstance(data["projects"], list)

    def test_create_and_delete_project(self, inspector: MCPInspector):
        """Test creating and deleting a project."""
        # Create
        create_result = inspector.call_tool(
            "create_project", {"name": "E2E Create Test Project"}
        )
        project = parse_mcp_response(create_result)

        assert "id" in project
        assert project["name"] == "E2E Create Test Project"

        project_id = project["id"]

        # Delete
        delete_result = inspector.call_tool(
            "delete_project", {"project_id": project_id}
        )
        # Delete typically returns empty or confirmation
        assert delete_result is not None

    def test_get_project(self, inspector: MCPInspector, created_project: dict):
        """Test getting a specific project."""
        project_id = created_project["id"]

        result = inspector.call_tool("get_project", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert data["id"] == project_id
        assert "name" in data

    def test_update_project(self, inspector: MCPInspector, created_project: dict):
        """Test updating a project."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "update_project",
            {"project_id": project_id, "name": "E2E Updated Project Name"},
        )
        # Update typically returns empty or the updated project
        assert result is not None

        # Verify the update
        get_result = inspector.call_tool("get_project", {"project_id": project_id})
        updated_project = parse_mcp_response(get_result)
        assert updated_project["name"] == "E2E Updated Project Name"

    def test_project_crud_workflow(self, inspector: MCPInspector):
        """Test complete project CRUD workflow."""
        # Create
        create_result = inspector.call_tool(
            "create_project",
            {"name": "E2E CRUD Workflow Project", "alert": False},
        )
        project = parse_mcp_response(create_result)
        assert "id" in project
        project_id = project["id"]

        try:
            # Read
            get_result = inspector.call_tool("get_project", {"project_id": project_id})
            read_project = parse_mcp_response(get_result)
            assert read_project["id"] == project_id
            assert read_project["name"] == "E2E CRUD Workflow Project"

            # Update
            inspector.call_tool(
                "update_project",
                {"project_id": project_id, "name": "E2E CRUD Updated"},
            )

            # Verify update
            get_result = inspector.call_tool("get_project", {"project_id": project_id})
            updated_project = parse_mcp_response(get_result)
            assert updated_project["name"] == "E2E CRUD Updated"

            # List and verify project is in list
            list_result = inspector.call_tool("list_projects")
            projects_data = parse_mcp_response(list_result)
            project_ids = [p["id"] for p in projects_data["projects"]]
            assert project_id in project_ids

        finally:
            # Delete (cleanup)
            inspector.call_tool("delete_project", {"project_id": project_id})

            # Verify deletion - project should not be in list
            list_result = inspector.call_tool("list_projects")
            projects_data = parse_mcp_response(list_result)
            project_ids = [p["id"] for p in projects_data["projects"]]
            assert project_id not in project_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
