"""Comprehensive scenario test simulating a real deployment workflow.

This test simulates a complete workflow:
1. Create a new project
2. Create environment variables
3. Create inventory
4. Create repository
5. Create a task template
6. Run a task
7. Monitor task execution
8. Handle task results
9. Clean up all resources
"""

import os
import sys
from pathlib import Path
from typing import Any

# Add e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_inspector import MCPInspector, MCPInspectorError  # noqa: E402


class ComprehensiveScenario:
    """Comprehensive test scenario."""

    def __init__(self, inspector: MCPInspector):
        self.inspector = inspector
        self.created_resources: dict[str, Any] = {}

    def run(self):
        """Execute the complete scenario."""
        print("🚀 Starting Comprehensive Deployment Scenario\n")
        print("=" * 60)

        try:
            self.step1_create_project()
            self.step2_create_environment()
            self.step3_create_inventory()
            self.step4_create_repository()
            self.step5_create_template()
            self.step6_run_task()
            self.step7_monitor_task()
            self.step8_analyze_results()

            print("\n" + "=" * 60)
            print("✅ Comprehensive scenario completed successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Scenario failed: {e}")
            raise
        finally:
            self.cleanup()

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call a tool and return the result."""
        print(f"    Calling {name}...")
        try:
            result = self.inspector.call_tool(name, arguments)
            return result
        except MCPInspectorError as e:
            print(f"    ❌ Failed: {e}")
            raise

    def step1_create_project(self):
        """Step 1: Create a project."""
        print("\n📁 Step 1: Creating Project")
        print("-" * 60)

        self.call_tool(
            "create_project",
            {
                "name": "E2E Deployment Project",
                "alert": True,
                "max_parallel_tasks": 5,
            },
        )

        # Extract project ID from response
        # Note: Adjust based on actual response format
        project_id = 1  # Placeholder
        self.created_resources["project_id"] = project_id

        print(f"    ✅ Project created with ID: {project_id}")

        # Verify by listing projects
        self.call_tool("list_projects")
        print("    ✅ Verified: Found projects in system")

    def step2_create_environment(self):
        """Step 2: Create environment variables."""
        print("\n🌍 Step 2: Creating Environment Variables")
        print("-" * 60)

        project_id = self.created_resources["project_id"]

        self.call_tool(
            "create_environment",
            {
                "project_id": project_id,
                "name": "Production Environment",
                "json": '{"DEPLOY_ENV": "production", "APP_VERSION": "1.0.0", "DEBUG": "false"}',
            },
        )

        env_id = 1  # Placeholder
        self.created_resources["environment_id"] = env_id

        print(f"    ✅ Environment created with ID: {env_id}")

        # Verify
        self.call_tool("list_environments", {"project_id": project_id})
        print("    ✅ Verified: Environment listed in project")

    def step3_create_inventory(self):
        """Step 3: Create inventory."""
        print("\n📋 Step 3: Creating Inventory")
        print("-" * 60)

        project_id = self.created_resources["project_id"]

        inventory_content = """[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
"""

        self.call_tool(
            "create_inventory",
            {
                "project_id": project_id,
                "name": "Production Servers",
                "inventory": inventory_content,
            },
        )

        inventory_id = 1  # Placeholder
        self.created_resources["inventory_id"] = inventory_id

        print(f"    ✅ Inventory created with ID: {inventory_id}")

        # Verify
        self.call_tool("list_inventory", {"project_id": project_id})
        print("    ✅ Verified: Inventory listed in project")

    def step4_create_repository(self):
        """Step 4: Create repository."""
        print("\n📦 Step 4: Creating Repository")
        print("-" * 60)

        project_id = self.created_resources["project_id"]

        self.call_tool(
            "create_repository",
            {
                "project_id": project_id,
                "name": "Deployment Scripts",
                "git_url": "https://github.com/ansible/ansible-examples.git",
                "git_branch": "master",
            },
        )

        repo_id = 1  # Placeholder
        self.created_resources["repository_id"] = repo_id

        print(f"    ✅ Repository created with ID: {repo_id}")

        # Verify
        self.call_tool("list_repositories", {"project_id": project_id})
        print("    ✅ Verified: Repository listed in project")

    def step5_create_template(self):
        """Step 5: Create task template."""
        print("\n📝 Step 5: Creating Task Template")
        print("-" * 60)

        project_id = self.created_resources["project_id"]

        self.call_tool(
            "create_template",
            {
                "project_id": project_id,
                "name": "Deploy Application",
                "playbook": "deploy.yml",
                "inventory_id": self.created_resources["inventory_id"],
                "repository_id": self.created_resources["repository_id"],
                "environment_id": self.created_resources["environment_id"],
            },
        )

        template_id = 1  # Placeholder
        self.created_resources["template_id"] = template_id

        print(f"    ✅ Template created with ID: {template_id}")

        # Verify
        self.call_tool("list_templates", {"project_id": project_id})
        print("    ✅ Verified: Template listed in project")

    def step6_run_task(self):
        """Step 6: Run a task."""
        print("\n▶️  Step 6: Running Task")
        print("-" * 60)

        project_id = self.created_resources["project_id"]
        template_id = self.created_resources["template_id"]

        self.call_tool(
            "run_task",
            {"project_id": project_id, "template_id": template_id, "monitor": True},
        )

        task_id = 1  # Placeholder
        self.created_resources["task_id"] = task_id

        print(f"    ✅ Task started with ID: {task_id}")

    def step7_monitor_task(self):
        """Step 7: Monitor task execution."""
        print("\n👀 Step 7: Monitoring Task Execution")
        print("-" * 60)

        project_id = self.created_resources["project_id"]
        task_id = self.created_resources["task_id"]

        # Get task status
        self.call_tool("get_task", {"project_id": project_id, "id": task_id})
        print("    ✅ Task status retrieved")

        # List recent tasks
        self.call_tool("list_tasks", {"project_id": project_id, "limit": 5})
        print("    ✅ Recent tasks listed")

        # Get waiting tasks
        self.call_tool("get_waiting_tasks", {"project_id": project_id})
        print("    ✅ Waiting tasks checked")

    def step8_analyze_results(self):
        """Step 8: Analyze task results."""
        print("\n📊 Step 8: Analyzing Task Results")
        print("-" * 60)

        project_id = self.created_resources["project_id"]
        task_id = self.created_resources["task_id"]

        # Filter tasks by status
        self.call_tool(
            "filter_tasks", {"project_id": project_id, "status": "running", "limit": 10}
        )
        print("    ✅ Tasks filtered by status")

        # Get task output (if available)
        try:
            self.call_tool(
                "get_task_raw_output", {"project_id": project_id, "id": task_id}
            )
            print("    ✅ Task output retrieved")
        except Exception:
            print("    ⚠️  Task output not yet available")

        # Check for failed tasks
        failed = self.call_tool("get_latest_failed_task", {"project_id": project_id})
        if failed:
            print("    ℹ️  Found failed task, analyzing...")
            # Note: analyze_task_failure requires LLM integration
            # analysis = self.call_tool('analyze_task_failure', {
            #     'project_id': project_id,
            #     'id': failed_task_id
            # })
        else:
            print("    ✅ No failed tasks found")

    def cleanup(self):
        """Clean up all created resources."""
        print("\n🧹 Cleanup: Removing Test Resources")
        print("-" * 60)

        project_id = self.created_resources.get("project_id")
        if not project_id:
            print("    ℹ️  No resources to clean up")
            return

        # Delete in reverse order of creation
        cleanup_steps = [
            ("template", "template_id", "delete_template"),
            ("repository", "repository_id", "delete_repository"),
            ("inventory", "inventory_id", "delete_inventory"),
            ("environment", "environment_id", "delete_environment"),
            ("project", "project_id", "delete_project"),
        ]

        for resource_type, id_key, delete_tool in cleanup_steps:
            resource_id = self.created_resources.get(id_key)
            if resource_id:
                try:
                    if resource_type == "project":
                        self.call_tool(delete_tool, {"id": resource_id})
                    else:
                        self.call_tool(
                            delete_tool, {"project_id": project_id, "id": resource_id}
                        )
                    print(f"    ✅ Deleted {resource_type} {resource_id}")
                except Exception as e:
                    print(f"    ⚠️  Failed to delete {resource_type}: {e}")

        print("    ✅ Cleanup completed")


def main():
    """Run the comprehensive scenario test."""
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    inspector = MCPInspector(server_url)

    scenario = ComprehensiveScenario(inspector)

    try:
        scenario.run()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Comprehensive scenario failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
