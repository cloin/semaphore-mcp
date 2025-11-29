"""E2E tests for Template tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestTemplatesE2E:
    """E2E tests for template CRUD operations.

    These tests use fixtures that set up the required dependencies:
    - created_environment: provides an environment
    - created_inventory: provides an inventory
    - created_repository: provides a repository with access key
    - created_template: provides a fully configured template
    """

    def test_list_templates(self, inspector: MCPInspector, created_project: dict):
        """Test listing templates for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_templates", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_create_and_delete_template(
        self,
        inspector: MCPInspector,
        created_project: dict,
        created_environment: tuple,
        created_inventory: tuple,
        created_repository: tuple,
    ):
        """Test creating and deleting a template."""
        project_id = created_project["id"]
        environment, _ = created_environment
        inventory, _ = created_inventory
        repository, _ = created_repository

        # Create
        create_result = inspector.call_tool(
            "create_template",
            {
                "project_id": project_id,
                "name": "E2E Create Test Template",
                "playbook": "test.yml",
                "environment_id": environment["id"],
                "inventory_id": inventory["id"],
                "repository_id": repository["id"],
            },
        )
        template = parse_mcp_response(create_result)

        assert "id" in template
        assert template["name"] == "E2E Create Test Template"

        template_id = template["id"]

        # Delete
        delete_result = inspector.call_tool(
            "delete_template",
            {"project_id": project_id, "template_id": template_id},
        )
        assert delete_result is not None

    def test_get_template(self, inspector: MCPInspector, created_template: tuple):
        """Test getting a specific template."""
        template, project_id = created_template

        result = inspector.call_tool(
            "get_template",
            {"project_id": project_id, "template_id": template["id"]},
        )
        data = parse_mcp_response(result)

        assert data["id"] == template["id"]
        assert "name" in data

    def test_update_template(self, inspector: MCPInspector, created_template: tuple):
        """Test updating a template."""
        template, project_id = created_template

        result = inspector.call_tool(
            "update_template",
            {
                "project_id": project_id,
                "template_id": template["id"],
                "name": "E2E Updated Template",
                "description": "Updated description",
            },
        )
        assert result is not None

        # Verify the update
        get_result = inspector.call_tool(
            "get_template",
            {"project_id": project_id, "template_id": template["id"]},
        )
        updated = parse_mcp_response(get_result)
        assert updated["name"] == "E2E Updated Template"

    def test_stop_all_template_tasks(
        self, inspector: MCPInspector, created_template: tuple
    ):
        """Test stopping all tasks for a template.

        Note: This just tests that the endpoint responds, even if there are no tasks.
        """
        template, project_id = created_template

        result = inspector.call_tool(
            "stop_all_template_tasks",
            {"project_id": project_id, "template_id": template["id"]},
        )
        # The result could indicate no tasks to stop, which is fine
        assert result is not None

    def test_template_crud_workflow(
        self,
        inspector: MCPInspector,
        created_project: dict,
        created_environment: tuple,
        created_inventory: tuple,
        created_repository: tuple,
    ):
        """Test complete template CRUD workflow."""
        project_id = created_project["id"]
        environment, _ = created_environment
        inventory, _ = created_inventory
        repository, _ = created_repository

        # Create
        create_result = inspector.call_tool(
            "create_template",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Template",
                "playbook": "test.yml",
                "environment_id": environment["id"],
                "inventory_id": inventory["id"],
                "repository_id": repository["id"],
                "description": "E2E test template",
            },
        )
        template = parse_mcp_response(create_result)
        assert "id" in template
        template_id = template["id"]

        try:
            # Read
            get_result = inspector.call_tool(
                "get_template",
                {"project_id": project_id, "template_id": template_id},
            )
            read_template = parse_mcp_response(get_result)
            assert read_template["id"] == template_id

            # Update
            inspector.call_tool(
                "update_template",
                {
                    "project_id": project_id,
                    "template_id": template_id,
                    "name": "E2E CRUD Updated Template",
                },
            )

            # Verify update
            get_result = inspector.call_tool(
                "get_template",
                {"project_id": project_id, "template_id": template_id},
            )
            updated_template = parse_mcp_response(get_result)
            assert updated_template["name"] == "E2E CRUD Updated Template"

            # List and verify template is in list
            list_result = inspector.call_tool(
                "list_templates", {"project_id": project_id}
            )
            templates_data = parse_mcp_response(list_result)
            template_ids = [t["id"] for t in templates_data["templates"]]
            assert template_id in template_ids

        finally:
            # Delete (cleanup)
            inspector.call_tool(
                "delete_template",
                {"project_id": project_id, "template_id": template_id},
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
