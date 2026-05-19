"""
Event and observability tools for Semaphore MCP.

This module provides tools for reading SemaphoreUI event activity and producing
small deterministic project activity summaries.
"""

import logging
from collections import Counter
from typing import Any

from .base import BaseTool

logger = logging.getLogger(__name__)


class EventTools(BaseTool):
    """Tools for reading Semaphore events and project activity."""

    def _limit_events(
        self, events: list[dict[str, Any]], limit: int
    ) -> list[dict[str, Any]]:
        if limit < 0:
            raise ValueError("limit must be 0 or greater")
        if limit == 0:
            return events
        return events[-limit:]

    def _count_by_field(
        self, events: list[dict[str, Any]], field: str
    ) -> dict[str, int]:
        values = [str(event.get(field) or "unknown") for event in events]
        return dict(Counter(values))

    async def list_events(self, limit: int = 0) -> dict[str, Any]:
        """List global events visible to the current user.

        Args:
            limit: Return only the most recent N events; 0 returns all events

        Returns:
            Dictionary containing the list of events
        """
        try:
            events = self.semaphore.list_events()
            return {"events": self._limit_events(events, limit)}
        except Exception as e:
            self.handle_error(e, "listing events")

    async def get_last_events(self, limit: int = 0) -> dict[str, Any]:
        """List the last global events visible to the current user.

        Semaphore returns the last 200 events. The optional limit trims that
        response further on the MCP side.

        Args:
            limit: Return only the most recent N events; 0 returns all returned events

        Returns:
            Dictionary containing the list of events
        """
        try:
            events = self.semaphore.get_last_events()
            return {"events": self._limit_events(events, limit)}
        except Exception as e:
            self.handle_error(e, "getting last events")

    async def list_project_events(
        self, project_id: int, limit: int = 0
    ) -> dict[str, Any]:
        """List events related to a project.

        Args:
            project_id: ID of the project
            limit: Return only the most recent N events; 0 returns all events

        Returns:
            Dictionary containing the list of project events
        """
        try:
            events = self.semaphore.list_project_events(project_id)
            return {"events": self._limit_events(events, limit)}
        except Exception as e:
            self.handle_error(e, f"listing events for project {project_id}")

    async def summarize_project_activity(
        self,
        project_id: int,
        limit: int = 50,
        recent_limit: int = 10,
    ) -> dict[str, Any]:
        """Summarize recent project activity from Semaphore events.

        Args:
            project_id: ID of the project
            limit: Number of most recent events to analyze
            recent_limit: Number of recent event objects to include

        Returns:
            Counts and recent event details for project activity
        """
        try:
            if limit < 1:
                raise ValueError("limit must be 1 or greater")
            if recent_limit < 0:
                raise ValueError("recent_limit must be 0 or greater")

            all_events = self.semaphore.list_project_events(project_id)
            events = self._limit_events(all_events, limit)
            recent_events = events[-recent_limit:] if recent_limit else []

            return {
                "project_id": project_id,
                "event_count": len(events),
                "total_available": len(all_events),
                "limit": limit,
                "counts_by_object_type": self._count_by_field(events, "object_type"),
                "counts_by_description": self._count_by_field(events, "description"),
                "counts_by_user_id": self._count_by_field(events, "user_id"),
                "recent_events": recent_events,
            }
        except Exception as e:
            self.handle_error(e, f"summarizing activity for project {project_id}")
