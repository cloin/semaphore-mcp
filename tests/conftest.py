"""
Shared pytest fixtures for semaphore-mcp tests.

This module provides common fixtures used across multiple test files
to reduce duplication and ensure consistency in testing patterns.
"""

from unittest.mock import MagicMock, Mock

import pytest
import pytest_asyncio

from semaphore_mcp.tools.environments import EnvironmentTools
from semaphore_mcp.tools.projects import ProjectTools
from semaphore_mcp.tools.repositories import RepositoryTools
from semaphore_mcp.tools.tasks import TaskTools
from semaphore_mcp.tools.templates import TemplateTools


# =============================================================================
# Mock API Client Fixtures
# =============================================================================


@pytest.fixture
def mock_semaphore_client():
    """Create a mock SemaphoreUI API client."""
    return MagicMock()


# =============================================================================
# Tool Instance Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def task_tools(mock_semaphore_client):
    """Create a TaskTools instance with a mock API client."""
    return TaskTools(mock_semaphore_client)


@pytest_asyncio.fixture
async def project_tools(mock_semaphore_client):
    """Create a ProjectTools instance with a mock API client."""
    return ProjectTools(mock_semaphore_client)


@pytest_asyncio.fixture
async def template_tools(mock_semaphore_client):
    """Create a TemplateTools instance with a mock API client."""
    return TemplateTools(mock_semaphore_client)


@pytest_asyncio.fixture
async def environment_tools(mock_semaphore_client):
    """Create an EnvironmentTools instance with a mock API client."""
    return EnvironmentTools(mock_semaphore_client)


@pytest_asyncio.fixture
async def repository_tools(mock_semaphore_client):
    """Create a RepositoryTools instance with a mock API client."""
    return RepositoryTools(mock_semaphore_client)


# =============================================================================
# Mock HTTP Response Fixtures
# =============================================================================


@pytest.fixture
def mock_http_response():
    """Factory fixture for creating mock HTTP responses.

    Usage:
        def test_something(mock_http_response):
            response = mock_http_response(status_code=200, json_data={"key": "value"})
    """

    def _make_response(status_code=200, json_data=None, content=b"", text=""):
        response = Mock()
        response.status_code = status_code
        response.content = content
        response.text = text or (content.decode() if content else "")
        response.json.return_value = json_data or {}
        response.raise_for_status.return_value = None
        return response

    return _make_response


@pytest.fixture
def mock_empty_response():
    """Create a mock empty response (204 No Content)."""
    response = Mock()
    response.status_code = 204
    response.content = b""
    response.raise_for_status.return_value = None
    return response


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_tasks():
    """Standard task list for testing."""
    return [
        {"id": 1, "created": "2023-06-01", "status": "success"},
        {"id": 2, "created": "2023-06-02", "status": "error"},
        {"id": 3, "created": "2023-06-03", "status": "running"},
        {"id": 4, "created": "2023-06-04", "status": "waiting"},
        {"id": 5, "created": "2023-06-05", "status": "success"},
    ]


@pytest.fixture
def sample_projects():
    """Standard project list for testing."""
    return [
        {"id": 1, "name": "Test Project 1"},
        {"id": 2, "name": "Test Project 2"},
    ]


@pytest.fixture
def sample_templates():
    """Standard template list for testing."""
    return [
        {"id": 1, "name": "Template 1", "project_id": 1, "playbook": "playbook1.yml"},
        {"id": 2, "name": "Template 2", "project_id": 1, "playbook": "playbook2.yml"},
    ]


@pytest.fixture
def sample_environments():
    """Standard environment list for testing."""
    return [
        {"id": 1, "name": "Staging", "project_id": 1, "json": '{"STAGE": "staging"}'},
        {
            "id": 2,
            "name": "Production",
            "project_id": 1,
            "json": '{"STAGE": "production"}',
        },
    ]


@pytest.fixture
def sample_repositories():
    """Standard repository list for testing."""
    return [
        {
            "id": 1,
            "name": "Demo",
            "project_id": 1,
            "git_url": "https://github.com/semaphoreui/semaphore-demo.git",
            "git_branch": "main",
            "ssh_key_id": 1,
        },
        {
            "id": 2,
            "name": "Production",
            "project_id": 1,
            "git_url": "https://github.com/example/production.git",
            "git_branch": "master",
            "ssh_key_id": 2,
        },
    ]


@pytest.fixture
def sample_inventory():
    """Standard inventory list for testing."""
    return [
        {
            "id": 1,
            "name": "Web Servers",
            "project_id": 1,
            "type": "file",
            "inventory": "[webservers]\n192.168.1.10\n192.168.1.11",
        },
        {
            "id": 2,
            "name": "DB Servers",
            "project_id": 1,
            "type": "file",
            "inventory": "[databases]\n192.168.1.20\n192.168.1.21",
        },
    ]
