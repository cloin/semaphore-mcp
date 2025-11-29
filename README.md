# SemaphoreUI MCP Server

A Model Context Protocol (MCP) server that connects AI assistants to [SemaphoreUI](https://semaphoreui.com/) - enabling natural language control of Ansible automation.

![demo](images/semaphore-mcp-rawoutput.gif)

## Quick Start

### Prerequisites

- Docker (or Podman)
- A running SemaphoreUI instance with an API token
- Claude Desktop or Claude Code (or another MCP client)
- Node.js (for Claude Desktop only - required for `mcp-remote`)

### 1. Get a SemaphoreUI API Token

1. Login to your SemaphoreUI instance
2. Go to User Settings
3. Generate a new API token

### 2. Run the MCP Server

```bash
docker run -d --name semaphore-mcp \
  --network host \
  -e SEMAPHORE_URL=http://localhost:3000 \
  -e SEMAPHORE_API_TOKEN=your-token-here \
  -e MCP_PORT=8500 \
  ghcr.io/cloin/semaphore-mcp:latest
```

> **Note:** `SEMAPHORE_URL` is where the MCP server connects to SemaphoreUI. `MCP_PORT` is where the MCP server listens for client connections (Claude Desktop/Code). Use this port in your client configuration below.

### 3a. Configure Claude Desktop

Claude Desktop requires the `mcp-remote` proxy to connect to HTTP-based MCP servers. This requires Node.js to be installed (`npx` comes with npm).

Edit your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:8500/mcp"]
    }
  }
}
```

### 3b. Configure Claude Code

Claude Code supports remote MCP servers directly:

```bash
claude mcp add --transport http semaphore http://127.0.0.1:8500/mcp
```

Verify it's configured:

```bash
claude mcp list
```

### 4. Test It

Restart Claude Desktop and try:

> "List all projects in SemaphoreUI"

## Docker Networking

The MCP server container needs to reach your SemaphoreUI instance.

**SemaphoreUI on the same host:**

Use `--network host` so the container can access localhost:

```bash
docker run -d --name semaphore-mcp \
  --network host \
  -e SEMAPHORE_URL=http://localhost:3000 \
  -e SEMAPHORE_API_TOKEN=your-token \
  -e MCP_PORT=8500 \
  ghcr.io/cloin/semaphore-mcp:latest
```

**SemaphoreUI on a different host:**

Use the IP or hostname directly (no `--network host` needed):

```bash
docker run -d --name semaphore-mcp \
  -e SEMAPHORE_URL=http://192.168.1.100:3000 \
  -e SEMAPHORE_API_TOKEN=your-token \
  -p 8500:8000 \
  ghcr.io/cloin/semaphore-mcp:latest
```

For more details, see [Docker's networking documentation](https://docs.docker.com/network/).

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SEMAPHORE_URL` | Yes | - | URL to your SemaphoreUI instance |
| `SEMAPHORE_API_TOKEN` | Yes | - | API token from SemaphoreUI |
| `MCP_TRANSPORT` | No | `http` | Transport mode: `http` or `stdio` |
| `MCP_HOST` | No | `0.0.0.0` | Host to bind to |
| `MCP_PORT` | No | `8000` | Port to listen on |

## What You Can Do

Once connected, you can interact with SemaphoreUI through natural conversation:

**Run automation:**
> "Run the database backup playbook on production"

**Monitor tasks:**
> "Show me all failed tasks from the last hour and analyze the errors"

**Manage infrastructure:**
> "Create a new staging environment with APP_ENV=staging"

**Troubleshoot:**
> "Get the output from task 42 and tell me why it failed"

## Available Tools

**Projects:** `list_projects`, `get_project`, `create_project`, `update_project`, `delete_project`

**Templates:** `list_templates`, `get_template`, `create_template`, `update_template`, `delete_template`

**Tasks:** `list_tasks`, `get_task`, `run_task`, `stop_task`, `get_task_raw_output`, `filter_tasks`, `bulk_stop_tasks`

**Analysis:** `analyze_task_failure`, `bulk_analyze_failures`, `get_latest_failed_task`

**Environments:** `list_environments`, `get_environment`, `create_environment`, `update_environment`, `delete_environment`

**Inventory:** `list_inventory`, `get_inventory`, `create_inventory`, `update_inventory`, `delete_inventory`

**Repositories:** `list_repositories`, `get_repository`, `create_repository`, `update_repository`, `delete_repository`

## Troubleshooting

**Container won't start or exits immediately:**
```bash
docker logs semaphore-mcp
```

**Can't connect to SemaphoreUI from container:**
- If SemaphoreUI is on localhost, use `--network host`
- Check that the URL is reachable from inside the container
- Verify the API token is correct

**Claude Desktop not seeing the MCP server:**
- Ensure the container is running: `docker ps`
- Check the port is accessible: `curl http://127.0.0.1:8500/mcp`
- Restart Claude Desktop after config changes

**Enable debug logging:**
```bash
docker run -d --name semaphore-mcp \
  --network host \
  -e SEMAPHORE_URL=http://localhost:3000 \
  -e SEMAPHORE_API_TOKEN=your-token \
  -e MCP_PORT=8500 \
  -e MCP_LOG_LEVEL=DEBUG \
  ghcr.io/cloin/semaphore-mcp:latest
```

## Development

For local development and contributing, see [DEVELOPMENT.md](DEVELOPMENT.md).

For testing documentation (unit tests, E2E tests, CI/CD), see [TESTING.md](TESTING.md).

## Resources

- [SemaphoreUI Documentation](https://docs.semaphoreui.com/)
- [SemaphoreUI API Reference](https://semaphoreui.com/api-docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitHub Issues](https://github.com/cloin/semaphore-mcp/issues)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Note:** Versions prior to 1.0.0 were released under the MIT License.
