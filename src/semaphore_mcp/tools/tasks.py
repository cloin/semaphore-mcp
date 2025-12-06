"""
Task-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore tasks.
"""

import asyncio
import logging
import time
from typing import Any, Optional, Union

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

    def _build_task_url(self, project_id: int, task_id: int) -> str:
        """Build a web URL for viewing a task in SemaphoreUI.

        Args:
            project_id: Project ID
            task_id: Task ID

        Returns:
            URL string for viewing the task
        """
        # Get the base URL from the semaphore client
        base_url = self.semaphore.base_url.rstrip("/")

        # Remove /api suffix if present to get the web UI base
        if base_url.endswith("/api"):
            base_url = base_url[:-4]

        return f"{base_url}/project/{project_id}/history?t={task_id}"

    def _build_project_tasks_url(self, project_id: int) -> str:
        """Build a web URL for viewing all tasks in a project.

        Args:
            project_id: Project ID

        Returns:
            URL string for viewing project tasks
        """
        base_url = self.semaphore.base_url.rstrip("/")
        if base_url.endswith("/api"):
            base_url = base_url[:-4]

        return f"{base_url}/project/{project_id}/history"

    async def list_tasks(
        self,
        project_id: int,
        limit: int = 5,
        status: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
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

    async def get_latest_failed_task(self, project_id: int) -> dict[str, Any]:
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

    async def get_task(self, project_id: int, task_id: int) -> dict[str, Any]:
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
            # If individual task fetch fails, try to find it in the task list
            if "404" in str(e):
                try:
                    tasks = self.semaphore.list_tasks(project_id)
                    if isinstance(tasks, list):
                        matching_task = next(
                            (task for task in tasks if task.get("id") == task_id), None
                        )
                        if matching_task:
                            return {
                                "task": matching_task,
                                "note": "Task found in list but individual endpoint unavailable",
                            }
                    self.handle_error(
                        e,
                        f"getting task {task_id}. Task may have been deleted or ID format may be incorrect",
                    )
                except Exception:
                    pass
            self.handle_error(e, f"getting task {task_id}")

    async def run_task(
        self,
        template_id: int,
        project_id: Optional[int] = None,
        environment: Optional[dict[str, str]] = None,
        limit: Optional[str] = None,
        dry_run: Optional[bool] = None,
        diff: Optional[bool] = None,
        debug: Optional[bool] = None,
        playbook: Optional[str] = None,
        git_branch: Optional[str] = None,
        message: Optional[str] = None,
        arguments: Optional[str] = None,
        inventory_id: Optional[int] = None,
        follow: bool = False,
    ) -> dict[str, Any]:
        """Run a task from a template with optional 30-second monitoring.

        Args:
            template_id: ID of the template to run
            project_id: Optional project ID (if not provided, will attempt to determine from template)
            environment: Optional environment variables for the task as dictionary
            limit: Restrict execution to specific hosts/groups (Ansible --limit)
            dry_run: Run without making changes (Ansible --check)
            diff: Show differences when changing files (Ansible --diff)
            debug: Enable verbose debug output
            playbook: Override playbook file path
            git_branch: Override git branch to use
            message: Task description/message
            arguments: Additional CLI arguments
            inventory_id: Override inventory to use
            follow: Enable 30-second monitoring for startup verification (default: False)

        Returns:
            Task execution result with immediate web URLs and optional monitoring summary

        Template Override Requirements:
            Some parameters require the template to have overrides enabled in task_params.
            Use create_template() or update_template() with task_params to enable:

            - limit: requires task_params={"allow_override_limit": true}
            - inventory_id: requires task_params={"allow_override_inventory": true}

            Without these settings, the parameter will be ignored silently.

        Examples:
            # Just start the task and get URLs
            result = await run_task(template_id=5)

            # Start task with 30-second monitoring and get URLs
            result = await run_task(template_id=5, follow=True)

            # Run with limit to specific hosts (template must allow override)
            result = await run_task(template_id=5, limit="webservers")

            # Dry run with diff to preview changes
            result = await run_task(template_id=5, dry_run=True, diff=True)
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
                task_result = self.semaphore.run_task(
                    project_id,
                    template_id,
                    environment=environment,
                    limit=limit,
                    dry_run=dry_run,
                    diff=diff,
                    debug=debug,
                    playbook=playbook,
                    git_branch=git_branch,
                    message=message,
                    arguments=arguments,
                    inventory_id=inventory_id,
                )

                # Extract task ID for URL generation
                task_id = task_result.get("id")
                if not task_id:
                    logger.error(f"Task result missing ID field: {task_result}")
                    return {
                        "error": "Could not extract task ID for URL generation",
                        "original_result": task_result,
                        "suggestion": "Check if the task was created successfully",
                    }

                # Build URLs for immediate access
                task_url = self._build_task_url(project_id, task_id)
                project_url = self._build_project_tasks_url(project_id)

                # Prepare base response with immediate URL access
                response = {
                    "task": task_result,
                    "web_urls": {"task_detail": task_url, "project_tasks": project_url},
                    "message": f"Task #{task_id} started successfully!",
                    "next_steps": "Use the task_detail URL above to monitor progress in SemaphoreUI",
                }

                # If follow is False, return immediately with URLs
                if not follow:
                    response["monitoring"] = {
                        "enabled": False,
                        "message": "Use the web URL above to monitor task progress",
                    }
                    return response

                # If follow is True, do 30-second smart monitoring
                logger.info(
                    f"Starting 30-second monitoring for task {task_id} in project {project_id}"
                )

                monitoring_result = await self._monitor_task_startup(
                    project_id, task_id
                )

                response["monitoring"] = monitoring_result

                # Update the message based on monitoring results
                if monitoring_result.get("completed"):
                    final_status = monitoring_result.get("final_status")
                    if final_status in ["success", "successful"]:
                        response["message"] = f"Task #{task_id} completed successfully!"
                    elif final_status in ["error", "failed"]:
                        response["message"] = (
                            f"Task #{task_id} failed. Check logs via the URL above."
                        )
                    else:
                        response["message"] = (
                            f"Task #{task_id} finished with status: {final_status}"
                        )
                else:
                    response["message"] = (
                        f"Task #{task_id} is still running. Use the URL above for live progress."
                    )

                return response

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
                # Don't re-raise, let the outer handler catch the original HTTP error
                raise http_err
            except Exception as e:
                logger.error(
                    f"Error running task for template {template_id} in project {project_id}: {str(e)}"
                )
                raise RuntimeError(f"Error running task: {str(e)}") from e

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error while running task: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_type": "connection_error",
                "suggestion": "Check if SemaphoreUI is running and accessible",
            }
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error while running task: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_type": "http_error",
                "suggestion": "Check API credentials and template permissions",
            }
        except Exception as e:
            error_msg = (
                f"Unexpected error running task for template {template_id}: {str(e)}"
            )
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_type": "unexpected_error",
                "suggestion": "Check logs for more details",
            }

    async def stop_task(self, project_id: int, task_id: int) -> dict[str, Any]:
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
        status: Optional[list[str]] = None,
        limit: int = 50,
        use_last_tasks: bool = True,
    ) -> dict[str, Any]:
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
            stats: dict[str, Union[int, dict[str, int]]] = {
                "total_tasks": len(all_tasks),
                "filtered_tasks": len(filtered_tasks),
                "returned_tasks": len(limited_tasks),
            }

            # Status breakdown
            if filtered_tasks:
                status_counts: dict[str, int] = {}
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
        self, project_id: int, task_ids: list[int], confirm: bool = False
    ) -> dict[str, Any]:
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
                status_counts: dict[str, int] = {}
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

    async def restart_task(self, project_id: int, task_id: int) -> dict[str, Any]:
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
        self, project_id: int, task_ids: list[int]
    ) -> dict[str, Any]:
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

    async def _monitor_task_startup(
        self, project_id: int, task_id: int
    ) -> dict[str, Any]:
        """Monitor task for 30 seconds to catch quick completions and startup issues.

        Args:
            project_id: Project ID
            task_id: Task ID to monitor

        Returns:
            Monitoring summary focused on startup verification
        """
        status_updates = []
        start_time = time.time()
        last_status = None
        poll_count = 0
        consecutive_errors = 0
        max_consecutive_errors = 3

        # Fixed 30-second monitoring with 3-second intervals
        monitoring_duration = 30
        poll_interval = 3
        max_polls = 10  # 30 seconds / 3 seconds = 10 polls

        logger.info(f"Starting 30-second startup monitoring for task {task_id}")

        # Small initial delay to allow task to be created in API
        await asyncio.sleep(0.5)

        try:
            for _poll_num in range(max_polls):
                current_time = time.time()
                elapsed = current_time - start_time

                # Check if we've exceeded 30 seconds
                if elapsed > monitoring_duration:
                    break

                # Get current task status
                try:
                    task = self.semaphore.get_task(project_id, task_id)
                    current_status = task.get("status", "unknown")
                    poll_count += 1
                    consecutive_errors = 0  # Reset error count on success

                    # Log status change
                    if current_status != last_status:
                        status_msg = f"Task {task_id}: {last_status or 'started'} → {current_status}"
                        logger.info(status_msg)
                        status_updates.append(
                            {
                                "timestamp": current_time,
                                "status": current_status,
                                "message": status_msg,
                                "poll_count": poll_count,
                            }
                        )
                        last_status = current_status

                    # Check if task completed
                    if current_status in [
                        "success",
                        "error",
                        "stopped",
                        "successful",
                        "failed",
                    ]:
                        # Get final output if available
                        output_available = False
                        try:
                            self.semaphore.get_task_raw_output(project_id, task_id)
                            output_available = True
                        except Exception:
                            pass  # Output not available yet, that's ok

                        completion_msg = f"Task completed with status: {current_status}"
                        logger.info(completion_msg)
                        status_updates.append(
                            {
                                "timestamp": current_time,
                                "message": completion_msg,
                                "status": current_status,
                                "output_available": output_available,
                            }
                        )

                        return {
                            "completed": True,
                            "duration_seconds": elapsed,
                            "final_status": current_status,
                            "total_polls": poll_count,
                            "status_updates": status_updates,
                            "summary": f"Task finished in {elapsed:.1f}s with status: {current_status}",
                        }

                    # Continue monitoring
                    await asyncio.sleep(poll_interval)

                except requests.exceptions.HTTPError as e:
                    # Handle 404 errors with fallback to task list
                    consecutive_errors += 1

                    if "404" in str(e) and poll_count < 3:
                        try:
                            logger.info(
                                f"Task {task_id} not found via direct API, trying task list..."
                            )
                            tasks = self.semaphore.list_tasks(project_id)
                            if isinstance(tasks, list):
                                matching_task = next(
                                    (
                                        task
                                        for task in tasks
                                        if task.get("id") == task_id
                                    ),
                                    None,
                                )
                                if matching_task:
                                    current_status = matching_task.get(
                                        "status", "unknown"
                                    )
                                    poll_count += 1
                                    consecutive_errors = 0

                                    if current_status != last_status:
                                        status_msg = f"Task {task_id}: {last_status or 'started'} → {current_status} (via task list)"
                                        logger.info(status_msg)
                                        status_updates.append(
                                            {
                                                "timestamp": current_time,
                                                "status": current_status,
                                                "message": status_msg,
                                                "poll_count": poll_count,
                                                "source": "task_list",
                                            }
                                        )
                                        last_status = current_status

                                    # Check if complete
                                    if current_status in [
                                        "success",
                                        "error",
                                        "stopped",
                                        "successful",
                                        "failed",
                                    ]:
                                        completion_msg = f"Task completed with status: {current_status} (via task list)"
                                        logger.info(completion_msg)
                                        status_updates.append(
                                            {
                                                "timestamp": current_time,
                                                "message": completion_msg,
                                                "status": current_status,
                                                "output_available": False,
                                                "source": "task_list",
                                            }
                                        )

                                        return {
                                            "completed": True,
                                            "duration_seconds": elapsed,
                                            "final_status": current_status,
                                            "total_polls": poll_count,
                                            "status_updates": status_updates,
                                            "summary": f"Task finished in {elapsed:.1f}s with status: {current_status}",
                                        }

                                    await asyncio.sleep(poll_interval)
                                    continue
                        except Exception as list_error:
                            logger.warning(
                                f"Error checking task list: {str(list_error)}"
                            )

                    # Log the HTTP error
                    error_msg = f"HTTP error polling task status (attempt {consecutive_errors}): {str(e)}"
                    status_updates.append(
                        {
                            "timestamp": current_time,
                            "message": error_msg,
                            "status": "http_error",
                            "consecutive_errors": consecutive_errors,
                        }
                    )
                    logger.warning(error_msg)

                    # Give up after too many consecutive errors
                    if consecutive_errors >= max_consecutive_errors:
                        break

                    await asyncio.sleep(poll_interval)

                except Exception as e:
                    consecutive_errors += 1
                    error_msg = f"Error polling task status (attempt {consecutive_errors}): {str(e)}"
                    status_updates.append(
                        {
                            "timestamp": current_time,
                            "message": error_msg,
                            "status": "error",
                            "consecutive_errors": consecutive_errors,
                        }
                    )
                    logger.error(error_msg)

                    if consecutive_errors >= max_consecutive_errors:
                        break

                    await asyncio.sleep(poll_interval)

            # If we get here, monitoring completed without task finishing
            current_time = time.time()
            elapsed = current_time - start_time

            logger.info(
                f"30-second monitoring completed for task {task_id}: {poll_count} polls, status: {last_status}"
            )

            return {
                "completed": False,
                "duration_seconds": elapsed,
                "final_status": last_status,
                "total_polls": poll_count,
                "status_updates": status_updates,
                "summary": f"Task still {last_status or 'running'} after {elapsed:.1f}s of monitoring",
                "consecutive_errors": consecutive_errors,
            }

        except Exception as e:
            current_time = time.time()
            elapsed = current_time - start_time

            error_msg = f"Critical error during startup monitoring: {str(e)}"
            logger.error(error_msg)

            return {
                "completed": False,
                "monitoring_failed": True,
                "error": error_msg,
                "duration_seconds": elapsed,
                "status_updates": status_updates,
                "consecutive_errors": consecutive_errors,
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
    ) -> dict[str, Any]:
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

            # Get raw output for analysis
            raw_output = None

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
                    "raw": raw_output,
                    "has_raw_output": raw_output is not None,
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
    ) -> dict[str, Any]:
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
            error_patterns: dict[str, int] = {}
            template_failure_counts: dict[str, int] = {}

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

    async def get_waiting_tasks(self, project_id: int) -> dict[str, Any]:
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
