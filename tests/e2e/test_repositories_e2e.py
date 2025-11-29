"""E2E tests for Repository tools."""

import sys
from pathlib import Path

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


class TestRepositoriesE2E:
    """E2E tests for repository CRUD operations.

    These tests use the created_access_key fixture which provides a 'none' type
    access key suitable for public repositories.
    """

    def test_list_repositories(self, inspector: MCPInspector, created_project: dict):
        """Test listing repositories for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_repositories", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "repositories" in data
        assert isinstance(data["repositories"], list)

    def test_create_and_delete_repository(
        self, inspector: MCPInspector, created_project: dict, created_access_key: tuple
    ):
        """Test creating and deleting a repository."""
        project_id = created_project["id"]
        access_key, _ = created_access_key

        # Create
        create_result = inspector.call_tool(
            "create_repository",
            {
                "project_id": project_id,
                "name": "E2E Create Test Repository",
                "git_url": "https://github.com/cloin/ansible-test",
                "git_branch": "main",
                "ssh_key_id": access_key["id"],
            },
        )
        repository = parse_mcp_response(create_result)

        assert "id" in repository
        assert repository["name"] == "E2E Create Test Repository"

        repository_id = repository["id"]

        # Delete
        delete_result = inspector.call_tool(
            "delete_repository",
            {"project_id": project_id, "repository_id": repository_id},
        )
        assert delete_result is not None

    def test_get_repository(self, inspector: MCPInspector, created_repository: tuple):
        """Test getting a specific repository."""
        repository, project_id = created_repository

        result = inspector.call_tool(
            "get_repository",
            {"project_id": project_id, "repository_id": repository["id"]},
        )
        data = parse_mcp_response(result)

        assert data["id"] == repository["id"]
        assert "name" in data

    def test_update_repository(
        self, inspector: MCPInspector, created_repository: tuple
    ):
        """Test updating a repository."""
        repository, project_id = created_repository

        result = inspector.call_tool(
            "update_repository",
            {
                "project_id": project_id,
                "repository_id": repository["id"],
                "name": "E2E Updated Repository",
                "git_branch": "main",  # Keep same branch since we're using a real repo
            },
        )
        assert result is not None

        # Verify the update
        get_result = inspector.call_tool(
            "get_repository",
            {"project_id": project_id, "repository_id": repository["id"]},
        )
        updated = parse_mcp_response(get_result)
        assert updated["name"] == "E2E Updated Repository"

    def test_repository_crud_workflow(
        self, inspector: MCPInspector, created_project: dict, created_access_key: tuple
    ):
        """Test complete repository CRUD workflow."""
        project_id = created_project["id"]
        access_key, _ = created_access_key

        # Create
        create_result = inspector.call_tool(
            "create_repository",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Repository",
                "git_url": "https://github.com/cloin/ansible-test",
                "git_branch": "main",
                "ssh_key_id": access_key["id"],
            },
        )
        repository = parse_mcp_response(create_result)
        assert "id" in repository
        repository_id = repository["id"]

        try:
            # Read
            get_result = inspector.call_tool(
                "get_repository",
                {"project_id": project_id, "repository_id": repository_id},
            )
            read_repo = parse_mcp_response(get_result)
            assert read_repo["id"] == repository_id

            # Update
            inspector.call_tool(
                "update_repository",
                {
                    "project_id": project_id,
                    "repository_id": repository_id,
                    "name": "E2E CRUD Updated Repo",
                    "git_branch": "main",
                },
            )

            # Verify update
            get_result = inspector.call_tool(
                "get_repository",
                {"project_id": project_id, "repository_id": repository_id},
            )
            updated_repo = parse_mcp_response(get_result)
            assert updated_repo["name"] == "E2E CRUD Updated Repo"

            # List and verify repository is in list
            list_result = inspector.call_tool(
                "list_repositories", {"project_id": project_id}
            )
            repos_data = parse_mcp_response(list_result)
            repo_ids = [r["id"] for r in repos_data["repositories"]]
            assert repository_id in repo_ids

        finally:
            # Delete (cleanup)
            inspector.call_tool(
                "delete_repository",
                {"project_id": project_id, "repository_id": repository_id},
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
