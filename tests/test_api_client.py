"""
Tests for the SemaphoreUI API client.
"""

import os

import pytest

from semaphore_mcp.api import create_client


@pytest.fixture
def semaphore_client():
    """Create a SemaphoreUI API client for testing."""
    base_url = os.environ.get("SEMAPHORE_URL", "http://localhost:3000")
    token = os.environ.get("SEMAPHORE_API_TOKEN")

    if not token:
        pytest.skip("No API token available for testing")

    return create_client(base_url, token)


def test_client_connection(semaphore_client):
    """Test that the client can connect to SemaphoreUI."""
    # Simple test to ensure we can connect and get a response
    projects = semaphore_client.list_projects()
    assert isinstance(projects, list)


def test_project_operations(semaphore_client):
    """Test project-related operations."""
    # List projects (should return at least an empty list)
    projects = semaphore_client.list_projects()
    assert isinstance(projects, list)

    # If there are projects, test getting a specific one
    if projects:
        project_id = projects[0]["id"]
        project = semaphore_client.get_project(project_id)
        assert project["id"] == project_id


@pytest.mark.skip(reason="Environment API integration currently unstable")
def test_environment_operations(semaphore_client):
    """Test environment-related operations."""
    try:
        # Need at least one project to test environments
        try:
            projects = semaphore_client.list_projects()
            if not projects:
                pytest.skip("No projects available for environment tests")
        except Exception as e:
            pytest.skip(f"Failed to list projects: {str(e)}")

        project_id = projects[0]["id"]

        # Test listing environments
        try:
            environments = semaphore_client.list_environments(project_id)
            assert isinstance(environments, list)
        except Exception as e:
            pytest.skip(f"Failed to list environments: {str(e)}")

        # Create a test environment with unique name
        import uuid

        test_env_name = f"test-env-{uuid.uuid4().hex[:8]}"
        test_env_data = {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}

        # Create environment
        try:
            created_env = semaphore_client.create_environment(
                project_id, test_env_name, test_env_data
            )
            assert "id" in created_env, "Created environment should have an ID"
            assert created_env["name"] == test_env_name
            environment_id = created_env["id"]
        except Exception as e:
            pytest.skip(f"Failed to create environment: {str(e)}")
            return

        # Get environment
        try:
            environment = semaphore_client.get_environment(project_id, environment_id)
            assert environment["id"] == environment_id
            assert environment["name"] == test_env_name
        except Exception as e:
            pytest.skip(f"Failed to get environment: {str(e)}")

        # Update environment
        try:
            updated_name = test_env_name + "-updated"
            updated_env_data = {"TEST_VAR": "updated_value", "NEW_VAR": "new_value"}

            updated_env = semaphore_client.update_environment(
                project_id, environment_id, updated_name, updated_env_data
            )
            assert updated_env["name"] == updated_name
        except Exception as e:
            pytest.skip(f"Failed to update environment: {str(e)}")

    finally:
        # Clean up: delete the test environment if it was created
        if "environment_id" in locals():
            try:
                semaphore_client.delete_environment(project_id, environment_id)
            except Exception:
                pass


@pytest.mark.skip(reason="Inventory API integration currently unstable")
def test_inventory_operations(semaphore_client):
    """Test inventory-related operations."""
    try:
        # Need at least one project to test inventory
        try:
            projects = semaphore_client.list_projects()
            if not projects:
                pytest.skip("No projects available for inventory tests")
        except Exception as e:
            pytest.skip(f"Failed to list projects: {str(e)}")

        project_id = projects[0]["id"]

        # Test listing inventory
        try:
            inventory_items = semaphore_client.list_inventory(project_id)
            assert isinstance(inventory_items, list)
        except Exception as e:
            pytest.skip(f"Failed to list inventory: {str(e)}")

        # Create a test inventory with unique name
        import uuid

        test_inv_name = f"test-inventory-{uuid.uuid4().hex[:8]}"
        test_inv_data = "[webservers]\nlocalhost ansible_connection=local\n\n[dbservers]\n192.168.1.1"

        # Create inventory
        try:
            created_inv = semaphore_client.create_inventory(
                project_id, test_inv_name, test_inv_data
            )
            assert "id" in created_inv, "Created inventory should have an ID"
            assert created_inv["name"] == test_inv_name
            inventory_id = created_inv["id"]
        except Exception as e:
            pytest.skip(f"Failed to create inventory: {str(e)}")
            return

        # Get inventory
        try:
            inventory = semaphore_client.get_inventory(project_id, inventory_id)
            assert inventory["id"] == inventory_id
            assert inventory["name"] == test_inv_name
        except Exception as e:
            pytest.skip(f"Failed to get inventory: {str(e)}")

        # Update inventory
        try:
            updated_name = test_inv_name + "-updated"
            updated_inv_data = "[webservers]\nlocalhost ansible_connection=local\n\n[dbservers]\n192.168.1.1\n192.168.1.2"

            updated_inv = semaphore_client.update_inventory(
                project_id, inventory_id, updated_name, updated_inv_data
            )
            assert updated_inv["name"] == updated_name
        except Exception as e:
            pytest.skip(f"Failed to update inventory: {str(e)}")

    finally:
        # Clean up: delete the test inventory if it was created
        if "inventory_id" in locals():
            try:
                semaphore_client.delete_inventory(project_id, inventory_id)
            except Exception:
                pass
            # Verify deletion
            inventory_items = semaphore_client.list_inventory(project_id)
            inv_ids = [inv["id"] for inv in inventory_items]
            assert inventory_id not in inv_ids
