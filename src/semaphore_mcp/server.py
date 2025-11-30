"""
FastMCP Server implementation for SemaphoreUI.

This module implements a Model Context Protocol server using FastMCP that exposes
SemaphoreUI API functionality through MCP tools.
"""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .api import create_client
from .config import configure_logging, get_config
from .tools.access_keys import AccessKeyTools
from .tools.environments import EnvironmentTools
from .tools.projects import ProjectTools
from .tools.repositories import RepositoryTools
from .tools.tasks import TaskTools
from .tools.templates import TemplateTools

# Configure logging
configure_logging()
logger = logging.getLogger("semaphore_mcp")


class SemaphoreMCPServer:
    """FastMCP server for SemaphoreUI."""

    def __init__(
        self,
        semaphore_url: Optional[str] = None,
        semaphore_token: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        """
        Initialize the MCP server.

        Args:
            semaphore_url: SemaphoreUI API URL
            semaphore_token: SemaphoreUI API token
            host: Host to bind to (for HTTP transport)
            port: Port to listen on (for HTTP transport)
        """
        # Use provided values or fall back to config
        self.url = semaphore_url or get_config("SEMAPHORE_URL")
        self.token = semaphore_token or get_config("SEMAPHORE_API_TOKEN")
        self.semaphore = create_client(self.url, self.token)

        # Initialize FastMCP with host/port for HTTP transport
        self.mcp = FastMCP("semaphore", host=host, port=port)

        # Initialize tool classes
        self.project_tools = ProjectTools(self.semaphore)
        self.template_tools = TemplateTools(self.semaphore)
        self.task_tools = TaskTools(self.semaphore)
        self.environment_tools = EnvironmentTools(self.semaphore)
        self.repository_tools = RepositoryTools(self.semaphore)
        self.access_key_tools = AccessKeyTools(self.semaphore)

        # Register tools
        self.register_tools()

    def register_tools(self):
        """Register MCP tools for SemaphoreUI."""
        # Project tools
        self.mcp.tool()(self.project_tools.list_projects)
        self.mcp.tool()(self.project_tools.get_project)
        self.mcp.tool()(self.project_tools.create_project)
        self.mcp.tool()(self.project_tools.update_project)
        self.mcp.tool()(self.project_tools.delete_project)

        # Template tools
        self.mcp.tool()(self.template_tools.list_templates)
        self.mcp.tool()(self.template_tools.get_template)
        self.mcp.tool()(self.template_tools.create_template)
        self.mcp.tool()(self.template_tools.update_template)
        self.mcp.tool()(self.template_tools.delete_template)
        self.mcp.tool()(self.template_tools.stop_all_template_tasks)

        # Task tools
        self.mcp.tool()(self.task_tools.list_tasks)
        self.mcp.tool()(self.task_tools.get_task)
        self.mcp.tool()(self.task_tools.run_task)
        self.mcp.tool()(self.task_tools.get_latest_failed_task)

        # Enhanced task tools - filtering and bulk operations
        self.mcp.tool()(self.task_tools.filter_tasks)
        self.mcp.tool()(self.task_tools.stop_task)
        self.mcp.tool()(self.task_tools.bulk_stop_tasks)
        self.mcp.tool()(self.task_tools.get_waiting_tasks)

        # LLM-based failure analysis tools
        self.mcp.tool()(self.task_tools.get_task_raw_output)
        self.mcp.tool()(self.task_tools.analyze_task_failure)
        self.mcp.tool()(self.task_tools.bulk_analyze_failures)

        # Optional: Task restart operations (if needed)
        # self.mcp.tool()(self.task_tools.restart_task)
        # self.mcp.tool()(self.task_tools.bulk_restart_tasks)

        # Environment tools
        self.mcp.tool()(self.environment_tools.list_environments)
        self.mcp.tool()(self.environment_tools.get_environment)
        self.mcp.tool()(self.environment_tools.create_environment)
        self.mcp.tool()(self.environment_tools.update_environment)
        self.mcp.tool()(self.environment_tools.delete_environment)

        # Inventory tools
        self.mcp.tool()(self.environment_tools.list_inventory)
        self.mcp.tool()(self.environment_tools.get_inventory)
        self.mcp.tool()(self.environment_tools.create_inventory)
        self.mcp.tool()(self.environment_tools.update_inventory)
        self.mcp.tool()(self.environment_tools.delete_inventory)

        # Repository tools
        self.mcp.tool()(self.repository_tools.list_repositories)
        self.mcp.tool()(self.repository_tools.get_repository)
        self.mcp.tool()(self.repository_tools.create_repository)
        self.mcp.tool()(self.repository_tools.update_repository)
        self.mcp.tool()(self.repository_tools.delete_repository)

        # Access key tools (limited to safe operations)
        self.mcp.tool()(self.access_key_tools.list_access_keys)
        self.mcp.tool()(self.access_key_tools.create_access_key)

    # Tool methods have been moved to dedicated tool classes

    def run(self, transport: str = "stdio"):
        """Run the MCP server.

        Args:
            transport: Transport type - "stdio" or "http"
        """
        logger.info(f"Starting FastMCP server for SemaphoreUI at {self.url}")
        if transport == "http":
            logger.info(
                f"HTTP transport on {self.mcp.settings.host}:{self.mcp.settings.port}"
            )
            self.mcp.run(transport="streamable-http")
        else:
            logger.info("STDIO transport")
            self.mcp.run(transport="stdio")


def start_server(
    semaphore_url: Optional[str] = None,
    semaphore_token: Optional[str] = None,
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """
    Start an MCP server.

    Args:
        semaphore_url: SemaphoreUI API URL
        semaphore_token: SemaphoreUI API token
        transport: Transport type - "stdio" or "http"
        host: Host to bind to (for HTTP transport)
        port: Port to listen on (for HTTP transport)
    """
    server = SemaphoreMCPServer(semaphore_url, semaphore_token, host=host, port=port)
    server.run(transport=transport)


if __name__ == "__main__":
    start_server()
