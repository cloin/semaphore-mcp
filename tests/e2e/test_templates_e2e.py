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

    Note: Template operations require environment, inventory, and repository
    to be configured first. Most tests are skipped by default as they require
    a more complete project setup.
    """

    def test_list_templates(self, inspector: MCPInspector, created_project: dict):
        """Test listing templates for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_templates", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "templates" in data
        assert isinstance(data["templates"], list)

    @pytest.mark.skip(
        reason="Requires environment, inventory, and repository to be created first"
    )
    def test_create_and_delete_template(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating and deleting a template.

        This test is skipped because templates require:
        - An environment
        - An inventory
        - A repository

        All of which must exist before creating a template.
        """
        project_id = created_project["id"]
        environment_id = 1  # Would need to create first
        inventory_id = 1  # Would need to create first
        repository_id = 1  # Would need to create first

        # Create
        create_result = inspector.call_tool(
            "create_template",
            {
                "project_id": project_id,
                "name": "E2E Create Test Template",
                "playbook": "playbook.yml",
                "environment_id": environment_id,
                "inventory_id": inventory_id,
                "repository_id": repository_id,
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

    @pytest.mark.skip(reason="Requires template to be created first")
    def test_get_template(self, inspector: MCPInspector, created_project: dict):
        """Test getting a specific template."""
        project_id = created_project["id"]
        template_id = 1  # Would need to create first

        result = inspector.call_tool(
            "get_template",
            {"project_id": project_id, "template_id": template_id},
        )
        data = parse_mcp_response(result)

        assert data["id"] == template_id
        assert "name" in data

    @pytest.mark.skip(reason="Requires template to be created first")
    def test_update_template(self, inspector: MCPInspector, created_project: dict):
        """Test updating a template."""
        project_id = created_project["id"]
        template_id = 1  # Would need to create first

        result = inspector.call_tool(
            "update_template",
            {
                "project_id": project_id,
                "template_id": template_id,
                "name": "E2E Updated Template",
                "description": "Updated description",
            },
        )
        assert result is not None

    @pytest.mark.skip(reason="Requires template to be created first")
    def test_stop_all_template_tasks(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test stopping all tasks for a template."""
        project_id = created_project["id"]
        template_id = 1  # Would need to create first

        result = inspector.call_tool(
            "stop_all_template_tasks",
            {"project_id": project_id, "template_id": template_id},
        )
        assert result is not None

    @pytest.mark.skip(
        reason="Requires environment, inventory, and repository to be created first"
    )
    def test_template_crud_workflow(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test complete template CRUD workflow.

        This test is skipped because templates require dependent resources.
        """
        project_id = created_project["id"]
        environment_id = 1
        inventory_id = 1
        repository_id = 1

        # Create
        create_result = inspector.call_tool(
            "create_template",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Template",
                "playbook": "site.yml",
                "environment_id": environment_id,
                "inventory_id": inventory_id,
                "repository_id": repository_id,
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
