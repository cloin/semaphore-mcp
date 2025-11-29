"""E2E tests for Access Key tools.

Note: Only list and create operations are exposed as MCP tools.
Get, update, and delete are intentionally not exposed for security reasons.
"""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestAccessKeysE2E:
    """E2E tests for access key operations."""

    def test_list_access_keys(self, inspector: MCPInspector, created_project: dict):
        """Test listing access keys for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_access_keys", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "access_keys" in data
        assert isinstance(data["access_keys"], list)

    def test_create_access_key_none_type(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating a 'none' type access key for public repos."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "create_access_key",
            {
                "project_id": project_id,
                "name": "E2E Public Repo Key",
                "key_type": "none",
            },
        )
        access_key = parse_mcp_response(result)

        assert "id" in access_key
        assert access_key["name"] == "E2E Public Repo Key"
        assert access_key["type"] == "none"

    def test_create_access_key_login_password_type(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating a 'login_password' type access key."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "create_access_key",
            {
                "project_id": project_id,
                "name": "E2E Login Key",
                "key_type": "login_password",
                "login": "test_user",
                "password": "test_password",
            },
        )
        access_key = parse_mcp_response(result)

        assert "id" in access_key
        assert access_key["name"] == "E2E Login Key"
        assert access_key["type"] == "login_password"

    def test_create_and_list_access_keys(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating access keys and verifying they appear in list."""
        project_id = created_project["id"]

        # Create two access keys
        result1 = inspector.call_tool(
            "create_access_key",
            {
                "project_id": project_id,
                "name": "E2E Key 1",
                "key_type": "none",
            },
        )
        key1 = parse_mcp_response(result1)

        result2 = inspector.call_tool(
            "create_access_key",
            {
                "project_id": project_id,
                "name": "E2E Key 2",
                "key_type": "none",
            },
        )
        key2 = parse_mcp_response(result2)

        # List and verify both keys are present
        list_result = inspector.call_tool(
            "list_access_keys", {"project_id": project_id}
        )
        data = parse_mcp_response(list_result)

        key_ids = [k["id"] for k in data["access_keys"]]
        assert key1["id"] in key_ids
        assert key2["id"] in key_ids

    def test_access_key_workflow(self, inspector: MCPInspector, created_project: dict):
        """Test complete access key workflow for setting up a public repo."""
        project_id = created_project["id"]

        # Step 1: List keys (should be empty initially)
        list_result = inspector.call_tool(
            "list_access_keys", {"project_id": project_id}
        )
        initial_keys = parse_mcp_response(list_result)
        initial_count = len(initial_keys["access_keys"])

        # Step 2: Create a none-type key for public repo access
        create_result = inspector.call_tool(
            "create_access_key",
            {
                "project_id": project_id,
                "name": "E2E Workflow Public Key",
                "key_type": "none",
            },
        )
        created_key = parse_mcp_response(create_result)
        assert "id" in created_key
        assert created_key["type"] == "none"

        # Step 3: Verify key appears in list
        list_result = inspector.call_tool(
            "list_access_keys", {"project_id": project_id}
        )
        final_keys = parse_mcp_response(list_result)
        assert len(final_keys["access_keys"]) == initial_count + 1

        # Verify our key is in the list
        key_names = [k["name"] for k in final_keys["access_keys"]]
        assert "E2E Workflow Public Key" in key_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
