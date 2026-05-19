"""E2E tests for project backup and restore tools."""

import sys
from pathlib import Path
from uuid import uuid4

import pytest

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response  # noqa: E402
from mcp_inspector import MCPInspector  # noqa: E402


def _unique_name(prefix: str) -> str:
    return f"{prefix} {uuid4().hex[:8]}"


class TestProjectBackupsE2E:
    """E2E tests for project backup and restore workflows."""

    def test_backup_validate_and_summarize_project(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test backing up a project and inspecting the backup payload."""
        project_id = created_project["id"]

        backup_result = inspector.call_tool(
            "backup_project", {"project_id": project_id}
        )
        backup_data = parse_mcp_response(backup_result)
        backup = backup_data["backup"]

        assert backup_data["project_id"] == project_id
        assert backup["meta"]["name"] == created_project["name"]
        assert backup_data["summary"]["project_name"] == created_project["name"]

        validation_result = inspector.call_tool(
            "validate_project_backup",
            {"backup": backup},
        )
        validation = parse_mcp_response(validation_result)
        assert validation["valid"] is True
        assert validation["errors"] == []

        summary_result = inspector.call_tool(
            "summarize_project_backup",
            {"backup": backup},
        )
        summary = parse_mcp_response(summary_result)
        assert summary["project_name"] == created_project["name"]
        assert "templates" in summary["sections"]

    def test_restore_project_backup_with_name_override(
        self, inspector: MCPInspector, created_project: dict
    ):
        """Test restoring a project backup with a new project name."""
        restored_project_id = None
        restored_name = _unique_name("E2E Restored Project")

        try:
            backup_result = inspector.call_tool(
                "backup_project",
                {"project_id": created_project["id"]},
            )
            backup = parse_mcp_response(backup_result)["backup"]

            restore_result = inspector.call_tool(
                "restore_project_backup",
                {"backup": backup, "project_name": restored_name},
            )
            restored = parse_mcp_response(restore_result)
            project = restored["project"]
            restored_project_id = project["id"]

            assert project["name"] == restored_name
            assert restored["summary"]["project_name"] == restored_name

            get_result = inspector.call_tool(
                "get_project",
                {"project_id": restored_project_id},
            )
            fetched = parse_mcp_response(get_result)
            assert fetched["name"] == restored_name
        finally:
            if restored_project_id is not None:
                inspector.call_tool(
                    "delete_project",
                    {"project_id": restored_project_id},
                )

    def test_clone_project(self, inspector: MCPInspector, created_project: dict):
        """Test cloning a project through the high-level tool."""
        cloned_project_id = None
        clone_name = _unique_name("E2E Cloned Project")

        try:
            clone_result = inspector.call_tool(
                "clone_project",
                {"project_id": created_project["id"], "name": clone_name},
            )
            clone_data = parse_mcp_response(clone_result)
            project = clone_data["project"]
            cloned_project_id = project["id"]

            assert clone_data["source_project_id"] == created_project["id"]
            assert project["name"] == clone_name
            assert clone_data["summary"]["project_name"] == clone_name
        finally:
            if cloned_project_id is not None:
                inspector.call_tool(
                    "delete_project",
                    {"project_id": cloned_project_id},
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
