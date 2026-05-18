"""Schedule tools for Semaphore MCP.

Provides tools for managing SemaphoreUI project schedules, including recurring
cron schedules and one-time run_at schedules.
"""

from typing import Any, Optional

from .base import BaseTool


class ScheduleTools(BaseTool):
    """Tools for managing Semaphore schedules."""

    def _validate_schedule_inputs(
        self,
        cron_format: Optional[str],
        schedule_type: str,
        run_at: Optional[str],
    ) -> None:
        if schedule_type not in ("", "run_at"):
            raise ValueError("schedule_type must be '' for cron or 'run_at'")
        if schedule_type == "run_at" and not run_at:
            raise ValueError("run_at is required for run_at schedules")
        if schedule_type == "" and not cron_format:
            raise ValueError("cron_format is required for cron schedules")

    async def list_schedules(self, project_id: int) -> dict[str, Any]:
        """List all schedules for a project.

        Args:
            project_id: ID of the project

        Returns:
            Dictionary containing list of schedules
        """
        try:
            schedules = self.semaphore.list_schedules(project_id)
            return {"schedules": schedules}
        except Exception as e:
            self.handle_error(e, f"listing schedules for project {project_id}")

    async def list_template_schedules(
        self, project_id: int, template_id: int
    ) -> dict[str, Any]:
        """List schedules attached to a template.

        Args:
            project_id: ID of the project
            template_id: ID of the template

        Returns:
            Dictionary containing list of template schedules
        """
        try:
            schedules = self.semaphore.list_template_schedules(project_id, template_id)
            return {"schedules": schedules}
        except Exception as e:
            self.handle_error(e, f"listing schedules for template {template_id}")

    async def get_schedule(self, project_id: int, schedule_id: int) -> dict[str, Any]:
        """Get details of a specific schedule.

        Args:
            project_id: ID of the project
            schedule_id: ID of the schedule to fetch

        Returns:
            Schedule details
        """
        try:
            return self.semaphore.get_schedule(project_id, schedule_id)
        except Exception as e:
            self.handle_error(e, f"getting schedule {schedule_id}")

    async def create_schedule(
        self,
        project_id: int,
        template_id: int,
        name: str,
        cron_format: Optional[str] = None,
        active: bool = True,
        schedule_type: str = "",
        run_at: Optional[str] = None,
        task_params: Optional[dict[str, Any]] = None,
        delete_after_run: Optional[bool] = None,
        repository_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a new schedule.

        Args:
            project_id: ID of the project
            template_id: ID of the template to run
            name: Schedule name
            cron_format: Cron expression for recurring schedules
            active: Whether the schedule is enabled
            schedule_type: Schedule type: "" for cron, or "run_at" for one-time runs
            run_at: RFC3339 timestamp for one-time schedules
            task_params: Optional task parameters to pass when the schedule runs
            delete_after_run: Delete the one-time schedule after it runs
            repository_id: Optional repository ID for commit-check schedules

        Returns:
            Created schedule details
        """
        try:
            self._validate_schedule_inputs(cron_format, schedule_type, run_at)
            return self.semaphore.create_schedule(
                project_id,
                template_id,
                name,
                cron_format,
                active,
                schedule_type,
                run_at,
                task_params,
                delete_after_run,
                repository_id,
            )
        except Exception as e:
            self.handle_error(e, f"creating schedule '{name}' in project {project_id}")

    async def update_schedule(
        self,
        project_id: int,
        schedule_id: int,
        template_id: Optional[int] = None,
        name: Optional[str] = None,
        cron_format: Optional[str] = None,
        active: Optional[bool] = None,
        schedule_type: Optional[str] = None,
        run_at: Optional[str] = None,
        task_params: Optional[dict[str, Any]] = None,
        delete_after_run: Optional[bool] = None,
        repository_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update an existing schedule.

        Args:
            project_id: ID of the project
            schedule_id: ID of the schedule to update
            template_id: ID of the template to run
            name: Schedule name
            cron_format: Cron expression for recurring schedules
            active: Whether the schedule is enabled
            schedule_type: Schedule type: "" for cron, or "run_at" for one-time runs
            run_at: RFC3339 timestamp for one-time schedules
            task_params: Optional task parameters to pass when the schedule runs
            delete_after_run: Delete the one-time schedule after it runs
            repository_id: Optional repository ID for commit-check schedules

        Returns:
            Updated schedule details or empty dict on success
        """
        try:
            if schedule_type is not None:
                if schedule_type not in ("", "run_at"):
                    raise ValueError("schedule_type must be '' for cron or 'run_at'")
            return self.semaphore.update_schedule(
                project_id,
                schedule_id,
                template_id,
                name,
                cron_format,
                active,
                schedule_type,
                run_at,
                task_params,
                delete_after_run,
                repository_id,
            )
        except Exception as e:
            self.handle_error(e, f"updating schedule {schedule_id}")

    async def set_schedule_active(
        self, project_id: int, schedule_id: int, active: bool
    ) -> dict[str, Any]:
        """Enable or disable a schedule.

        Args:
            project_id: ID of the project
            schedule_id: ID of the schedule to update
            active: Whether the schedule should be active

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.set_schedule_active(project_id, schedule_id, active)
        except Exception as e:
            self.handle_error(e, f"setting schedule {schedule_id} active={active}")

    async def delete_schedule(
        self, project_id: int, schedule_id: int
    ) -> dict[str, Any]:
        """Delete a schedule.

        Args:
            project_id: ID of the project
            schedule_id: ID of the schedule to delete

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.delete_schedule(project_id, schedule_id)
        except Exception as e:
            self.handle_error(e, f"deleting schedule {schedule_id}")

    async def validate_schedule_cron_format(
        self, project_id: int, cron_format: str
    ) -> dict[str, Any]:
        """Validate a cron expression for Semaphore schedules.

        Args:
            project_id: ID of the project
            cron_format: Cron expression to validate

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.validate_schedule_cron_format(project_id, cron_format)
        except Exception as e:
            self.handle_error(e, f"validating schedule cron format '{cron_format}'")
