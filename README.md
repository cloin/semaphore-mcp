# semaphore-mcp
MCP (Model Context Protocol) Server for SemaphoreUI

This project implements a MCP server for SemaphoreUI, a self-hosted Ansible UI. It encapsulates the SemaphoreUI API and provides a simple interface for AI applications and other services to interact with SemaphoreUI using the Model Context Protocol standard. The server enables automation of common SemaphoreUI tasks like managing projects, templates, tasks, environments, and inventory.

The server uses FastMCP for efficient protocol handling and simple tool registration.

## Project Status

### Completed
- [x] Basic project structure setup
- [x] SemaphoreUI API client implementation
- [x] MCP server implementation with FastMCP and stdio transport
- [x] Initial tool definitions for projects, templates, and tasks
- [x] Basic tests for API client and MCP server
- [x] GitHub Actions workflow for testing with Docker
- [x] Secure token handling for tests and CI
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
- [ ] Enhance CI workflow with deeper test coverage
- [ ] Comprehensive documentation for using the MCP server
- [ ] Server-Sent Events (SSE) transport implementation
- [ ] Authentication handling improvements
- [ ] Integration examples with Claude and other AI models
- [ ] Key operations and run task operations
- [ ] Performance optimization for large Semaphore installations
- [ ] Implement better error handling and recovery mechanisms

## Testing

### Setting up a Test Environment

Spin up a local SemaphoreUI instance using Docker:

```bash
docker run -d \
  --name semaphore-dev \
  -p 3000:3000 \
  -e SEMAPHORE_DB_DIALECT=bolt \
  -e SEMAPHORE_ADMIN_PASSWORD=admin123 \
  -e SEMAPHORE_ADMIN_NAME=admin \
  -e SEMAPHORE_ADMIN_EMAIL=admin@localhost \
  -e SEMAPHORE_ADMIN=admin \
  -v semaphore-data:/etc/semaphore \
  semaphoreui/semaphore:latest
```

After starting SemaphoreUI:

1. Access the web UI at http://localhost:3000
2. Login with username `admin` and password `admin123`
3. Navigate to User Settings and create an API token
4. Set up the API token in your `.env` file or generate one using the provided script (semaphore url hardcoded as http://localhost:3000):
   ```bash
   # Generate a token with default admin credentials
   ./scripts/generate-token.sh admin admin123
   ```

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
- mcp >= 1.9.3 package (for FastMCP support)

### Installation

#### Using uv

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

### Configuration

Create a `.env` file in the project root or set environment variables:

```bash
SEMAPHORE_URL=http://localhost:3000
SEMAPHORE_API_TOKEN=your-token-here
MCP_LOG_LEVEL=INFO  # Optional, defaults to INFO
```

To generate a token automatically:

```bash
./scripts/generate-token.sh admin admin123
```

### Running the Server

```bash
# Run the MCP server
python scripts/start_server.py
```

### Claude Desktop Client Integration

To use this MCP with the Claude Desktop Client:

1. Setup a virtual environment with all dependencies using your preferred package manager.

2. Then update your `claude_desktop_config.json` file (typically located at `~/.config/claude-desktop/claude_desktop_config.json`) with the following configuration:

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/semaphore-mcp && python -m scripts.start_server"
      ]
    }
  }
}
```

Make sure to:
1. Replace `/path/to/semaphore-mcp` with the absolute path to your semaphore-mcp directory
2. Ensure your `.env` file with SEMAPHORE_API_TOKEN is properly configured in the semaphore-mcp directory
3. The environment where bash is running should have all the required dependencies installed (`pip install -e . mcp>=1.9.3`)

#### Verifying Claude Desktop Setup

To verify that your setup works correctly before using it with Claude Desktop:

```bash
# Test the command exactly as Claude Desktop would run it
bash -c "cd /path/to/semaphore-mcp && python -m scripts.start_server"
```

If configured correctly, the server should start without errors. You can then press Ctrl+C to stop it. After verifying, restart Claude Desktop to apply the configuration changes.

### Available MCP Tools

The FastMCP server registers the following tools for interacting with SemaphoreUI:

- `list_projects` - List all projects
- `get_project` - Get a specific project by ID
- `create_project` - Create a new project
- `update_project` - Update an existing project
- `delete_project` - Delete a project
- `list_templates` - List templates for a project
- `get_template` - Get a specific template
- `list_tasks` - List tasks for a template
- `get_task` - Get a specific task

### Development with FastMCP

Tools are registered using the FastMCP decorator pattern for simplicity and maintainability:

```python
@mcp.tool()
def list_projects():
    # Implementation
    pass
```

This approach allows for easy extension with new tools as needed. Check the `server.py` file for implementation details.

## API Documentation

https://docs.semaphoreui.com/administration-guide/api/

## API Reference

https://semaphoreui.com/api-docs/

## MCP Reference

https://modelcontextprotocol.io/introduction