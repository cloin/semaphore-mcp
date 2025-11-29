"""E2E tests for Environment and Inventory tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestEnvironmentsE2E:
    """E2E tests for environment CRUD operations."""

    def test_list_environments(self, inspector: MCPInspector, created_project: dict):
        """Test listing environments for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_environments", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "environments" in data
        assert isinstance(data["environments"], list)

    def test_create_and_delete_environment(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating and deleting an environment."""
        project_id = created_project["id"]

        # Create
        create_result = inspector.call_tool(
            "create_environment",
            {
                "project_id": project_id,
                "name": "E2E Create Test Environment",
                "env_data": {"APP_ENV": "test", "DEBUG": "true"},
            },
        )
        environment = parse_mcp_response(create_result)

        assert "id" in environment
        assert environment["name"] == "E2E Create Test Environment"

        environment_id = environment["id"]

        # Delete
        delete_result = inspector.call_tool(
            "delete_environment",
            {"project_id": project_id, "environment_id": environment_id},
        )
        assert delete_result is not None

    def test_get_environment(self, inspector: MCPInspector, created_environment: tuple):
        """Test getting a specific environment."""
        environment, project_id = created_environment
        environment_id = environment["id"]

        result = inspector.call_tool(
            "get_environment",
            {"project_id": project_id, "environment_id": environment_id},
        )
        data = parse_mcp_response(result)

        assert data["id"] == environment_id
        assert "name" in data

    def test_update_environment(
        self, inspector: MCPInspector, created_environment: tuple
    ):
        """Test updating an environment."""
        environment, project_id = created_environment
        environment_id = environment["id"]

        result = inspector.call_tool(
            "update_environment",
            {
                "project_id": project_id,
                "environment_id": environment_id,
                "name": "E2E Updated Environment",
            },
        )
        assert result is not None

        # Verify the update
        get_result = inspector.call_tool(
            "get_environment",
            {"project_id": project_id, "environment_id": environment_id},
        )
        updated_env = parse_mcp_response(get_result)
        assert updated_env["name"] == "E2E Updated Environment"

    def test_environment_crud_workflow(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test complete environment CRUD workflow."""
        project_id = created_project["id"]

        # Create
        create_result = inspector.call_tool(
            "create_environment",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Environment",
                "env_data": {"WORKFLOW_TEST": "value"},
            },
        )
        environment = parse_mcp_response(create_result)
        assert "id" in environment
        environment_id = environment["id"]

        try:
            # Read
            get_result = inspector.call_tool(
                "get_environment",
                {"project_id": project_id, "environment_id": environment_id},
            )
            read_env = parse_mcp_response(get_result)
            assert read_env["id"] == environment_id

            # Update
            inspector.call_tool(
                "update_environment",
                {
                    "project_id": project_id,
                    "environment_id": environment_id,
                    "name": "E2E CRUD Updated Env",
                },
            )

            # Verify update
            get_result = inspector.call_tool(
                "get_environment",
                {"project_id": project_id, "environment_id": environment_id},
            )
            updated_env = parse_mcp_response(get_result)
            assert updated_env["name"] == "E2E CRUD Updated Env"

            # List and verify environment is in list
            list_result = inspector.call_tool(
                "list_environments", {"project_id": project_id}
            )
            envs_data = parse_mcp_response(list_result)
            env_ids = [e["id"] for e in envs_data["environments"]]
            assert environment_id in env_ids

        finally:
            # Delete (cleanup)
            inspector.call_tool(
                "delete_environment",
                {"project_id": project_id, "environment_id": environment_id},
            )


class TestInventoryE2E:
    """E2E tests for inventory CRUD operations."""

    def test_list_inventory(self, inspector: MCPInspector, created_project: dict):
        """Test listing inventory for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_inventory", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "inventory" in data
        assert isinstance(data["inventory"], list)

    def test_create_and_delete_inventory(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating and deleting an inventory."""
        project_id = created_project["id"]

        # Create
        create_result = inspector.call_tool(
            "create_inventory",
            {
                "project_id": project_id,
                "name": "E2E Create Test Inventory",
                "inventory_data": "[all]\nlocalhost ansible_connection=local",
            },
        )
        inventory = parse_mcp_response(create_result)

        assert "id" in inventory
        assert inventory["name"] == "E2E Create Test Inventory"

        inventory_id = inventory["id"]

        # Delete
        delete_result = inspector.call_tool(
            "delete_inventory",
            {"project_id": project_id, "inventory_id": inventory_id},
        )
        assert delete_result is not None

    def test_get_inventory(self, inspector: MCPInspector, created_inventory: tuple):
        """Test getting a specific inventory."""
        inventory, project_id = created_inventory
        inventory_id = inventory["id"]

        result = inspector.call_tool(
            "get_inventory",
            {"project_id": project_id, "inventory_id": inventory_id},
        )
        data = parse_mcp_response(result)

        assert data["id"] == inventory_id
        assert "name" in data

    def test_update_inventory(self, inspector: MCPInspector, created_inventory: tuple):
        """Test updating an inventory."""
        inventory, project_id = created_inventory
        inventory_id = inventory["id"]

        result = inspector.call_tool(
            "update_inventory",
            {
                "project_id": project_id,
                "inventory_id": inventory_id,
                "name": "E2E Updated Inventory",
            },
        )
        assert result is not None

        # Verify the update
        get_result = inspector.call_tool(
            "get_inventory",
            {"project_id": project_id, "inventory_id": inventory_id},
        )
        updated_inv = parse_mcp_response(get_result)
        assert updated_inv["name"] == "E2E Updated Inventory"

    def test_inventory_crud_workflow(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test complete inventory CRUD workflow."""
        project_id = created_project["id"]

        # Create
        create_result = inspector.call_tool(
            "create_inventory",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Inventory",
                "inventory_data": "[webservers]\nweb1.example.com\nweb2.example.com",
            },
        )
        inventory = parse_mcp_response(create_result)
        assert "id" in inventory
        inventory_id = inventory["id"]

        try:
            # Read
            get_result = inspector.call_tool(
                "get_inventory",
                {"project_id": project_id, "inventory_id": inventory_id},
            )
            read_inv = parse_mcp_response(get_result)
            assert read_inv["id"] == inventory_id

            # Update
            inspector.call_tool(
                "update_inventory",
                {
                    "project_id": project_id,
                    "inventory_id": inventory_id,
                    "name": "E2E CRUD Updated Inventory",
                },
            )

            # Verify update
            get_result = inspector.call_tool(
                "get_inventory",
                {"project_id": project_id, "inventory_id": inventory_id},
            )
            updated_inv = parse_mcp_response(get_result)
            assert updated_inv["name"] == "E2E CRUD Updated Inventory"

            # List and verify inventory is in list
            list_result = inspector.call_tool(
                "list_inventory", {"project_id": project_id}
            )
            invs_data = parse_mcp_response(list_result)
            inv_ids = [i["id"] for i in invs_data["inventory"]]
            assert inventory_id in inv_ids

        finally:
            # Delete (cleanup)
            inspector.call_tool(
                "delete_inventory",
                {"project_id": project_id, "inventory_id": inventory_id},
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
