"""
Comprehensive tests for the SemaphoreUI API client.
These tests focus on improving coverage of API methods.
"""

import json
import os
from unittest.mock import Mock, patch

import pytest

from semaphore_mcp.api import SemaphoreAPIClient, create_client


class TestSemaphoreAPIClientComprehensive:
    """Comprehensive test suite for API client methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a real API client instance for testing."""
        return SemaphoreAPIClient("http://test.example.com", "test-token")

    # Note: mock_http_response and mock_empty_response fixtures are available from conftest.py
    # We use inline fixtures here because these tests need specific response configurations

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object with success data."""
        response = Mock()
        response.status_code = 200
        response.content = b'{"result": "success"}'
        response.json.return_value = {"result": "success"}
        response.raise_for_status.return_value = None
        return response

    @pytest.fixture
    def empty_response(self, mock_empty_response):
        """Use shared empty response fixture."""
        return mock_empty_response

    def test_request_empty_response(self, mock_client, empty_response):
        """Test _request method with empty response content."""
        with patch.object(
            mock_client.session, "request", return_value=empty_response
        ) as mock_request:
            result = mock_client._request("GET", "test")
            assert result == {}
            mock_request.assert_called_once_with(
                "GET", "http://test.example.com/api/test", timeout=30.0
            )

    def test_request_with_content(self, mock_client, mock_response):
        """Test _request method with response content."""
        with patch.object(mock_client.session, "request", return_value=mock_response):
            result = mock_client._request("GET", "test")
            assert result == {"result": "success"}

    def test_request_preserves_explicit_timeout(self, mock_client, mock_response):
        """Test _request does not override an explicit per-call timeout."""
        with patch.object(
            mock_client.session, "request", return_value=mock_response
        ) as mock_request:
            result = mock_client._request("GET", "test", timeout=5)
            assert result == {"result": "success"}
            mock_request.assert_called_once_with(
                "GET", "http://test.example.com/api/test", timeout=5
            )

    def test_list_projects_dict_response(self, mock_client):
        """Test list_projects when API returns dict instead of list."""
        mock_response = {"projects": [{"id": 1, "name": "test"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_projects()
            assert result == []  # Should return empty list for non-list response

    def test_list_projects_list_response(self, mock_client):
        """Test list_projects when API returns list."""
        mock_response = [{"id": 1, "name": "test"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_projects()
            assert result == mock_response

    def test_get_project(self, mock_client):
        """Test get_project method."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_project(1)
            assert result == mock_response

    def test_list_templates_dict_response(self, mock_client):
        """Test list_templates when API returns dict instead of list."""
        mock_response = {"templates": [{"id": 1, "name": "test"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_templates(1)
            assert result == []  # Should return empty list for non-list response

    def test_list_templates_list_response(self, mock_client):
        """Test list_templates when API returns list."""
        mock_response = [{"id": 1, "name": "test"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_templates(1)
            assert result == mock_response

    def test_get_template(self, mock_client):
        """Test get_template method."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_template(1, 1)
            assert result == mock_response

    def test_list_tasks_dict_response(self, mock_client):
        """Test list_tasks when API returns dict instead of list."""
        mock_response = {"tasks": [{"id": 1, "status": "success"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_tasks(1)
            assert result == []  # Should return empty list for non-list response

    def test_list_tasks_list_response(self, mock_client):
        """Test list_tasks when API returns list."""
        mock_response = [{"id": 1, "status": "success"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_tasks(1)
            assert result == mock_response

    def test_get_task(self, mock_client):
        """Test get_task method."""
        mock_response = {"id": 1, "status": "success"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.get_task(1, 1)
            assert result == mock_response
            mock_request.assert_called_once_with("GET", "project/1/tasks/1")

    def test_run_task_basic(self, mock_client):
        """Test run_task method without environment."""
        mock_response = {"id": 1, "status": "started"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.run_task(1, 1)
            assert result == mock_response

    def test_run_task_with_environment(self, mock_client):
        """Test run_task method with environment variables."""
        import json

        mock_response = {"id": 1, "status": "started"}
        environment = {"VAR1": "value1", "VAR2": "value2"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.run_task(1, 1, environment)
            assert result == mock_response
            # Verify environment was passed in payload as JSON string
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            # Semaphore API expects environment as JSON string
            assert kwargs["json"]["environment"] == json.dumps(environment)

    def test_stop_task(self, mock_client):
        """Test stop_task method."""
        mock_response = {"status": "stopped"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.stop_task(1, 1)
            assert result == mock_response

    def test_get_last_tasks_dict_response(self, mock_client):
        """Test get_last_tasks when API returns dict instead of list."""
        mock_response = {"tasks": [{"id": 1, "status": "success"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_last_tasks(1)
            assert result == []  # Should return empty list for non-list response

    def test_get_last_tasks_list_response(self, mock_client):
        """Test get_last_tasks when API returns list."""
        mock_response = [{"id": 1, "status": "success"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_last_tasks(1)
            assert result == mock_response

    def test_get_task_raw_output(self, mock_client):
        """Test get_task_raw_output method."""
        mock_response = Mock()
        mock_response.text = "raw task output"
        mock_response.raise_for_status.return_value = None
        with patch.object(
            mock_client.session, "request", return_value=mock_response
        ) as mock_request:
            result = mock_client.get_task_raw_output(1, 1)
            assert result == "raw task output"
            mock_request.assert_called_once_with(
                "GET",
                "http://test.example.com/api/project/1/tasks/1/raw_output",
                timeout=30.0,
            )

    def test_delete_task(self, mock_client):
        """Test delete_task method."""
        mock_response = {"status": "deleted"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.delete_task(1, 1)
            assert result == mock_response

    def test_restart_task(self, mock_client):
        """Test restart_task method."""
        mock_response = {"status": "restarted"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.restart_task(1, 1)
            assert result == mock_response

    def test_list_schedules_dict_response(self, mock_client):
        """Test list_schedules when API returns dict instead of list."""
        mock_response = {"schedules": [{"id": 1, "name": "nightly"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_schedules(1)
            assert result == []

    def test_list_schedules_list_response(self, mock_client):
        """Test list_schedules when API returns list."""
        mock_response = [{"id": 1, "name": "nightly"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_schedules(1)
            assert result == mock_response

    def test_list_template_schedules(self, mock_client):
        """Test list_template_schedules method."""
        mock_response = [{"id": 1, "template_id": 2}]
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.list_template_schedules(1, 2)
            assert result == mock_response
            mock_request.assert_called_once_with(
                "GET", "project/1/templates/2/schedules"
            )

    def test_get_schedule(self, mock_client):
        """Test get_schedule method."""
        mock_response = {"id": 1, "name": "nightly"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.get_schedule(1, 1)
            assert result == mock_response
            mock_request.assert_called_once_with("GET", "project/1/schedules/1")

    def test_create_cron_schedule(self, mock_client):
        """Test create_schedule method for cron schedules."""
        mock_response = {"id": 1, "name": "nightly"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_schedule(
                1,
                2,
                "nightly",
                cron_format="0 0 * * *",
                active=False,
                task_params={"message": "scheduled"},
            )
            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST",
                "project/1/schedules",
                json={
                    "project_id": 1,
                    "template_id": 2,
                    "name": "nightly",
                    "active": False,
                    "type": "",
                    "cron_format": "0 0 * * *",
                    "task_params": {"message": "scheduled"},
                },
            )

    def test_create_run_at_schedule(self, mock_client):
        """Test create_schedule method for one-time schedules."""
        mock_response = {"id": 1, "type": "run_at"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_schedule(
                1,
                2,
                "maintenance",
                active=False,
                schedule_type="run_at",
                run_at="2026-05-19T12:00:00Z",
                delete_after_run=True,
            )
            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST",
                "project/1/schedules",
                json={
                    "project_id": 1,
                    "template_id": 2,
                    "name": "maintenance",
                    "active": False,
                    "type": "run_at",
                    "run_at": "2026-05-19T12:00:00Z",
                    "delete_after_run": True,
                },
            )

    def test_update_schedule_preserves_existing_fields(self, mock_client):
        """Test update_schedule fetches existing schedule and preserves fields."""
        existing = {
            "id": 3,
            "project_id": 1,
            "template_id": 2,
            "name": "nightly",
            "cron_format": "0 0 * * *",
            "active": False,
            "type": "",
            "delete_after_run": False,
        }
        with patch.object(
            mock_client, "_request", side_effect=[existing, {}]
        ) as mock_request:
            result = mock_client.update_schedule(1, 3, name="updated", active=True)
            assert result == {}
            assert mock_request.call_count == 2
            mock_request.assert_any_call("GET", "project/1/schedules/3")
            mock_request.assert_any_call(
                "PUT",
                "project/1/schedules/3",
                json={
                    "id": 3,
                    "project_id": 1,
                    "template_id": 2,
                    "name": "updated",
                    "cron_format": "0 0 * * *",
                    "active": True,
                    "type": "",
                    "run_at": None,
                    "delete_after_run": False,
                },
            )

    def test_set_schedule_active(self, mock_client):
        """Test set_schedule_active method."""
        with patch.object(mock_client, "_request", return_value={}) as mock_request:
            result = mock_client.set_schedule_active(1, 3, False)
            assert result == {}
            mock_request.assert_called_once_with(
                "PUT", "project/1/schedules/3/active", json={"active": False}
            )

    def test_delete_schedule(self, mock_client):
        """Test delete_schedule method."""
        with patch.object(mock_client, "_request", return_value={}) as mock_request:
            result = mock_client.delete_schedule(1, 3)
            assert result == {}
            mock_request.assert_called_once_with("DELETE", "project/1/schedules/3")

    def test_validate_schedule_cron_format(self, mock_client):
        """Test validate_schedule_cron_format method."""
        with patch.object(mock_client, "_request", return_value={}) as mock_request:
            result = mock_client.validate_schedule_cron_format(1, "0 0 * * *")
            assert result == {}
            mock_request.assert_called_once_with(
                "POST",
                "project/1/schedules/validate",
                json={"cron_format": "0 0 * * *"},
            )

    def test_list_environments_dict_response(self, mock_client):
        """Test list_environments when API returns dict instead of list."""
        mock_response = {"environments": [{"id": 1, "name": "test"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_environments(1)
            assert result == []  # Should return empty list for non-list response

    def test_list_environments_list_response(self, mock_client):
        """Test list_environments when API returns list."""
        mock_response = [{"id": 1, "name": "test"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_environments(1)
            assert result == mock_response

    def test_get_environment(self, mock_client):
        """Test get_environment method."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_environment(1, 1)
            assert result == mock_response

    def test_create_environment_basic(self, mock_client):
        """Test create_environment method without env_data."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.create_environment(1, "test", {})
            assert result == mock_response

    def test_create_environment_with_data(self, mock_client):
        """Test create_environment method with env_data."""
        mock_response = {"id": 1, "name": "test"}
        env_data = {"VAR1": "value1", "VAR2": "value2"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_environment(1, "test", env_data)
            assert result == mock_response
            # Verify env_data was JSON encoded
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["json"] == json.dumps(env_data)

    def test_update_environment_name_only(self, mock_client):
        """Test update_environment method with name only."""
        mock_response = {"id": 1, "name": "updated"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_environment(1, 1, "updated")
            assert result == mock_response
            # Verify only name was updated
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["name"] == "updated"
            assert "json" not in kwargs["json"]  # env_data not included

    def test_update_environment_data_only(self, mock_client):
        """Test update_environment method with env_data only."""
        mock_response = {"id": 1, "name": "test"}
        env_data = {"VAR1": "value1"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_environment(1, 1, env_data=env_data)
            assert result == mock_response
            # Verify env_data was JSON encoded
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["json"] == json.dumps(env_data)
            assert "name" not in kwargs["json"]  # name not included

    def test_update_environment_both(self, mock_client):
        """Test update_environment method with both name and env_data."""
        mock_response = {"id": 1, "name": "updated"}
        env_data = {"VAR1": "value1"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_environment(1, 1, "updated", env_data)
            assert result == mock_response
            # Verify both were included
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["name"] == "updated"
            assert kwargs["json"]["json"] == json.dumps(env_data)

    def test_delete_environment(self, mock_client):
        """Test delete_environment method."""
        mock_response = {"status": "deleted"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.delete_environment(1, 1)
            assert result == mock_response

    def test_list_inventory_dict_response(self, mock_client):
        """Test list_inventory when API returns dict instead of list."""
        mock_response = {"inventory": [{"id": 1, "name": "test"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_inventory(1)
            assert result == []  # Should return empty list for non-list response

    def test_list_inventory_list_response(self, mock_client):
        """Test list_inventory when API returns list."""
        mock_response = [{"id": 1, "name": "test"}]
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.list_inventory(1)
            assert result == mock_response

    def test_get_inventory(self, mock_client):
        """Test get_inventory method."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_inventory(1, 1)
            assert result == mock_response

    def test_create_inventory_basic(self, mock_client):
        """Test create_inventory method without inventory_data."""
        mock_response = {"id": 1, "name": "test"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_inventory(1, "test", "")
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert args == ("POST", "project/1/inventory")
            assert kwargs["json"] == {
                "name": "test",
                "type": "static",
                "project_id": 1,
            }

    def test_create_inventory_with_data(self, mock_client):
        """Test create_inventory method with inventory_data."""
        mock_response = {"id": 1, "name": "test"}
        inventory_data = "[webservers]\nlocalhost"
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_inventory(1, "test", inventory_data)
            assert result == mock_response
            # Verify inventory_data was included
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["type"] == "static"
            assert kwargs["json"]["inventory"] == inventory_data

    def test_create_inventory_with_file_type(self, mock_client):
        """Test create_inventory method with a file-backed inventory."""
        mock_response = {"id": 1, "name": "test"}
        inventory_path = "inventories/hosts.ini"
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_inventory(
                1, "test", inventory_path, inventory_type="file"
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert args == ("POST", "project/1/inventory")
            assert kwargs["json"] == {
                "name": "test",
                "type": "file",
                "project_id": 1,
                "inventory": inventory_path,
            }

    def test_update_inventory_name_only(self, mock_client):
        """Test update_inventory method with name only."""
        mock_response = {"id": 1, "name": "updated"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_inventory(1, 1, "updated")
            assert result == mock_response
            # Verify only name was updated
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["type"] == "static"
            assert kwargs["json"]["name"] == "updated"
            assert "inventory" not in kwargs["json"]  # inventory_data not included

    def test_update_inventory_data_only(self, mock_client):
        """Test update_inventory method with inventory_data only."""
        mock_response = {"id": 1, "name": "test"}
        inventory_data = "[webservers]\nlocalhost"
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_inventory(1, 1, inventory_data=inventory_data)
            assert result == mock_response
            # Verify inventory_data was included
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["type"] == "static"
            assert kwargs["json"]["inventory"] == inventory_data
            assert "name" not in kwargs["json"]  # name not included

    def test_update_inventory_both(self, mock_client):
        """Test update_inventory method with both name and inventory_data."""
        mock_response = {"id": 1, "name": "updated"}
        inventory_data = "[webservers]\nlocalhost"
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_inventory(1, 1, "updated", inventory_data)
            assert result == mock_response
            # Verify both were included
            args, kwargs = mock_request.call_args
            assert "json" in kwargs
            assert kwargs["json"]["type"] == "static"
            assert kwargs["json"]["name"] == "updated"
            assert kwargs["json"]["inventory"] == inventory_data

    def test_update_inventory_with_file_type(self, mock_client):
        """Test update_inventory method with a file-backed inventory."""
        mock_response = {"id": 1, "name": "updated"}
        inventory_path = "inventories/hosts.ini"
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_inventory(
                1,
                1,
                "updated",
                inventory_path,
                inventory_type="file",
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert args == ("PUT", "project/1/inventory/1")
            assert kwargs["json"] == {
                "type": "file",
                "project_id": 1,
                "id": 1,
                "name": "updated",
                "inventory": inventory_path,
            }

    def test_delete_inventory(self, mock_client):
        """Test delete_inventory method."""
        mock_response = {"status": "deleted"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.delete_inventory(1, 1)
            assert result == mock_response


class TestProjectCRUDOperations:
    """Test project CRUD operations in API client."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client for testing."""
        return SemaphoreAPIClient("http://test.example.com", "test-token")

    def test_create_project_basic(self, mock_client):
        """Test create_project with basic parameters."""
        mock_response = {"id": 1, "name": "test-project"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_project("test-project")
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["name"] == "test-project"
            assert kwargs["json"]["alert"] is False
            assert kwargs["json"]["max_parallel_tasks"] == 0
            assert kwargs["json"]["demo"] is False

    def test_create_project_with_all_options(self, mock_client):
        """Test create_project with all optional parameters."""
        mock_response = {"id": 1, "name": "test-project"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_project(
                name="test-project",
                alert=True,
                alert_chat="slack-channel",
                max_parallel_tasks=5,
                project_type="ansible",
                demo=True,
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["name"] == "test-project"
            assert kwargs["json"]["alert"] is True
            assert kwargs["json"]["alert_chat"] == "slack-channel"
            assert kwargs["json"]["max_parallel_tasks"] == 5
            assert kwargs["json"]["type"] == "ansible"
            assert kwargs["json"]["demo"] is True

    def test_update_project_name_only(self, mock_client):
        """Test update_project with name only."""
        mock_response = {}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_project(1, name="updated-name")
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["id"] == 1
            assert kwargs["json"]["name"] == "updated-name"

    def test_update_project_all_fields(self, mock_client):
        """Test update_project with all fields."""
        mock_response = {}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_project(
                project_id=1,
                name="updated-name",
                alert=True,
                alert_chat="new-channel",
                max_parallel_tasks=10,
                project_type="terraform",
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["id"] == 1
            assert kwargs["json"]["name"] == "updated-name"
            assert kwargs["json"]["alert"] is True
            assert kwargs["json"]["alert_chat"] == "new-channel"
            assert kwargs["json"]["max_parallel_tasks"] == 10
            assert kwargs["json"]["type"] == "terraform"

    def test_delete_project(self, mock_client):
        """Test delete_project method."""
        mock_response = {}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.delete_project(1)
            assert result == mock_response


class TestTemplateCRUDOperations:
    """Test template CRUD operations in API client."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client for testing."""
        return SemaphoreAPIClient("http://test.example.com", "test-token")

    def test_create_template_basic(self, mock_client):
        """Test create_template with required parameters."""
        mock_response = {"id": 1, "name": "test-template"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_template(
                project_id=1,
                name="test-template",
                playbook="playbook.yml",
                inventory_id=1,
                repository_id=1,
                environment_id=1,
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["project_id"] == 1
            assert kwargs["json"]["name"] == "test-template"
            assert kwargs["json"]["playbook"] == "playbook.yml"
            assert kwargs["json"]["inventory_id"] == 1
            assert kwargs["json"]["repository_id"] == 1
            assert kwargs["json"]["environment_id"] == 1

    def test_create_template_with_all_options(self, mock_client):
        """Test create_template with all optional parameters."""
        mock_response = {"id": 1, "name": "test-template"}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.create_template(
                project_id=1,
                name="test-template",
                playbook="playbook.yml",
                inventory_id=1,
                repository_id=1,
                environment_id=1,
                description="Test description",
                arguments='["--check"]',
                allow_override_args_in_task=True,
                suppress_success_alerts=True,
                app="ansible",
                git_branch="main",
                survey_vars=[{"name": "var1", "title": "Variable 1"}],
                vaults=[{"name": "vault1"}],
                template_type="build",
                start_version="1.0.0",
                build_template_id=2,
                autorun=True,
                view_id=1,
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["description"] == "Test description"
            assert kwargs["json"]["arguments"] == '["--check"]'
            assert kwargs["json"]["allow_override_args_in_task"] is True
            assert kwargs["json"]["suppress_success_alerts"] is True
            assert kwargs["json"]["git_branch"] == "main"
            assert kwargs["json"]["survey_vars"] == [
                {"name": "var1", "title": "Variable 1"}
            ]
            assert kwargs["json"]["vaults"] == [{"name": "vault1"}]
            assert kwargs["json"]["type"] == "build"
            assert kwargs["json"]["start_version"] == "1.0.0"
            assert kwargs["json"]["build_template_id"] == 2
            assert kwargs["json"]["autorun"] is True
            assert kwargs["json"]["view_id"] == 1

    def test_update_template_partial(self, mock_client):
        """Test update_template with partial fields."""
        mock_response = {}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_template(
                project_id=1,
                template_id=1,
                name="updated-template",
                playbook="new-playbook.yml",
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            assert kwargs["json"]["id"] == 1
            assert kwargs["json"]["project_id"] == 1
            assert kwargs["json"]["name"] == "updated-template"
            assert kwargs["json"]["playbook"] == "new-playbook.yml"

    def test_update_template_all_fields(self, mock_client):
        """Test update_template with all fields."""
        mock_response = {}
        with patch.object(
            mock_client, "_request", return_value=mock_response
        ) as mock_request:
            result = mock_client.update_template(
                project_id=1,
                template_id=1,
                name="updated-template",
                playbook="new-playbook.yml",
                inventory_id=2,
                repository_id=2,
                environment_id=2,
                description="Updated description",
                arguments='["--diff"]',
                allow_override_args_in_task=False,
                suppress_success_alerts=False,
                app="terraform",
                git_branch="develop",
                survey_vars=[{"name": "var2"}],
                vaults=[{"name": "vault2"}],
                template_type="deploy",
                start_version="2.0.0",
                build_template_id=3,
                autorun=False,
                view_id=2,
            )
            assert result == mock_response
            args, kwargs = mock_request.call_args
            payload = kwargs["json"]
            assert payload["name"] == "updated-template"
            assert payload["playbook"] == "new-playbook.yml"
            assert payload["inventory_id"] == 2
            assert payload["repository_id"] == 2
            assert payload["environment_id"] == 2
            assert payload["description"] == "Updated description"
            assert payload["arguments"] == '["--diff"]'
            assert payload["allow_override_args_in_task"] is False
            assert payload["suppress_success_alerts"] is False
            assert payload["app"] == "terraform"
            assert payload["git_branch"] == "develop"
            assert payload["survey_vars"] == [{"name": "var2"}]
            assert payload["vaults"] == [{"name": "vault2"}]
            assert payload["type"] == "deploy"
            assert payload["start_version"] == "2.0.0"
            assert payload["build_template_id"] == 3
            assert payload["autorun"] is False
            assert payload["view_id"] == 2

    def test_delete_template(self, mock_client):
        """Test delete_template method."""
        mock_response = {}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.delete_template(1, 1)
            assert result == mock_response

    def test_stop_all_template_tasks(self, mock_client):
        """Test stop_all_template_tasks method."""
        mock_response = {}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.stop_all_template_tasks(1, 1)
            assert result == mock_response


class TestAPIClientErrorHandling:
    """Test API client error handling."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client for testing."""
        return SemaphoreAPIClient("http://test.example.com", "test-token")

    def test_request_404_error_enhanced_message(self, mock_client):
        """Test that 404 errors get enhanced error messages."""
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b""
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        with patch.object(mock_client.session, "request", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError) as exc_info:
                mock_client._request("GET", "project/999")
            assert "Resource not found (404)" in str(exc_info.value)
            assert "may have been deleted" in str(exc_info.value)

    def test_request_http_error_includes_response_body(self, mock_client):
        """Test that HTTP errors include Semaphore's response body."""
        import requests

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"error":"Cron: empty spec string"}'
        mock_response.text = '{"error":"Cron: empty spec string"}'
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        with patch.object(mock_client.session, "request", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError) as exc_info:
                mock_client._request("POST", "project/1/schedules")
            assert (
                "POST http://test.example.com/api/project/1/schedules failed with 400"
                in str(exc_info.value)
            )
            assert "Cron: empty spec string" in str(exc_info.value)
            assert exc_info.value.response is mock_response

    def test_request_invalid_json_response(self, mock_client):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"not valid json"
        mock_response.text = "not valid json"
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)

        with patch.object(mock_client.session, "request", return_value=mock_response):
            with pytest.raises(ValueError) as exc_info:
                mock_client._request("GET", "test")
            assert "Invalid JSON response" in str(exc_info.value)


class TestCreateClientFunction:
    """Test the create_client factory function."""

    def test_create_client_with_parameters(self):
        """Test create_client with explicit parameters."""
        client = create_client("http://test.example.com", "test-token")
        assert client.base_url == "http://test.example.com"
        assert client.token == "test-token"

    def test_create_client_with_base_url_only(self):
        """Test create_client with base_url only."""
        client = create_client("http://test.example.com")
        assert client.base_url == "http://test.example.com"

    @patch.dict(os.environ, {"SEMAPHORE_URL": "http://env.example.com"})
    def test_create_client_from_environment(self):
        """Test create_client using environment variables."""
        client = create_client()
        assert client.base_url == "http://env.example.com"

    def test_create_client_default_url(self):
        """Test create_client with default URL when no environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            client = create_client()
            assert client.base_url == "http://localhost:3000"


class TestAPIClientInitialization:
    """Test API client initialization and configuration."""

    def test_init_with_token(self):
        """Test client initialization with token."""
        client = SemaphoreAPIClient("http://test.example.com", "test-token")
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test-token"
        assert client.request_timeout == 30.0

    def test_init_with_custom_request_timeout(self):
        """Test client initialization with a custom request timeout."""
        client = SemaphoreAPIClient(
            "http://test.example.com", "test-token", request_timeout=10
        )
        assert client.request_timeout == 10

    def test_init_without_token(self):
        """Test client initialization without token."""
        with patch.dict(os.environ, {}, clear=True):
            client = SemaphoreAPIClient("http://test.example.com")
            assert "Authorization" not in client.session.headers

    @patch.dict(os.environ, {"SEMAPHORE_API_TOKEN": "env-token"})
    def test_init_token_from_environment(self):
        """Test client initialization getting token from environment."""
        client = SemaphoreAPIClient("http://test.example.com")
        assert client.token == "env-token"
        assert client.session.headers["Authorization"] == "Bearer env-token"

    def test_base_url_stripping(self):
        """Test that trailing slashes are stripped from base URL."""
        client = SemaphoreAPIClient("http://test.example.com/")
        assert client.base_url == "http://test.example.com"

    def test_default_headers(self):
        """Test that default headers are set correctly."""
        client = SemaphoreAPIClient("http://test.example.com")
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["Accept"] == "application/json"
