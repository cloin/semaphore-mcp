"""E2E tests for project user tools."""

import os
import sys
import uuid
from pathlib import Path

import pytest
import requests

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


@pytest.fixture
def semaphore_admin_headers():
    """Return admin API headers for direct Semaphore setup calls."""
    token = os.getenv("SEMAPHORE_API_TOKEN")
    if not token:
        pytest.skip("SEMAPHORE_API_TOKEN is required for project user E2E setup")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def temporary_semaphore_user(semaphore_admin_headers):
    """Create a temporary global Semaphore user for project membership tests."""
    semaphore_url = os.getenv("SEMAPHORE_URL", "http://localhost:3000").rstrip("/")
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "name": f"E2E Project User {suffix}",
        "username": f"e2e-project-user-{suffix}",
        "email": f"e2e-project-user-{suffix}@localhost",
        "password": f"E2E-{suffix}-Password-123!",
        "alert": False,
        "admin": False,
        "external": False,
    }

    response = requests.post(
        f"{semaphore_url}/api/users",
        headers=semaphore_admin_headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    user = response.json()

    yield user

    try:
        requests.delete(
            f"{semaphore_url}/api/users/{user['id']}/",
            headers=semaphore_admin_headers,
            timeout=30,
        )
    except Exception:
        pass


class TestProjectUsersE2E:
    """E2E tests for project user operations."""

    def test_get_project_role(self, inspector: MCPInspector, created_project: dict):
        """Test getting the current user's project role."""
        project_id = created_project["id"]

        result = inspector.call_tool("get_project_role", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert data["role"] == "owner"
        assert "permissions" in data

    def test_list_project_users(self, inspector: MCPInspector, created_project: dict):
        """Test listing users linked to a project."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "list_project_users",
            {"project_id": project_id, "sort": "username", "order": "asc"},
        )
        data = parse_mcp_response(result)

        assert "users" in data
        assert isinstance(data["users"], list)
        assert any(user["role"] == "owner" for user in data["users"])

    def test_project_user_membership_workflow(
        self,
        inspector: MCPInspector,
        created_project: dict,
        temporary_semaphore_user: dict,
    ):
        """Test adding, updating, listing, and removing a project user."""
        project_id = created_project["id"]
        user_id = temporary_semaphore_user["id"]
        linked = False

        try:
            add_result = inspector.call_tool(
                "add_project_user",
                {"project_id": project_id, "user_id": user_id, "role": "guest"},
            )
            assert add_result is not None
            linked = True

            list_result = inspector.call_tool(
                "list_project_users",
                {"project_id": project_id, "sort": "username", "order": "asc"},
            )
            users = parse_mcp_response(list_result)["users"]
            linked_user = next(user for user in users if user["id"] == user_id)
            assert linked_user["role"] == "guest"

            update_result = inspector.call_tool(
                "update_project_user",
                {"project_id": project_id, "user_id": user_id, "role": "manager"},
            )
            assert update_result is not None

            list_result = inspector.call_tool(
                "list_project_users",
                {"project_id": project_id, "sort": "username", "order": "asc"},
            )
            users = parse_mcp_response(list_result)["users"]
            linked_user = next(user for user in users if user["id"] == user_id)
            assert linked_user["role"] == "manager"

        finally:
            if linked:
                inspector.call_tool(
                    "remove_project_user",
                    {"project_id": project_id, "user_id": user_id},
                )

        list_result = inspector.call_tool(
            "list_project_users",
            {"project_id": project_id, "sort": "username", "order": "asc"},
        )
        users = parse_mcp_response(list_result)["users"]
        assert user_id not in [user["id"] for user in users]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
