# End-to-End MCP Integration Tests

This directory contains end-to-end tests for the Semaphore MCP server using the [MCP Inspector CLI](https://github.com/modelcontextprotocol/inspector).

> **Note:** For comprehensive testing documentation including how the MCP protocol flow works, see [TESTING.md](../../TESTING.md) in the project root.

## Overview

These tests validate the MCP server by:
1. Starting both Semaphore and Semaphore-MCP containers
2. Using MCP Inspector CLI to interact with the server as a real MCP client
3. Testing all 37 MCP tools across different scenarios
4. Verifying correct integration with SemaphoreUI

## Test Structure

### Core Files

| File | Description |
|------|-------------|
| `conftest.py` | Shared pytest fixtures (inspector, parse_mcp_response, created_project, etc.) |
| `mcp_inspector.py` | Python wrapper around the MCP Inspector CLI |

### Test Files

| File | Description | Tests Enabled |
|------|-------------|---------------|
| `test_tool_registration.py` | Verifies all 37 MCP tools are registered | Yes |
| `test_projects_e2e.py` | Project CRUD operations | Yes |
| `test_environments_e2e.py` | Environment + Inventory CRUD | Yes |
| `test_repositories_e2e.py` | Repository operations (requires SSH key) | List only |
| `test_templates_e2e.py` | Template operations (requires full setup) | List only |
| `test_tasks_e2e.py` | Task operations (requires templates) | List/filter only |
| `test_comprehensive_scenario.py` | Full deployment scenario | No (requires setup) |

### Expected Tools (37 total)

- **Projects** (5): list, get, create, update, delete
- **Templates** (6): list, get, create, update, delete, stop_all_tasks
- **Tasks** (11): list, get, run, stop, filter, bulk_stop, get_waiting, get_latest_failed, get_raw_output, analyze_failure, bulk_analyze_failures
- **Environments** (10): environment and inventory CRUD operations
- **Repositories** (5): list, get, create, update, delete

### 🚀 `test_comprehensive_scenario.py`
**Real-world simulation** that exercises multiple tools in a realistic deployment scenario:

1. Create project
2. Create environment variables
3. Create inventory
4. Create repository
5. Create task template
6. Run task
7. Monitor execution
8. Analyze results
9. Clean up resources

## Running Tests Locally

### Prerequisites

1. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Node.js** (for MCP Inspector)
   ```bash
   node --version  # v18+
   npx --version
   ```

3. **Python 3.10+**
   ```bash
   python --version
   pip install -e .
   ```

### Using the Test Script

The easiest way to run E2E tests:

```bash
./scripts/run-e2e-tests.sh
```

This script:
- ✅ Builds and starts containers
- ✅ Waits for services to be ready
- ✅ Generates Semaphore API token
- ✅ Runs all test suites
- ✅ Shows detailed logs on failure
- ✅ Cleans up containers on exit

### Manual Testing

1. **Start containers:**
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. **Wait for Semaphore:**
   ```bash
   curl http://localhost:3000/api/ping
   ```

3. **Generate API token:**
   ```bash
   # Login
   TOKEN=$(curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"auth": "admin", "password": "changeme"}' \
     | jq -r '.token')

   # Export for MCP server
   export SEMAPHORE_API_TOKEN=$TOKEN
   ```

4. **Restart MCP server with token:**
   ```bash
   docker-compose -f docker-compose.test.yml restart semaphore-mcp
   ```

5. **Run tests:**
   ```bash
   export MCP_SERVER_URL=http://localhost:8000

   # Tool registration smoke test
   python tests/e2e/test_tool_registration.py

   # Per-category workflow tests (using pytest)
   pytest tests/e2e/test_projects_e2e.py -v
   pytest tests/e2e/test_environments_e2e.py -v

   # Or run all e2e tests
   pytest tests/e2e/ -v --ignore=tests/e2e/test_comprehensive_scenario.py
   ```

6. **Cleanup:**
   ```bash
   docker-compose -f docker-compose.test.yml down -v
   ```

## GitHub Actions Integration

The `.github/workflows/test-mcp-integration.yml` workflow runs E2E tests automatically:

- **Triggers:** Push to main/develop, PRs, manual workflow dispatch
- **Runtime:** ~5-10 minutes
- **Steps:**
  1. Setup Python, Node.js, Docker
  2. Build containers with layer caching
  3. Start Semaphore and generate API token
  4. Start MCP server
  5. Run test suites
  6. Show logs on failure
  7. Cleanup

**View results:**
- Check Actions tab: `MCP Integration Tests` workflow
- See detailed logs for each test step
- Container logs available on failure

## Using MCP Inspector Directly

You can also use MCP Inspector CLI directly for ad-hoc testing:

### List all tools:
```bash
npx @modelcontextprotocol/inspector --cli http://localhost:8000 \
  --method tools/list
```

### Call a specific tool:
```bash
# List projects
npx @modelcontextprotocol/inspector --cli http://localhost:8000 \
  --method tools/call \
  --tool-name list_projects

# Create project
npx @modelcontextprotocol/inspector --cli http://localhost:8000 \
  --method tools/call \
  --tool-name create_project \
  --tool-arg 'name="Test Project"' \
  --tool-arg 'alert=true'
```

### List resources:
```bash
npx @modelcontextprotocol/inspector --cli http://localhost:8000 \
  --method resources/list
```

## Extending Tests

### Adding New Per-Category Tests

1. Create a new test file: `tests/e2e/test_<category>_e2e.py`
2. Import fixtures from `conftest.py`
3. Define pytest test classes/functions
4. Add to `run-e2e-tests.sh` and GitHub workflow if needed

Example:
```python
import pytest
from conftest import parse_mcp_response
from mcp_inspector import MCPInspector

class TestMyToolsE2E:
    def test_list_operation(self, inspector: MCPInspector, created_project: dict):
        """Test listing resources."""
        project_id = created_project["id"]

        result = inspector.call_tool("list_my_resources", {"project_id": project_id})
        data = parse_mcp_response(result)

        assert "resources" in data
        assert isinstance(data["resources"], list)

    def test_crud_workflow(self, inspector: MCPInspector, created_project: dict):
        """Test complete CRUD workflow."""
        project_id = created_project["id"]

        # Create
        create_result = inspector.call_tool(
            "create_resource",
            {"project_id": project_id, "name": "Test Resource"}
        )
        resource = parse_mcp_response(create_result)
        resource_id = resource["id"]

        try:
            # Read, Update operations...
            pass
        finally:
            # Cleanup
            inspector.call_tool(
                "delete_resource",
                {"project_id": project_id, "resource_id": resource_id}
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Using Fixtures

The `conftest.py` provides these fixtures:

- `inspector` - MCP Inspector client (session-scoped)
- `mcp_server_url` - Server URL from environment
- `created_project` - Creates a project and cleans up after test
- `created_environment` - Creates an environment (requires project)
- `created_inventory` - Creates an inventory (requires project)
- `parse_mcp_response()` - Helper to extract data from MCP responses

## Troubleshooting

### MCP Inspector not found
```bash
# Install Node.js 18+ and verify npx works
npx @modelcontextprotocol/inspector --version
```

### Container not starting
```bash
# Check logs
docker-compose -f docker-compose.test.yml logs semaphore
docker-compose -f docker-compose.test.yml logs semaphore-mcp

# Check health
docker-compose -f docker-compose.test.yml ps
```

### API token issues
```bash
# Verify Semaphore is accessible
curl http://localhost:3000/api/ping

# Check login credentials
docker-compose -f docker-compose.test.yml logs semaphore | grep -i admin
```

### MCP server connection errors
```bash
# Verify MCP server is listening
curl http://localhost:8000

# Check MCP server has valid token
docker-compose -f docker-compose.test.yml exec semaphore-mcp env | grep SEMAPHORE
```

## Benefits of MCP Inspector Approach

✅ **Official tooling** - Uses Anthropic's standard MCP testing tool
✅ **No custom client** - No need to maintain MCP protocol implementation
✅ **Real client behavior** - Tests actual MCP client interactions
✅ **CLI automation** - Easy to integrate in CI/CD pipelines
✅ **JSON output** - Machine-readable results for validation
✅ **Ecosystem alignment** - Follows MCP best practices

## Future Enhancements

- [ ] Add performance/load testing scenarios
- [ ] Test error handling and edge cases
- [ ] Add tests for LLM-powered features (task analysis)
- [ ] Create reusable test fixtures for common workflows
- [ ] Add API response validation schemas
- [ ] Test concurrent tool calls
- [ ] Add integration with Claude Desktop for manual testing
