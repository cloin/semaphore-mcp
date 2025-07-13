# SemaphoreUI MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with powerful automation capabilities for SemaphoreUI - a modern, web-based Ansible management platform.

## 🎯 What is this?

This MCP server bridges AI assistants (like Claude) with SemaphoreUI, enabling you to:

- **Automate Ansible playbook execution** through natural language
- **Monitor and analyze task failures** with AI-powered insights
- **Manage infrastructure projects** with conversational commands
- **Streamline DevOps workflows** by combining AI reasoning with automation

Perfect for DevOps teams who want to leverage AI for infrastructure management while maintaining the power and flexibility of Ansible.

## 🎯 Use Cases

### For DevOps Engineers
- **Incident Response**: "Find all failed deployments in the last 6 hours and analyze the errors"
- **Routine Operations**: "Deploy the latest version to staging and run the smoke tests"
- **Infrastructure Scaling**: "Add the new servers to our production inventory and update the load balancer config"

### For Platform Teams  
- **Self-Service**: Enable developers to deploy to staging environments through conversational AI
- **Monitoring**: Get intelligent summaries of deployment status and failure patterns
- **Compliance**: Ensure deployment procedures are followed consistently

### For Site Reliability Engineers
- **Automation**: Convert manual runbooks into conversational workflows
- **Troubleshooting**: AI-powered analysis of failure logs and suggested remediation
- **Capacity Planning**: Monitor deployment patterns and resource usage trends

## ⚡ Quick Start

1. **Spin up SemaphoreUI locally:**
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

2. **Install and configure:** (Requires Python 3.10+)
```bash
# Install the package
pip install semaphore-mcp

# Generate API token automatically  
curl -O https://raw.githubusercontent.com/cloin/semaphore-mcp/main/scripts/generate-token.sh
chmod +x generate-token.sh
./generate-token.sh admin admin123
```

3. **Test the server:**
```bash
semaphore-mcp --help
```

