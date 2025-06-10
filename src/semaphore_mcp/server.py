"""
FastMCP Server implementation for SemaphoreUI.

This module implements a Model Context Protocol server using FastMCP that exposes 
SemaphoreUI API functionality through MCP tools.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .api import SemaphoreAPIClient, create_client
from .config import configure_logging, get_config

# Configure logging
configure_logging()
logger = logging.getLogger("semaphore_mcp")


class SemaphoreMCPServer:
    """FastMCP server for SemaphoreUI."""
    
    def __init__(
            self,
            semaphore_url: Optional[str] = None,
            semaphore_token: Optional[str] = None
        ):
        """
        Initialize the MCP server.
        
        Args:
            semaphore_url: SemaphoreUI API URL
            semaphore_token: SemaphoreUI API token
        """
        # Use provided values or fall back to config
        self.url = semaphore_url or get_config("SEMAPHORE_URL")
        self.token = semaphore_token or get_config("SEMAPHORE_API_TOKEN")
        self.semaphore = create_client(self.url, self.token)
        
        # Initialize FastMCP
        self.mcp = FastMCP("semaphore")
        
        # Register tools
        self.register_tools()
    
    def register_tools(self):
        """Register all available tools."""
        self.mcp.tool()(self.list_projects)
        self.mcp.tool()(self.get_project)
        self.mcp.tool()(self.list_templates)
        self.mcp.tool()(self.get_template)
        self.mcp.tool()(self.list_tasks)
        self.mcp.tool()(self.get_task)
        self.mcp.tool()(self.run_task)
        self.mcp.tool()(self.get_task_output)
        
        # Skip environment and inventory operations as they're unstable
        # These can be re-enabled when the API compatibility issues are resolved
        # self.mcp.tool()(self.list_environments)
        # self.mcp.tool()(self.get_environment)
        # self.mcp.tool()(self.create_environment)
        # self.mcp.tool()(self.update_environment)
        # self.mcp.tool()(self.delete_environment)
        
        # self.mcp.tool()(self.list_inventory)
        # self.mcp.tool()(self.get_inventory)
        # self.mcp.tool()(self.create_inventory)
        # self.mcp.tool()(self.update_inventory)
        # self.mcp.tool()(self.delete_inventory)
    
    async def list_projects(self) -> Dict[str, Any]:
        """List all projects in SemaphoreUI.

        Returns:
            A list of projects with their details.
        """
        try:
            return self.semaphore.list_projects()
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            raise RuntimeError(f"Error listing projects: {str(e)}")
    
    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get details of a specific project.

        Args:
            project_id: ID of the project to fetch

        Returns:
            Project details
        """
        try:
            return self.semaphore.get_project(project_id)
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise RuntimeError(f"Error getting project: {str(e)}")
    
    async def list_templates(self, project_id: int) -> Dict[str, Any]:
        """List all templates for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of templates for the project
        """
        try:
            return self.semaphore.list_templates(project_id)
        except Exception as e:
            logger.error(f"Error listing templates for project {project_id}: {str(e)}")
            raise RuntimeError(f"Error listing templates: {str(e)}")
    
    async def get_template(self, project_id: int, template_id: int) -> Dict[str, Any]:
        """Get details of a specific template.

        Args:
            project_id: ID of the project
            template_id: ID of the template to fetch

        Returns:
            Template details
        """
        try:
            return self.semaphore.get_template(project_id, template_id)
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {str(e)}")
            raise RuntimeError(f"Error getting template: {str(e)}")
    
    async def list_tasks(self, project_id: int) -> Dict[str, Any]:
        """List all tasks for a project.

        Args:
            project_id: ID of the project

        Returns:
            A list of tasks for the project
        """
        try:
            return self.semaphore.list_tasks(project_id)
        except Exception as e:
            logger.error(f"Error listing tasks for project {project_id}: {str(e)}")
            raise RuntimeError(f"Error listing tasks: {str(e)}")
    
    async def get_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Get details of a specific task.

        Args:
            project_id: ID of the project
            task_id: ID of the task to fetch

        Returns:
            Task details
        """
        try:
            return self.semaphore.get_task(project_id, task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            raise RuntimeError(f"Error getting task: {str(e)}")
    
    async def run_task(self, template_id: int, environment_id: Optional[int] = None, 
                       inventory_id: Optional[int] = None, playbook: Optional[str] = None,
                       debug: bool = False, dry_run: bool = False, 
                       task_type: str = "template") -> Dict[str, Any]:
        """Run a task from a template.

        Args:
            template_id: ID of the template to run
            environment_id: Optional ID of the environment to use
            inventory_id: Optional ID of the inventory to use
            playbook: Optional playbook to use
            debug: Whether to run in debug mode
            dry_run: Whether to run in dry run mode
            task_type: Type of task to run (default: 'template')

        Returns:
            Task run result
        """
        try:
            return self.semaphore.run_task(
                template_id, 
                environment_id=environment_id,
                inventory_id=inventory_id,
                playbook=playbook,
                debug=debug,
                dry_run=dry_run,
                task_type=task_type
            )
        except Exception as e:
            logger.error(f"Error running task for template {template_id}: {str(e)}")
            raise RuntimeError(f"Error running task: {str(e)}")
    
    async def get_task_output(self, task_id: int) -> str:
        """Get output from a completed task.

        Args:
            task_id: ID of the task

        Returns:
            Task output
        """
        try:
            output = self.semaphore.get_task_output(task_id)
            # Format output nicely
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Error getting output for task {task_id}: {str(e)}")
            raise RuntimeError(f"Error getting task output: {str(e)}")
    
    def run(self):
        """Run the MCP server."""
        logger.info(f"Starting FastMCP server for SemaphoreUI at {self.url}")
        self.mcp.run(transport='stdio')


def start_server(semaphore_url: Optional[str] = None, 
                semaphore_token: Optional[str] = None):
    """
    Start an MCP server.
    
    Args:
        semaphore_url: SemaphoreUI API URL
        semaphore_token: SemaphoreUI API token
    """
    server = SemaphoreMCPServer(semaphore_url, semaphore_token)
    server.run()


if __name__ == "__main__":
    start_server()
