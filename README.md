# semaphore-mcp
MCP (Model Context Protocol) Server for SemaphoreUI

This project implements a MCP server for SemaphoreUI, a self-hosted Ansible UI. It encapsulates the SemaphoreUI API and provides a simple interface for AI applications and other services to interact with SemaphoreUI using the Model Context Protocol standard. The server enables automation of common SemaphoreUI tasks like managing projects, templates, tasks, environments, and inventory.

## Project Status

### Completed
- [x] Basic project structure setup
- [x] SemaphoreUI API client implementation
- [x] MCP server implementation with stdio transport
- [x] Initial tool definitions for projects, templates, and tasks
- [x] Basic tests for API client and MCP server
- [x] GitHub Actions workflow for testing with Podman
- [x] Environment variables configuration
- [x] Improved error handling in server response formatting

### Working Features
- ✅ Project operations (list, get, create, update, delete)
- ✅ Template operations (list, get)
- ✅ Task operations (list, get)
- ✅ MCP server tools for project management
- ✅ JSON response formatting with content blocks

### In Progress / Partially Working
- [ ] Environment management API integration (partially implemented)
- [ ] Inventory management API integration (partially implemented)

### To Do
- [ ] Fix environment and inventory API payloads for SemaphoreUI compatibility
- [ ] Comprehensive documentation for using the MCP server
- [ ] Server-Sent Events (SSE) transport implementation
- [ ] Authentication handling improvements
- [ ] Integration examples
- [ ] Key operations and run task operations

## Testing

### Setting up a Test Environment

Spin up a local SemaphoreUI instance using Docker or Podman:

```bash
podman run -d \
  --name semaphore-dev \
  -p 3000:3000 \
  -e SEMAPHORE_DB_DIALECT=bolt \
  -e SEMAPHORE_ADMIN_PASSWORD=admin123 \
  -e SEMAPHORE_ADMIN_NAME=admin \
  -e SEMAPHORE_ADMIN_EMAIL=admin@localhost \
  -e SEMAPHORE_ADMIN=admin \
  -v semaphore-data:/etc/semaphore:Z \
  semaphoreui/semaphore:latest
```

After starting SemaphoreUI:

1. Access the web UI at http://localhost:3000
2. Login with username `admin` and password `admin123`
3. Navigate to User Settings and create an API token
4. Set up the API token in your `.env` file

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_api_client.py
```

### Known Test Issues

Some tests for environment and inventory management are currently skipped due to API compatibility issues. These will be addressed in future updates.

## Installation and Usage

### Prerequisites
- Python 3.8+
- SemaphoreUI instance (see Testing section for local setup)
- SemaphoreUI API token

### Installation

#### Option 1: Using uv (Recommended by MCP)

```bash
# Clone the repository
git clone https://github.com/yourusername/semaphore-mcp.git
cd semaphore-mcp

# Install uv if you don't have it already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install the package
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .
```

#### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/semaphore-mcp.git
cd semaphore-mcp

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

### Configuration

Create a `.env` file in the project root or set environment variables:

```bash
SEMAPHORE_URL=http://localhost:3000
SEMAPHORE_API_TOKEN=your-token-here
MCP_LOG_LEVEL=INFO  # Optional, defaults to INFO
```

### Running the Server

```bash
# Run the MCP server
python scripts/start_server.py
```

### Claude Desktop Client Integration

To use this MCP with the Claude Desktop Client:

1. First run the setup script to create a dedicated virtual environment with all dependencies:

```bash
./scripts/setup_for_claude.sh
```

2. Then update your `claude_desktop_config.json` file (typically located at `~/.config/claude-desktop/claude_desktop_config.json`) with the following configuration:

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "bash",
      "args": [
        "-c",
        "cd /Users/colin/Projects/homelab/semaphore-mcp && /Users/colin/.local/bin/uv pip install -e . mcp && /Users/colin/.local/bin/uv run scripts/start_server.py"
      ]
    }
  }
}
```

Make sure to:
1. Replace the paths with the absolute paths to your semaphore-mcp directory and uv installation
2. Ensure your `.env` file with SEMAPHORE_API_TOKEN is properly configured in the semaphore-mcp directory

#### Verifying Claude Desktop Setup

To verify that your setup works correctly before using it with Claude Desktop:

```bash
# Test the command exactly as Claude Desktop would run it
bash -c "cd /Users/colin/Projects/homelab/semaphore-mcp && /Users/colin/.local/bin/uv pip install -e . mcp && /Users/colin/.local/bin/uv run scripts/start_server.py"
```

If configured correctly, the server should start without errors. You can then press Ctrl+C to stop it. After verifying, restart Claude Desktop to apply the configuration changes.

### Available MCP Tools

The MCP server provides the following tools for interacting with SemaphoreUI:

- `list_projects` - List all projects
- `get_project` - Get a specific project by ID
- `create_project` - Create a new project
- `update_project` - Update an existing project
- `delete_project` - Delete a project
- `list_templates` - List templates for a project
- `get_template` - Get a specific template
- `list_tasks` - List tasks for a template
- `get_task` - Get a specific task

## API Documentation

https://docs.semaphoreui.com/administration-guide/api/

## API Reference

https://semaphoreui.com/api-docs/

## MCP Reference

https://modelcontextprotocol.io/introduction