4. **Connect to Claude Desktop** (see [Claude Integration](#claude-desktop-integration) below)

## 🚀 What You Can Do

Once connected to an AI assistant, you can perform complex automation tasks through natural conversation:

### Ansible Automation
- "Run the database backup playbook on production servers"
- "Execute the server update template and monitor progress"
- "Show me all failed deployments from the last week"

### Infrastructure Management  
- "Create a new environment for staging with these variables"
- "List all running tasks and stop any that are failing"
- "Analyze the last deployment failure and suggest fixes"

### Project Operations
- "Set up a new project for the web application deployment"
- "Show me all templates in the infrastructure project"
- "Update the production inventory with new server IPs"

The AI can reason about your infrastructure, suggest solutions, and execute actions all in one conversation.

## 🛠️ Features

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
- [x] Project operations (list, get, create, update, delete)
- [x] Template operations (list, get)
- [x] Task operations (list, get, filter by status, execute with monitoring)
- [x] Task control operations (stop, bulk stop with confirmation, restart)
- [x] Task status polling and streaming updates
- [x] Environment management (list, get, create, update, delete)
- [x] Inventory management (list, get, create, update, delete)
- [x] LLM-based task failure analysis tools
- [x] MCP server tools for project management
- [x] JSON response formatting with content blocks

### To Do
- [ ] Server-Sent Events (SSE) transport implementation (not sure if there's client support)
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

### Test Coverage

The project includes comprehensive tests for all major functionality:
- Project operations (CRUD)
- Template operations (list, get)
- Task operations (CRUD, monitoring, bulk operations, failure analysis)
- Environment operations (CRUD)
- Inventory operations (CRUD)
- Error handling scenarios

## 📦 Installation

### Prerequisites
- Python 3.10+
- SemaphoreUI instance (local or remote)
- SemaphoreUI API token

## 🚀 For Users

### Install from PyPI (Recommended)

```bash
# Install the package
pip install semaphore-mcp

# Or with uv (faster)
uv pip install semaphore-mcp

# Verify installation
semaphore-mcp --help
```

### Install from GitHub

```bash
# Install latest development version
pip install git+https://github.com/cloin/semaphore-mcp.git

# Or specific version
pip install git+https://github.com/cloin/semaphore-mcp.git@v0.1.0
```

## 🛠️ For Developers

### Development Setup

```bash
# Clone the repository
git clone https://github.com/cloin/semaphore-mcp.git
cd semaphore-mcp

# Option 1: Using uv (recommended)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Option 2: Using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Option 3: Using poetry
poetry install && poetry shell
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/semaphore_mcp --cov-report=term-missing
```

## ⚙️ Configuration

### Environment Variables

Set these in your environment or create a `.env` file:

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

## Claude Desktop Integration

### Step 1: Install and Configure

First, install semaphore-mcp:

```bash
# Install from PyPI
pip install semaphore-mcp

# Create a directory for configuration
mkdir ~/.semaphore-mcp
cd ~/.semaphore-mcp

# Create .env file with your configuration
echo "SEMAPHORE_URL=http://localhost:3000" > .env
echo "SEMAPHORE_API_TOKEN=your-token-here" >> .env
```

If you need to generate a token and have SemaphoreUI running locally:

```bash
# Download the token generation script
curl -O https://raw.githubusercontent.com/cloin/semaphore-mcp/main/scripts/generate-token.sh
chmod +x generate-token.sh

# Generate token automatically
./generate-token.sh admin admin123 >> .env
```

### Step 2: Update Claude Desktop Configuration

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "semaphore-mcp",
      "args": [],
      "env": {
        "SEMAPHORE_URL": "http://localhost:3000", 
        "SEMAPHORE_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Alternative**: If you prefer using a config directory:

```json
{
  "mcpServers": {
    "semaphore": {
      "command": "bash",
      "args": [
        "-c", 
        "cd ~/.semaphore-mcp && semaphore-mcp"
      ]
    }
  }
}
```

### Step 3: Test the Configuration

Verify your setup works before connecting to Claude:

```bash
# Test the command directly
SEMAPHORE_URL=http://localhost:3000 SEMAPHORE_API_TOKEN=your-token semaphore-mcp --verbose
```

You should see output like:
```
INFO:semaphore_mcp:Starting SemaphoreMCP server...
INFO:semaphore_mcp:Connected to SemaphoreUI at http://localhost:3000
```

Press `Ctrl+C` to stop the test.

### Step 4: Restart Claude Desktop

After updating the configuration file, restart Claude Desktop to apply the changes.

### Step 5: Verify Connection

In Claude Desktop, start a new conversation and try:
```
List all projects in SemaphoreUI
```

If successful, Claude will use the MCP server to fetch and display your projects.

### Available MCP Tools

The FastMCP server registers the following tools for interacting with SemaphoreUI:

**Project Management:**
- `list_projects` - List all projects
- `get_project` - Get a specific project by ID
- `create_project` - Create a new project
- `update_project` - Update an existing project
- `delete_project` - Delete a project

**Template Operations:**
- `list_templates` - List templates for a project
- `get_template` - Get a specific template

**Task Management:**
- `list_tasks` - List tasks for a project
- `get_task` - Get a specific task
- `run_task` - Execute a task from a template
- `get_task_output` - Get structured task output
- `get_task_raw_output` - Get raw task output for analysis
- `stop_task` - Stop a running task
- `bulk_stop_tasks` - Stop multiple tasks with confirmation
- `filter_tasks` - Filter tasks by status and other criteria
- `run_task_with_monitoring` - Execute task with real-time monitoring

**LLM-Based Failure Analysis:**
- `analyze_task_failure` - Comprehensive analysis of failed tasks
- `bulk_analyze_failures` - Pattern detection across multiple failures
- `get_latest_failed_task` - Get most recent failed task

**Environment Management:**
- `list_environments` - List environments for a project
- `get_environment` - Get a specific environment
- `create_environment` - Create a new environment with variables
- `update_environment` - Update environment name and variables
- `delete_environment` - Delete an environment

**Inventory Management:**
- `list_inventory` - List inventory items for a project
- `get_inventory` - Get a specific inventory item
- `create_inventory` - Create a new inventory with content
- `update_inventory` - Update inventory name and content
- `delete_inventory` - Delete an inventory item

### Development with FastMCP

Tools are registered using the FastMCP decorator pattern for simplicity and maintainability:

```python
@mcp.tool()
def list_projects():
    # Implementation
    pass
```

This approach allows for easy extension with new tools as needed. Check the `server.py` file for implementation details.

## 📖 Practical Usage Examples

### Example 1: Setting Up a New Project

**You say to Claude:**
> "I need to set up a new project for deploying our web application. Create a project called 'webapp-deploy' and add a staging environment with these variables: APP_ENV=staging, DB_HOST=staging-db.example.com"

**Claude will:**
1. Create the project using `create_project`
2. Create a staging environment using `create_environment`
3. Confirm the setup and provide you with project details

### Example 2: Monitoring and Troubleshooting

**You say to Claude:**
> "Check if there are any failed tasks in the last hour and analyze what went wrong"

**Claude will:**
1. Use `filter_tasks` to find recent failed tasks
2. Use `analyze_task_failure` to examine error logs
3. Provide detailed analysis and suggested fixes
4. Optionally restart tasks if appropriate

### Example 3: Automated Deployment Workflow

**You say to Claude:**
> "Run the 'deploy-app' template on production, monitor the progress, and let me know when it's done"

**Claude will:**
1. Execute the template using `run_task_with_monitoring`
2. Stream real-time progress updates
3. Notify you of completion status
4. If it fails, automatically analyze the failure

### Example 4: Infrastructure Inventory Management

**You say to Claude:**
> "Update our production inventory to add these new servers: web-03.prod.example.com, web-04.prod.example.com"

**Claude will:**
1. Retrieve current inventory using `get_inventory`
2. Parse and update the inventory content
3. Use `update_inventory` to save changes
4. Confirm the servers were added successfully

### Example 5: Bulk Operations

**You say to Claude:**
> "I see there are several stuck tasks running for more than 2 hours. Please stop them all safely"

**Claude will:**
1. Use `filter_tasks` to find long-running tasks
2. Use `bulk_stop_tasks` with confirmation prompts
3. Provide summary of stopped tasks
4. Suggest investigating why tasks got stuck

## 🔧 Troubleshooting

### Common Issues

**Connection refused to SemaphoreUI**
- Ensure SemaphoreUI is running on the configured URL
- Check firewall settings if using remote SemaphoreUI
- Verify the URL format (include http:// or https://)

**Authentication errors**
- Regenerate your API token using `./scripts/generate-token.sh`
- Ensure the token is correctly set in your `.env` file
- Check that the user account has appropriate permissions

**Claude Desktop not connecting**
- Verify the absolute path in your config is correct
- Test the command manually in terminal first
- Check Claude Desktop logs for specific error messages
- Ensure virtual environment has all required dependencies

**Tasks failing to execute**
- Verify your templates are properly configured in SemaphoreUI
- Check that inventory and environment variables are set correctly
- Ensure your Ansible playbooks are accessible to SemaphoreUI

### Debug Mode

Enable detailed logging by setting:
```bash
export MCP_LOG_LEVEL=DEBUG
```

This will provide verbose output about MCP communications and API calls.

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/cloin/semaphore-mcp.git
cd semaphore-mcp

# Install in development mode
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
isort src/ tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- **SemaphoreUI Documentation**: https://docs.semaphoreui.com/
- **SemaphoreUI API Reference**: https://semaphoreui.com/api-docs/
- **Model Context Protocol**: https://modelcontextprotocol.io/introduction
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp

## 📞 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/cloin/semaphore-mcp/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/cloin/semaphore-mcp/discussions)
- **SemaphoreUI Community**: Get help with SemaphoreUI at their [community forums](https://github.com/ansible-semaphore/semaphore)

---

**⭐ If this project helps you, please give it a star on GitHub!**
