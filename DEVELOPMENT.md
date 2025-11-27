# Development Guide

This guide covers local development setup, testing, and contributing to the project.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A SemaphoreUI instance for testing

## Local Setup

```bash
# Clone the repository
git clone https://github.com/cloin/semaphore-mcp.git
cd semaphore-mcp

# Create virtual environment and install dependencies
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Locally

The server supports two transport modes:

### STDIO Mode (Default)

Used for direct integration with MCP clients like Claude Desktop:

```bash
semaphore-mcp --url http://localhost:3000 --token your-token
```

### HTTP Mode

Used for network-accessible deployments:

```bash
semaphore-mcp --transport http --host 0.0.0.0 --port 8000 \
  --url http://localhost:3000 --token your-token
```

### Environment Variables

You can also configure via environment variables:

```bash
export SEMAPHORE_URL=http://localhost:3000
export SEMAPHORE_API_TOKEN=your-token
export MCP_LOG_LEVEL=DEBUG  # For verbose logging

semaphore-mcp
```

## Claude Desktop Configuration (Local Development)

For local development with STDIO mode, configure Claude Desktop to use your virtual environment directly:

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/claude-desktop/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "/path/to/semaphore-mcp/.venv/bin/semaphore-mcp",
      "args": [],
      "env": {
        "SEMAPHORE_URL": "http://localhost:3000",
        "SEMAPHORE_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Setting Up a Test SemaphoreUI Instance

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

Then:
1. Access http://localhost:3000
2. Login with `admin` / `admin123`
3. Go to User Settings and create an API token

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api_client.py

# Run with coverage
pytest --cov=semaphore_mcp
```

### Test Coverage

The project includes tests for:
- Project operations (CRUD)
- Template operations (list, get)
- Task operations (CRUD, monitoring, bulk operations, failure analysis)
- Environment operations (CRUD)
- Inventory operations (CRUD)
- Error handling scenarios

## Code Quality

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Fix linting issues automatically
ruff check --fix src/ tests/

# Run all checks via pre-commit
pre-commit run --all-files
```

## Building Docker Image Locally

```bash
docker build -t semaphore-mcp:local .

# Test the local image
docker run --rm -e SEMAPHORE_URL=http://host.docker.internal:3000 \
  -e SEMAPHORE_API_TOKEN=your-token \
  -p 8000:8000 \
  semaphore-mcp:local
```

## Project Structure

```
semaphore-mcp/
├── src/semaphore_mcp/
│   ├── __init__.py
│   ├── api.py              # SemaphoreUI API client
│   ├── config.py           # Configuration management
│   ├── server.py           # FastMCP server implementation
│   ├── scripts/
│   │   └── start_server.py # CLI entry point
│   └── tools/              # MCP tool implementations
│       ├── base.py
│       ├── projects.py
│       ├── templates.py
│       ├── tasks.py
│       ├── environments.py
│       └── repositories.py
├── tests/
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest`)
5. Run linting (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## GitHub Actions CI/CD

If contributing, ensure the repository has these secrets configured for CI:

- `ADMIN_USERNAME`: SemaphoreUI admin username (e.g., "admin")
- `ADMIN_PASSWORD`: SemaphoreUI admin password (e.g., "admin123")

These are used for integration tests in CI. Local development can use environment variables or `.env` files.

## Troubleshooting

### Connection refused to SemaphoreUI
- Ensure SemaphoreUI is running on the configured URL
- Check firewall settings if using remote SemaphoreUI
- Verify the URL format (include `http://` or `https://`)

### Authentication errors
- Regenerate your API token in SemaphoreUI User Settings
- Ensure the token is correctly set in your environment
- Check that the user account has appropriate permissions

### Claude Desktop not connecting
- Verify the absolute path in your config is correct
- Test the command manually in terminal first
- Check Claude Desktop logs for specific error messages
- Ensure virtual environment has all required dependencies

### Debug Mode

Enable detailed logging:
```bash
export MCP_LOG_LEVEL=DEBUG
semaphore-mcp
```
