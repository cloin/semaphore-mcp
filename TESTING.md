# Testing Guide

This document describes the testing strategy for the Semaphore MCP server, including unit tests, integration tests, and end-to-end (E2E) tests.

## Overview

The project uses a multi-layered testing approach:

| Layer | Purpose | Tools | Location |
|-------|---------|-------|----------|
| Unit Tests | Test individual functions and classes | pytest, unittest.mock | `tests/` |
| E2E Tests | Test MCP tools against real Semaphore | MCP Inspector CLI | `tests/e2e/` |

## End-to-End Testing

E2E tests validate the MCP server by simulating real MCP client interactions using Anthropic's official [MCP Inspector CLI](https://github.com/modelcontextprotocol/inspector).

### How It Works

The E2E tests simulate exactly what happens when Claude (or any MCP client) calls your tools:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Test Runner   │────▶│  MCP Inspector  │────▶│   MCP Server    │────▶│  Semaphore API  │
│   (pytest)      │     │  (npx CLI)      │     │  (FastMCP)      │     │  (container)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Test Runner** (pytest) orchestrates the tests
2. **MCP Inspector** acts as a real MCP client, sending JSON-RPC requests
3. **MCP Server** (FastMCP server) processes tool calls
4. **Semaphore API** (Docker container) handles the actual operations

### The MCP Protocol Flow

When a test calls a tool like `list_projects`, the Inspector sends a standard MCP request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_projects",
    "arguments": {}
  }
}
```

The server responds with MCP-formatted content:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"projects\": [{\"id\": 1, \"name\": \"My Project\"}]}"
      }
    ]
  }
}
```

This is the **exact same protocol** that Claude uses when calling MCP tools.

### Running E2E Tests

#### Quick Start

```bash
./scripts/run-e2e-tests.sh
```

This script:
1. Builds and starts Semaphore + MCP server containers
2. Generates an API token for authentication
3. Runs all E2E test suites
4. Cleans up containers on exit

#### Manual Testing

For more control over the test environment:

```bash
# 1. Start the test containers
docker-compose -f docker-compose.test.yml up -d semaphore

# 2. Wait for Semaphore to be ready
curl http://localhost:3000/api/ping

# 3. Generate an API token
COOKIE_FILE=$(mktemp)
curl -c "$COOKIE_FILE" -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"auth": "admin", "password": "changeme123"}'

TOKEN=$(curl -b "$COOKIE_FILE" -X POST http://localhost:3000/api/user/tokens | \
  grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# 4. Start the MCP server with the token
export SEMAPHORE_API_TOKEN=$TOKEN
docker-compose -f docker-compose.test.yml up -d semaphore-mcp

# 5. Run specific tests
export MCP_SERVER_URL=http://localhost:8000
uv run pytest tests/e2e/test_projects_e2e.py -v

# 6. Clean up
docker-compose -f docker-compose.test.yml down -v
```

### Test Structure

#### Test Files

| File | Description | Tests |
|------|-------------|-------|
| `test_tool_registration.py` | Verifies all 37 MCP tools are registered | 1 |
| `test_projects_e2e.py` | Project CRUD operations | 5 |
| `test_environments_e2e.py` | Environment + Inventory CRUD | 10 |
| `test_repositories_e2e.py` | Repository operations (list only) | 1 |
| `test_templates_e2e.py` | Template operations (list only) | 1 |
| `test_tasks_e2e.py` | Task operations (list/filter) | 4 |

#### Shared Fixtures

The `tests/e2e/conftest.py` provides pytest fixtures:

- `inspector` - MCP Inspector client (session-scoped)
- `created_project` - Creates a project, yields it, then cleans up
- `created_environment` - Creates an environment with cleanup
- `created_inventory` - Creates an inventory with cleanup

#### Helper Functions

From `tests/e2e/helpers.py`:

```python
def parse_mcp_response(response: dict) -> Any:
    """Extract data from MCP response wrapper.

    MCP returns: {"content": [{"type": "text", "text": "...json..."}]}
    This extracts and parses the JSON from the text field.
    """
```

### Writing New E2E Tests

#### Basic Test Structure

```python
"""E2E tests for MyFeature tools."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from helpers import parse_mcp_response
from mcp_inspector import MCPInspector


class TestMyFeatureE2E:
    """E2E tests for my feature."""

    def test_list_items(self, inspector: MCPInspector, created_project: dict):
        """Test listing items."""
        project_id = created_project["id"]

        result = inspector.call_tool(
            "list_items",
            {"project_id": project_id}
        )
        data = parse_mcp_response(result)

        assert "items" in data
        assert isinstance(data["items"], list)

    def test_crud_workflow(self, inspector: MCPInspector, created_project: dict):
        """Test complete CRUD lifecycle."""
        project_id = created_project["id"]

        # Create
        result = inspector.call_tool(
            "create_item",
            {"project_id": project_id, "name": "Test Item"}
        )
        item = parse_mcp_response(result)
        item_id = item["id"]

        try:
            # Read
            result = inspector.call_tool(
                "get_item",
                {"project_id": project_id, "item_id": item_id}
            )
            assert parse_mcp_response(result)["id"] == item_id

            # Update
            inspector.call_tool(
                "update_item",
                {"project_id": project_id, "item_id": item_id, "name": "Updated"}
            )

        finally:
            # Always clean up
            inspector.call_tool(
                "delete_item",
                {"project_id": project_id, "item_id": item_id}
            )
```

#### Using the MCP Inspector Directly

For ad-hoc testing or debugging:

```bash
# List all registered tools
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp \
  --transport http \
  --method tools/list

# Call a specific tool
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp \
  --transport http \
  --method tools/call \
  --tool-name list_projects

# Call with arguments
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp \
  --transport http \
  --method tools/call \
  --tool-name create_project \
  --tool-arg 'name="My Test Project"'
```

### CI/CD Integration

E2E tests run automatically in GitHub Actions on:
- Push to `main` or `develop`
- Pull requests to `main`
- Manual workflow dispatch

See `.github/workflows/test-mcp-integration.yml` for the workflow configuration.

## Unit Tests

Unit tests use mocked dependencies to test individual components in isolation.

### Running Unit Tests

```bash
# Run all unit tests
uv run pytest tests/ --ignore=tests/e2e/ -v

# Run with coverage
uv run pytest tests/ --ignore=tests/e2e/ --cov=src/semaphore_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_api_client.py -v
```

### Test Categories

| File | Description |
|------|-------------|
| `test_api_client.py` | SemaphoreUI API client |
| `test_config.py` | Configuration loading |
| `test_mcp_server.py` | MCP server initialization |
| `test_task_tools_coverage.py` | Task tool methods |
| `test_environment_tools_coverage.py` | Environment tool methods |

## Test Coverage

To generate a coverage report:

```bash
uv run pytest tests/ --cov=src/semaphore_mcp --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### MCP Inspector Connection Issues

```bash
# Verify the server is running
curl -s http://localhost:8000/mcp -w "\nHTTP: %{http_code}\n"

# Check container logs
docker-compose -f docker-compose.test.yml logs semaphore-mcp
```

### Semaphore Container Issues

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' semaphore-test

# View startup logs
docker-compose -f docker-compose.test.yml logs semaphore
```

### API Token Issues

```bash
# Verify Semaphore is accessible
curl http://localhost:3000/api/ping

# Check the MCP server has a valid token
docker-compose -f docker-compose.test.yml exec semaphore-mcp env | grep SEMAPHORE
```
