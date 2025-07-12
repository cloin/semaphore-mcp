"""
Task-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore tasks.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests  # type: ignore

from .base import BaseTool

logger = logging.getLogger(__name__)


class TaskTools(BaseTool):
    """Tools for working with Semaphore tasks."""

    # Status mapping for user-friendly names
    STATUS_MAPPING = {
        "successful": "success",
        "failed": "error",
        "running": "running",
        "waiting": "waiting",
        "stopped": "stopped",  # May need to verify this mapping
    }

    async def list_tasks(
        self,
        project_id: int,
        limit: int = 5,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """List tasks for a project with a default limit of 5 to avoid overloading context windows.

        Args:
            project_id: ID of the project
            limit: Maximum number of tasks to return (default: 5)
            status: Optional status filter (e.g., 'success', 'error', 'running')
            tags: Optional list of tags to filter by

        Returns:
            A list of tasks for the project, limited by the specified count
        """
        try:
            # Warn if a large number of tasks is requested
            if limit > 5:
                logger.warning(
                    f"Requesting {limit} tasks may overload the context window"
                )

            # Get all tasks from the API
            api_response = self.semaphore.list_tasks(project_id)

            # Handle different response formats (list or dict with 'tasks' key)
            all_tasks = []
            if isinstance(api_response, list):
                all_tasks = api_response
            elif isinstance(api_response, dict) and "tasks" in api_response:
                all_tasks = api_response.get("tasks", [])

            # Filter tasks by status and tags if provided
            filtered_tasks = all_tasks
            if status:
                filtered_tasks = [
                    t
                    for t in filtered_tasks
                    if t.get("status") == self.STATUS_MAPPING.get(status)
                ]
            if tags:
                filtered_tasks = [
                    t
                    for t in filtered_tasks
                    if all(tag in t.get("tags", []) for tag in tags)
                ]

            # Sort tasks by creation time (newest first)
            sorted_tasks = sorted(
                filtered_tasks,
                key=lambda x: x.get("created", "") if isinstance(x, dict) else "",
                reverse=True,
            )

            # Return only the limited number of tasks
            limited_tasks = sorted_tasks[:limit]

            return {
                "tasks": limited_tasks,
                "total": len(all_tasks),
                "shown": len(limited_tasks),
                "note": f"Showing {len(limited_tasks)} of {len(all_tasks)} tasks (sorted by newest first)",
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
            failed_tasks = [
                t for t in tasks if isinstance(t, dict) and t.get("status") == "error"
            ]
            sorted_failed = sorted(
                failed_tasks, key=lambda x: x.get("created", ""), reverse=True
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

    async def run_task(
        self,
        template_id: int,
        project_id: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
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
                            elif (
                                isinstance(templates, dict) and "templates" in templates
                            ):
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
                            logger.warning(
                                f"Error checking templates in project {proj['id']}: {str(template_err)}"
                            )
                            continue

                if not project_id:
                    raise RuntimeError(
                        f"Could not determine project_id for template {template_id}. Please provide it explicitly."
                    )

            # Now run the task with the determined project_id
            try:
                return self.semaphore.run_task(
                    project_id, template_id, environment=environment
                )
            except requests.exceptions.HTTPError as http_err:
                status_code = (
                    http_err.response.status_code
                    if hasattr(http_err, "response")
                    and hasattr(http_err.response, "status_code")
                    else "unknown"
                )
                error_msg = (
                    f"HTTP error {status_code} when running task: {str(http_err)}"
                )
                if status_code == 400 and environment:
                    error_msg += ". The 400 Bad Request might be related to unsupported environment variables"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            except Exception as e:
                logger.error(
                    f"Error running task for template {template_id} in project {project_id}: {str(e)}"
                )
                raise RuntimeError(f"Error running task: {str(e)}")
        except Exception as e:
            logger.error(
                f"Error in project/template lookup for template {template_id}: {str(e)}"
            )
            raise RuntimeError(f"Error preparing to run task: {str(e)}")

    async def get_task_output(self, project_id: int, task_id: int) -> str:
        """Get output from a completed task.

        Args:
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Task output
        """
        try:
            output = self.semaphore.get_task_output(project_id, task_id)
            # Format output nicely
            return json.dumps(output, indent=2)
        except Exception as e:
            self.handle_error(e, f"getting output for task {task_id}")

    async def stop_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Stop a running task.

        Args:
            project_id: ID of the project
            task_id: ID of the task to stop

        Returns:
            Task stop result
        """
        try:
            return self.semaphore.stop_task(project_id, task_id)
        except Exception as e:
            self.handle_error(e, f"stopping task {task_id}")

    async def filter_tasks(
        self,
        project_id: int,
        status: Optional[List[str]] = None,
        limit: int = 50,
        use_last_tasks: bool = True,
    ) -> Dict[str, Any]:
        """Filter tasks by multiple criteria with bulk operation support.

        Args:
            project_id: ID of the project
            status: List of statuses to filter by (e.g., ['success', 'error'])
            limit: Maximum number of tasks to return
            use_last_tasks: Use efficient last 200 tasks endpoint

        Returns:
            Filtered tasks with statistics
        """
        try:
            # Get tasks using efficient endpoint if available
            if use_last_tasks:
                try:
                    api_response = self.semaphore.get_last_tasks(project_id)
                except Exception:
                    # Fallback to regular list if last_tasks fails
                    api_response = self.semaphore.list_tasks(project_id)
            else:
                api_response = self.semaphore.list_tasks(project_id)

            # Handle different response formats
            all_tasks = []
            if isinstance(api_response, list):
                all_tasks = api_response
            elif isinstance(api_response, dict) and "tasks" in api_response:
                all_tasks = api_response.get("tasks", [])

            # Apply status filters
            filtered_tasks = all_tasks
            if status:
                # Convert user-friendly status names to API status values
                api_statuses = [self.STATUS_MAPPING.get(s, s) for s in status]
                filtered_tasks = [
                    t for t in filtered_tasks if t.get("status") in api_statuses
                ]

            # Sort by creation time (newest first)
            sorted_tasks = sorted(
                filtered_tasks,
                key=lambda x: x.get("created", "") if isinstance(x, dict) else "",
                reverse=True,
            )

            # Apply limit
            limited_tasks = sorted_tasks[:limit]

            # Generate statistics
            stats: Dict[str, Union[int, Dict[str, int]]] = {
                "total_tasks": len(all_tasks),
                "filtered_tasks": len(filtered_tasks),
                "returned_tasks": len(limited_tasks),
            }

            # Status breakdown
            if filtered_tasks:
                status_counts: Dict[str, int] = {}
                for task in filtered_tasks:
                    task_status = task.get("status", "unknown")
                    status_counts[task_status] = status_counts.get(task_status, 0) + 1
                stats["status_breakdown"] = status_counts

            return {
                "tasks": limited_tasks,
                "statistics": stats,
                "note": f"Showing {len(limited_tasks)} of {len(filtered_tasks)} filtered tasks",
            }
        except Exception as e:
            self.handle_error(e, f"filtering tasks for project {project_id}")

    async def bulk_stop_tasks(
        self, project_id: int, task_ids: List[int], confirm: bool = False
    ) -> Dict[str, Any]:
        """Stop multiple tasks with confirmation.

        Args:
            project_id: ID of the project
            task_ids: List of task IDs to stop
            confirm: Set to True to execute the bulk stop operation

        Returns:
            Confirmation details or bulk stop results
        """
        try:
            if not confirm:
                # Get details about tasks to be stopped
                task_details = []
                for task_id in task_ids:
                    try:
                        task = self.semaphore.get_task(project_id, task_id)
                        task_details.append(
                            {
                                "id": task_id,
                                "status": task.get("status"),
                                "template": task.get("template", {}).get(
                                    "name", "Unknown"
                                ),
                            }
                        )
                    except Exception:
                        task_details.append(
                            {"id": task_id, "status": "unknown", "template": "Unknown"}
                        )

                # Generate confirmation message
                status_counts: Dict[str, int] = {}
                for task in task_details:
                    status = task["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1

                return {
                    "confirmation_required": True,
                    "tasks_to_stop": len(task_ids),
                    "task_details": task_details,
                    "status_breakdown": status_counts,
                    "message": "Add confirm=True to proceed with bulk stop operation",
                }

            # Execute bulk stop
            results = []
            successful_stops = 0
            failed_stops = 0

            for task_id in task_ids:
                try:
                    result = self.semaphore.stop_task(project_id, task_id)
                    results.append(
                        {"task_id": task_id, "status": "stopped", "result": result}
                    )
                    successful_stops += 1
                except Exception as e:
                    results.append(
                        {"task_id": task_id, "status": "failed", "error": str(e)}
                    )
                    failed_stops += 1

            return {
                "bulk_operation_complete": True,
                "summary": {
                    "total_tasks": len(task_ids),
                    "successful_stops": successful_stops,
                    "failed_stops": failed_stops,
                },
                "results": results,
            }
        except Exception as e:
            self.handle_error(e, f"bulk stopping tasks for project {project_id}")

    async def restart_task(self, project_id: int, task_id: int) -> Dict[str, Any]:
        """Restart a stopped or failed task.

        Args:
            project_id: ID of the project
            task_id: ID of the task to restart

        Returns:
            Task restart result
        """
        try:
            return self.semaphore.restart_task(project_id, task_id)
        except Exception as e:
            self.handle_error(e, f"restarting task {task_id}")

    async def bulk_restart_tasks(
        self, project_id: int, task_ids: List[int]
    ) -> Dict[str, Any]:
        """Restart multiple tasks in bulk.

        Args:
            project_id: ID of the project
            task_ids: List of task IDs to restart

        Returns:
            Bulk task restart result
        """
        try:
            results = []
            for task_id in task_ids:
                try:
                    result = await self.restart_task(project_id, task_id)
                    results.append({"task_id": task_id, "result": result})
                except Exception as e:
                    results.append({"task_id": task_id, "error": str(e)})
            return {"results": results}
        except Exception as e:
            self.handle_error(e, f"bulk restarting tasks for project {project_id}")

    async def run_task_with_monitoring(
        self,
        template_id: int,
        project_id: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
        follow: bool = False,
        poll_interval: int = 3,
        max_poll_duration: int = 300,
    ) -> Dict[str, Any]:
        """Run a task with optional progress monitoring.

        Args:
            template_id: ID of the template to run
            project_id: Optional project ID
            environment: Optional environment variables
            follow: Enable monitoring and status updates
            poll_interval: Seconds between status checks (default: 3)
            max_poll_duration: Maximum time to poll in seconds (default: 300)

        Returns:
            Task execution result with optional monitoring updates
        """
        try:
            # Start the task using existing run_task method
            task_result = await self.run_task(template_id, project_id, environment)

            if not follow:
                return task_result

            # Extract task and project IDs for monitoring
            task_id = task_result.get("id")
            if not task_id:
                return {
                    "error": "Could not extract task ID for monitoring",
                    "original_result": task_result,
                }

            # Determine project_id if not provided
            if not project_id:
                # Try to extract from task result or use template lookup
                project_id = task_result.get("project_id")
                if not project_id:
                    return {
                        "error": "Could not determine project ID for monitoring",
                        "original_result": task_result,
                    }

            # Start monitoring
            monitoring_result = await self._monitor_task_execution(
                project_id, task_id, poll_interval, max_poll_duration
            )

            return {"task_started": task_result, "monitoring": monitoring_result}

        except Exception as e:
            self.handle_error(
                e, f"running task with monitoring for template {template_id}"
            )

    async def _monitor_task_execution(
        self, project_id: int, task_id: int, poll_interval: int, max_poll_duration: int
    ) -> Dict[str, Any]:
        """Monitor task execution with smart polling.

        Args:
            project_id: Project ID
            task_id: Task ID to monitor
            poll_interval: Seconds between polls
            max_poll_duration: Maximum monitoring duration

        Returns:
            Monitoring results with status updates
        """
        status_updates = []
        start_time = asyncio.get_event_loop().time()
        last_status = None
        poll_count = 0

        try:
            while True:
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time

                # Check timeout
                if elapsed > max_poll_duration:
                    status_updates.append(
                        {
                            "timestamp": current_time,
                            "message": f"Monitoring timeout after {max_poll_duration}s",
                            "status": "timeout",
                        }
                    )
                    break

                # Get current task status
                try:
                    task = self.semaphore.get_task(project_id, task_id)
                    current_status = task.get("status", "unknown")
                    poll_count += 1

                    # Log status change
                    if current_status != last_status:
                        status_updates.append(
                            {
                                "timestamp": current_time,
                                "status": current_status,
                                "message": f"Task {task_id}: {last_status or 'started'} → {current_status}",
                                "poll_count": poll_count,
                            }
                        )
                        last_status = current_status

                    # Check if task is complete
                    if current_status in ["success", "error", "stopped"]:
                        # Get final output
                        try:
                            self.semaphore.get_task_output(project_id, task_id)
                            status_updates.append(
                                {
                                    "timestamp": current_time,
                                    "message": f"Task completed with status: {current_status}",
                                    "status": current_status,
                                    "output_available": True,
                                }
                            )
                        except Exception as e:
                            status_updates.append(
                                {
                                    "timestamp": current_time,
                                    "message": f"Task completed but output unavailable: {str(e)}",
                                    "status": current_status,
                                    "output_available": False,
                                }
                            )
                        break

                    # Continue polling for running/waiting tasks
                    if current_status in ["running", "waiting"]:
                        await asyncio.sleep(poll_interval)
                        continue

                    # Unknown status - continue polling but log it
                    status_updates.append(
                        {
                            "timestamp": current_time,
                            "message": f"Unknown status: {current_status}, continuing to monitor",
                            "status": current_status,
                        }
                    )
                    await asyncio.sleep(poll_interval)

                except Exception as e:
                    status_updates.append(
                        {
                            "timestamp": current_time,
                            "message": f"Error polling task status: {str(e)}",
                            "status": "error",
                        }
                    )
                    await asyncio.sleep(poll_interval)

            return {
                "monitoring_complete": True,
                "total_polls": poll_count,
                "duration_seconds": elapsed,
                "final_status": last_status,
                "status_updates": status_updates,
            }

        except Exception as e:
            return {
                "monitoring_failed": True,
                "error": str(e),
                "status_updates": status_updates,
            }

    async def get_task_raw_output(self, project_id: int, task_id: int) -> str:
        """Get raw output from a completed task for LLM analysis.

        Args:
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Raw task output as plain text
        """
        try:
            return self.semaphore.get_task_raw_output(project_id, task_id)
        except Exception as e:
            self.handle_error(e, f"getting raw output for task {task_id}")

    async def analyze_task_failure(
        self, project_id: int, task_id: int
    ) -> Dict[str, Any]:
        """Analyze a failed task for LLM processing, gathering comprehensive failure context.

        Args:
            project_id: ID of the project
            task_id: ID of the task to analyze

        Returns:
            Comprehensive failure analysis data including task details, template context, and outputs
        """
        try:
            # Get task details
            task = self.semaphore.get_task(project_id, task_id)

            # Verify this is actually a failed task
            if task.get("status") != "error":
                return {
                    "warning": f"Task {task_id} has status '{task.get('status')}', not 'error'",
                    "task_status": task.get("status"),
                    "analysis_applicable": False,
                }

            # Get template context
            template_id = task.get("template_id") or task.get("template", {}).get("id")
            template_context = None
            if template_id:
                try:
                    template_context = self.semaphore.get_template(
                        project_id, template_id
                    )
                except Exception as e:
                    logger.warning(f"Could not fetch template {template_id}: {str(e)}")

            # Get both structured and raw output
            structured_output = None
            raw_output = None

            try:
                structured_output = self.semaphore.get_task_output(project_id, task_id)
            except Exception as e:
                logger.warning(f"Could not fetch structured output: {str(e)}")

            try:
                raw_output = self.semaphore.get_task_raw_output(project_id, task_id)
            except Exception as e:
                logger.warning(f"Could not fetch raw output: {str(e)}")

            # Get project context
            project_context = None
            try:
                projects = self.semaphore.list_projects()
                if isinstance(projects, list):
                    project_context = next(
                        (p for p in projects if p.get("id") == project_id), None
                    )
                elif isinstance(projects, dict) and "projects" in projects:
                    project_context = next(
                        (p for p in projects["projects"] if p.get("id") == project_id),
                        None,
                    )
            except Exception as e:
                logger.warning(f"Could not fetch project context: {str(e)}")

            return {
                "analysis_ready": True,
                "task_details": {
                    "id": task_id,
                    "status": task.get("status"),
                    "created": task.get("created"),
                    "started": task.get("started"),
                    "ended": task.get("ended"),
                    "message": task.get("message"),
                    "debug": task.get("debug"),
                    "environment": task.get("environment"),
                    "template_id": template_id,
                },
                "project_context": {
                    "id": project_id,
                    "name": project_context.get("name") if project_context else None,
                    "repository": (
                        project_context.get("repository") if project_context else None
                    ),
                },
                "template_context": (
                    {
                        "id": template_id,
                        "name": (
                            template_context.get("name") if template_context else None
                        ),
                        "playbook": (
                            template_context.get("playbook")
                            if template_context
                            else None
                        ),
                        "arguments": (
                            template_context.get("arguments")
                            if template_context
                            else None
                        ),
                        "description": (
                            template_context.get("description")
                            if template_context
                            else None
                        ),
                    }
                    if template_context
                    else None
                ),
                "outputs": {
                    "structured": structured_output,
                    "raw": raw_output,
                    "has_raw_output": raw_output is not None,
                    "has_structured_output": structured_output is not None,
                },
                "analysis_guidance": {
                    "focus_areas": [
                        "Check raw output for specific error messages",
                        "Look for Ansible task failures in the execution log",
                        "Examine any Python tracebacks or syntax errors",
                        "Check for connectivity or authentication issues",
                        "Look for missing files or incorrect paths",
                        "Verify playbook syntax and variable usage",
                    ],
                    "common_failure_patterns": [
                        "Host unreachable",
                        "Authentication failure",
                        "Module not found",
                        "Variable undefined",
                        "Permission denied",
                        "Syntax error in playbook",
                        "Task timeout",
                    ],
                },
            }
        except Exception as e:
            self.handle_error(e, f"analyzing failure for task {task_id}")

    async def bulk_analyze_failures(
        self, project_id: int, limit: int = 10
    ) -> Dict[str, Any]:
        """Analyze multiple failed tasks to identify patterns and common issues.

        Args:
            project_id: ID of the project
            limit: Maximum number of failed tasks to analyze (default: 10)

        Returns:
            Analysis of multiple failed tasks with pattern detection
        """
        try:
            # Get recent failed tasks
            failed_tasks_result = await self.filter_tasks(
                project_id, status=["failed"], limit=limit
            )
            failed_tasks = failed_tasks_result.get("tasks", [])

            if not failed_tasks:
                return {
                    "message": "No failed tasks found for analysis",
                    "failed_task_count": 0,
                }

            # Analyze each failed task
            analyses = []
            error_patterns: Dict[str, int] = {}
            template_failure_counts: Dict[str, int] = {}

            for task in failed_tasks:
                task_id = task.get("id")
                if not task_id:
                    continue

                try:
                    analysis = await self.analyze_task_failure(project_id, task_id)
                    if analysis.get("analysis_ready"):
                        analyses.append(analysis)

                        # Extract patterns for analysis
                        template_name = analysis.get("template_context", {}).get(
                            "name", "Unknown"
                        )
                        template_failure_counts[template_name] = (
                            template_failure_counts.get(template_name, 0) + 1
                        )

                        # Look for common error patterns in raw output
                        raw_output = analysis.get("outputs", {}).get("raw", "")
                        if raw_output:
                            # Simple pattern matching for common errors
                            common_patterns = [
                                (
                                    "connection_error",
                                    ["unreachable", "connection", "timeout", "refused"],
                                ),
                                (
                                    "auth_error",
                                    [
                                        "authentication",
                                        "permission denied",
                                        "unauthorized",
                                        "access denied",
                                    ],
                                ),
                                (
                                    "syntax_error",
                                    [
                                        "syntax error",
                                        "yaml error",
                                        "parse error",
                                        "invalid syntax",
                                    ],
                                ),
                                (
                                    "module_error",
                                    [
                                        "module not found",
                                        "no module named",
                                        "import error",
                                    ],
                                ),
                                (
                                    "variable_error",
                                    [
                                        "undefined variable",
                                        "variable not defined",
                                        "variable is undefined",
                                    ],
                                ),
                            ]

                            for pattern_name, keywords in common_patterns:
                                if any(
                                    keyword.lower() in raw_output.lower()
                                    for keyword in keywords
                                ):
                                    error_patterns[pattern_name] = (
                                        error_patterns.get(pattern_name, 0) + 1
                                    )

                except Exception as e:
                    logger.warning(f"Failed to analyze task {task_id}: {str(e)}")
                    continue

            # Generate insights
            insights = []
            if template_failure_counts:
                most_failing_template = max(
                    template_failure_counts.items(), key=lambda x: x[1]
                )
                insights.append(
                    f"Template '{most_failing_template[0]}' has the most failures ({most_failing_template[1]} out of {len(analyses)})"
                )

            if error_patterns:
                most_common_error = max(error_patterns.items(), key=lambda x: x[1])
                insights.append(
                    f"Most common error pattern: {most_common_error[0]} ({most_common_error[1]} occurrences)"
                )

            return {
                "bulk_analysis_complete": True,
                "analyzed_tasks": len(analyses),
                "total_failed_tasks": len(failed_tasks),
                "template_failure_breakdown": template_failure_counts,
                "error_pattern_analysis": error_patterns,
                "insights": insights,
                "detailed_analyses": analyses,
                "recommendations": [
                    "Focus on fixing the most frequently failing templates",
                    "Address common error patterns identified in the analysis",
                    "Review authentication and connection settings if auth/connection errors are common",
                    "Validate playbook syntax if syntax errors are frequent",
                    "Check variable definitions and inventory if variable errors are present",
                ],
            }
        except Exception as e:
            self.handle_error(e, f"bulk analyzing failures for project {project_id}")

    async def get_waiting_tasks(self, project_id: int) -> Dict[str, Any]:
        """Get all tasks in waiting state for bulk operations.

        Args:
            project_id: ID of the project

        Returns:
            List of waiting tasks with bulk operation guidance
        """
        try:
            result = await self.filter_tasks(project_id, status=["waiting"], limit=100)
            waiting_tasks = result.get("tasks", [])

            if not waiting_tasks:
                return {
                    "message": "No tasks in waiting state found",
                    "waiting_tasks": [],
                }

            # Extract task IDs for bulk operations
            task_ids = [task["id"] for task in waiting_tasks]

            return {
                "waiting_tasks": waiting_tasks,
                "count": len(waiting_tasks),
                "task_ids": task_ids,
                "bulk_operations": {
                    "stop_all": f"Use bulk_stop_tasks(project_id={project_id}, task_ids={task_ids})",
                    "note": "Add confirm=True to execute bulk operations",
                },
            }
        except Exception as e:
            self.handle_error(e, f"getting waiting tasks for project {project_id}")
