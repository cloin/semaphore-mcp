# SemaphoreUI MCP Server
# 🚧 **Under active development!** 🚧
 
A Model Context Protocol (MCP) server that provides AI assistants with powerful automation capabilities for SemaphoreUI - a modern, web-based Ansible management platform.

![rawoutput-demo-gif](images/semaphore-mcp-rawoutput.gif)

## Table of Contents

- [What is this?](#what-is-this)
- [Use Cases](#use-cases)
- [What You Can Do](#what-you-can-do)
- [Installation](#installation)
- [Configuration](#configuration)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Features](#features)
- [Practical Usage Examples](#practical-usage-examples)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Contributing](#contributing)

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

## 📦 Installation

### Prerequisites
- Python 3.10+
- SemaphoreUI instance (local or remote)
- SemaphoreUI API token

### Install from PyPI

```bash
# Install with --user flag (recommended for PATH access)
pip install --user semaphore-mcp

# Or use pipx (handles PATH automatically)
pipx install semaphore-mcp

# Verify installation
semaphore-mcp --help
```

**Note**: If `semaphore-mcp` command is not found after installation, you may need to use the full path. Find it with:
```bash
# If installed with pipx
pipx list | grep semaphore-mcp

# If installed with pip --user
python3 -m site --user-base
```

### Or Install from GitHub

```bash
# Install latest development version
pip install --user git+https://github.com/cloin/semaphore-mcp.git
```

### Optional: Stand up a testing SemaphoreUI instance

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

### Generate API Token

- Login to SemaphoreUI
- Navigate to User Settings
- Generate a new API token

## ⚙️ Configuration

## Claude Desktop Integration

### Step 1: Configure Claude Desktop

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

**Note**: If `semaphore-mcp` is not found, use the full path from the installation step above.

### Step 2: Test and Restart

Restart Claude Desktop, then try:
```
List all projects in SemaphoreUI
```

Or Test your setup:
```bash
SEMAPHORE_URL=http://localhost:3000 SEMAPHORE_API_TOKEN=your-token semaphore-mcp --help
```

## 🛠️ Features

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
4. Set up the API token in your MCP client (like Claude Desktop) (semaphore url hardcoded as http://localhost:3000):

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

### Development with FastMCP

Tools are registered using the FastMCP decorator pattern for simplicity and maintainability:

```python
@mcp.tool()
def list_projects():
    # Implementation
    pass
```

This approach allows for easy extension with new tools as needed. Check the `server.py` file for implementation details.

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

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting manually
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Or run all linters at once with pre-commit
pre-commit run --all-files
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- **SemaphoreUI Documentation**: https://docs.semaphoreui.com/
- **SemaphoreUI API Reference**: https://semaphoreui.com/api-docs/
- **Model Context Protocol**: https://modelcontextprotocol.io/introduction
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp

---

**⭐ If this project helps you, please give it a star on GitHub!**
