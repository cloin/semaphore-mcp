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

    Note: Repository operations require an SSH key ID for authentication.
    In a real E2E test environment, you would need to create a key store
    entry first. For basic testing, we test list operations and skip
    create/update tests that require SSH keys.
    """

    def test_list_repositories(self, inspector: MCPInspector, created_project: dict):
        """Test listing repositories for a project."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_repositories", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "repositories" in data
        assert isinstance(data["repositories"], list)

    @pytest.mark.skip(reason="Requires SSH key ID to be created first")
    def test_create_and_delete_repository(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test creating and deleting a repository.

        This test is skipped by default because it requires an SSH key
        to be configured in the project first.
        """
        project_id = created_project["id"]
        ssh_key_id = 1  # Would need to create a key store entry first

        # Create
        create_result = inspector.call_tool(
            "create_repository",
            {
                "project_id": project_id,
                "name": "E2E Create Test Repository",
                "git_url": "https://github.com/example/test-repo.git",
                "git_branch": "main",
                "ssh_key_id": ssh_key_id,
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

    @pytest.mark.skip(reason="Requires SSH key ID to be created first")
    def test_get_repository(self, inspector: MCPInspector, created_project: dict):
        """Test getting a specific repository.

        This test is skipped because it requires a repository to exist first.
        """
        project_id = created_project["id"]
        repository_id = 1  # Would need to create a repository first

        result = inspector.call_tool(
            "get_repository",
            {"project_id": project_id, "repository_id": repository_id},
        )
        data = parse_mcp_response(result)

        assert data["id"] == repository_id
        assert "name" in data

    @pytest.mark.skip(reason="Requires SSH key ID to be created first")
    def test_update_repository(self, inspector: MCPInspector, created_project: dict):
        """Test updating a repository.

        This test is skipped because it requires a repository to exist first.
        """
        project_id = created_project["id"]
        repository_id = 1  # Would need to create a repository first

        result = inspector.call_tool(
            "update_repository",
            {
                "project_id": project_id,
                "repository_id": repository_id,
                "name": "E2E Updated Repository",
                "git_branch": "develop",
            },
        )
        assert result is not None

    @pytest.mark.skip(reason="Requires SSH key ID to be created first")
    def test_repository_crud_workflow(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test complete repository CRUD workflow.

        This test is skipped because repository operations require
        SSH key configuration which involves creating key store entries.
        """
        project_id = created_project["id"]
        ssh_key_id = 1  # Would need to create first

        # Create
        create_result = inspector.call_tool(
            "create_repository",
            {
                "project_id": project_id,
                "name": "E2E CRUD Workflow Repository",
                "git_url": "https://github.com/example/workflow-repo.git",
                "git_branch": "main",
                "ssh_key_id": ssh_key_id,
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
                    "git_branch": "develop",
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
