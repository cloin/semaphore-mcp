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
        """Register MCP tools for SemaphoreUI."""
        self.mcp.tool()(self.list_projects)
        self.mcp.tool()(self.get_project)
        self.mcp.tool()(self.list_templates)
        self.mcp.tool()(self.get_template)
        self.mcp.tool()(self.list_tasks)
        self.mcp.tool()(self.get_task)
        self.mcp.tool()(self.run_task)
        self.mcp.tool()(self.get_task_output)
        self.mcp.tool()(self.get_latest_failed_task)
        
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
    
    async def list_tasks(self, project_id: int, limit: int = 5) -> Dict[str, Any]:
        """List tasks for a project with a default limit of 5 to avoid overloading context windows.

        Args:
            project_id: ID of the project
            limit: Maximum number of tasks to return (default: 5)

        Returns:
            A list of tasks for the project, limited by the specified count
        """
        try:
            # Warn if a large number of tasks is requested
            if limit > 5:
                logger.warning(f"Requesting {limit} tasks may overload the context window")
            
            # Get all tasks from the API
            api_response = self.semaphore.list_tasks(project_id)
            
            # Handle different response formats (list or dict with 'tasks' key)
            all_tasks = []
            if isinstance(api_response, list):
                all_tasks = api_response
            elif isinstance(api_response, dict) and "tasks" in api_response:
                all_tasks = api_response.get("tasks", [])
            
            # Sort tasks by creation time (newest first)
            sorted_tasks = sorted(
                all_tasks, 
                key=lambda x: x.get("created", "") if isinstance(x, dict) else "", 
                reverse=True
            )
            
            # Return only the limited number of tasks
            limited_tasks = sorted_tasks[:limit]
            
            return {
                "tasks": limited_tasks,
                "total": len(all_tasks),
                "shown": len(limited_tasks),
                "note": f"Showing {len(limited_tasks)} of {len(all_tasks)} tasks (sorted by newest first)"
            }
        except Exception as e:
            logger.error(f"Error listing tasks for project {project_id}: {str(e)}")
            raise RuntimeError(f"Error listing tasks: {str(e)}")
            
    async def get_latest_failed_task(self, project_id: int) -> Dict[str, Any]:
        """Get the most recent failed task for a project.

        Args:
            project_id: ID of the project

        Returns:
            The most recent failed task or a message if no failed tasks are found
        """
        try:
            # Get all tasks from the API
            api_response = self.semaphore.list_tasks(project_id)
            
            # Handle different response formats (list or dict with 'tasks' key)
            tasks = []
            if isinstance(api_response, list):
                tasks = api_response
            elif isinstance(api_response, dict) and "tasks" in api_response:
                tasks = api_response.get("tasks", [])
            
            # Filter for failed tasks and sort by creation time (newest first)
            failed_tasks = [t for t in tasks if isinstance(t, dict) and t.get("status") == "error"]
            sorted_failed = sorted(
                failed_tasks, 
                key=lambda x: x.get("created", ""), 
                reverse=True
            )
            
            if not sorted_failed:
                return {"message": "No failed tasks found for this project"}
                
            # Return the most recent failed task
            return {"task": sorted_failed[0]}
        except Exception as e:
            logger.error(f"Error getting latest failed task for project {project_id}: {str(e)}")
            raise RuntimeError(f"Error getting latest failed task: {str(e)}")
    
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
