"""
Task-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore tasks.
"""
import json
import logging
import requests
from typing import Dict, Any, List, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)

class TaskTools(BaseTool):
    """Tools for working with Semaphore tasks."""
    
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
            self.handle_error(e, f"listing tasks for project {project_id}")
    
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
            self.handle_error(e, f"getting latest failed task for project {project_id}")
    
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
            self.handle_error(e, f"getting task {task_id}")
    
    async def run_task(self, template_id: int, project_id: Optional[int] = None, 
                      environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run a task from a template.

        Args:
            template_id: ID of the template to run
            project_id: Optional project ID (if not provided, will attempt to determine from template)
            environment: Optional environment variables for the task as dictionary

        Returns:
            Task run result
        """
        try:
            # If project_id is not provided, we need to find it
            if not project_id:
                # First get all projects
                projects = self.semaphore.list_projects()
                
                # Handle different response formats
                project_list = []
                if isinstance(projects, list):
                    project_list = projects
                elif isinstance(projects, dict) and "projects" in projects:
                    project_list = projects["projects"]
                    
                # If we have projects, try to look at templates for each project
                found = False
                if project_list:
                    for proj in project_list:
                        try:
                            proj_id = proj["id"]
                            templates = self.semaphore.list_templates(proj_id)
                            
                            # Handle different response formats for templates
                            template_list = []
                            if isinstance(templates, list):
                                template_list = templates
                            elif isinstance(templates, dict) and "templates" in templates:
                                template_list = templates["templates"]
                            
                            # Check if our template ID is in this project's templates
                            for tmpl in template_list:
                                if tmpl["id"] == template_id:
                                    project_id = proj_id
                                    found = True
                                    break
                                    
                            if found:
                                break
                                
                        except Exception as template_err:
                            logger.warning(f"Error checking templates in project {proj['id']}: {str(template_err)}")
                            continue
                
                if not project_id:
                    raise RuntimeError(f"Could not determine project_id for template {template_id}. Please provide it explicitly.")
            
            # Now run the task with the determined project_id
            try:
                return self.semaphore.run_task(project_id, template_id, environment=environment)
            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code if hasattr(http_err, 'response') and hasattr(http_err.response, 'status_code') else 'unknown'
                error_msg = f"HTTP error {status_code} when running task: {str(http_err)}"
                if status_code == 400 and environment:
                    error_msg += ". The 400 Bad Request might be related to unsupported environment variables"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            except Exception as e:
                logger.error(f"Error running task for template {template_id} in project {project_id}: {str(e)}")
                raise RuntimeError(f"Error running task: {str(e)}")
        except Exception as e:
            logger.error(f"Error in project/template lookup for template {template_id}: {str(e)}")
            raise RuntimeError(f"Error preparing to run task: {str(e)}")
    
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
            self.handle_error(e, f"getting output for task {task_id}")
