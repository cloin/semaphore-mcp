"""
Unit tests for the task body built by SemaphoreAPIClient.run_task.
"""

from unittest.mock import Mock

import pytest

from semaphore_mcp.api import create_client


@pytest.fixture
def client():
    api = create_client("http://localhost:3000", "token")
    api._request = Mock(return_value={"id": 1})
    return api


def _payload(client):
    args, kwargs = client._request.call_args
    assert args == ("POST", "project/3/tasks")
    return kwargs["json"]


def test_run_task_without_params(client):
    client.run_task(3, 30)

    assert _payload(client) == {"template_id": 30}


def test_run_task_sends_params_object_as_is(client):
    params = {"destroy": True, "auto_approve": True}

    client.run_task(3, 30, params=params)

    payload = _payload(client)
    assert payload["params"] == params
    assert "destroy" not in payload
    assert "auto_approve" not in payload
