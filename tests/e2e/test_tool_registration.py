"""Test that all expected MCP tools are registered."""

import os
import sys
from pathlib import Path

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_inspector import MCPInspector  # noqa: E402

# Expected tools organized by category
EXPECTED_TOOLS = {
    # Project tools (5)
    "list_projects",
    "get_project",
    "create_project",
    "update_project",
    "delete_project",
    # Template tools (6)
    "list_templates",
    "get_template",
    "create_template",
    "update_template",
    "delete_template",
    "stop_all_template_tasks",
    # Task tools (11) - restart_task and bulk_restart_tasks are commented out in tasks.py
    "list_tasks",
    "get_task",
    "run_task",
    "stop_task",
    "get_latest_failed_task",
    "filter_tasks",
    "bulk_stop_tasks",
    "get_waiting_tasks",
    "get_task_raw_output",
    "analyze_task_failure",
    "bulk_analyze_failures",
    # Environment tools (10)
    "list_environments",
    "get_environment",
    "create_environment",
    "update_environment",
    "delete_environment",
    "list_inventory",
    "get_inventory",
    "create_inventory",
    "update_inventory",
    "delete_inventory",
    # Repository tools (5)
    "list_repositories",
    "get_repository",
    "create_repository",
    "update_repository",
    "delete_repository",
}


def test_tool_registration():
    """Test that all expected tools are registered with the MCP server."""
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    inspector = MCPInspector(server_url)

    print(f"🔍 Testing tool registration at {server_url}")

    # List all tools
    try:
        tools = inspector.list_tools()
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        sys.exit(1)

    # Extract tool names
    registered_tools = {tool["name"] for tool in tools}

    print(f"✅ Found {len(registered_tools)} registered tools")

    # Check for missing tools
    missing_tools = EXPECTED_TOOLS - registered_tools
    if missing_tools:
        print(f"❌ Missing tools: {sorted(missing_tools)}")
        sys.exit(1)

    # Check for unexpected tools
    unexpected_tools = registered_tools - EXPECTED_TOOLS
    if unexpected_tools:
        print(f"⚠️  Unexpected tools: {sorted(unexpected_tools)}")

    print(f"✅ All {len(EXPECTED_TOOLS)} expected tools are registered")

    # Verify each tool has required fields
    print("\n📋 Tool Details:")
    for tool in sorted(tools, key=lambda t: t["name"]):
        name = tool["name"]
        description = tool.get("description", "No description")
        input_schema = tool.get("inputSchema", {})
        required = input_schema.get("required", [])

        print(f"  • {name}")
        print(f"    Description: {description[:80]}...")
        if required:
            print(f"    Required params: {', '.join(required)}")

    print("\n✅ Tool registration test passed!")


if __name__ == "__main__":
    test_tool_registration()
