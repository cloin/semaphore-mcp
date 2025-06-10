"""
MCP Server implementation for SemaphoreUI.

This module implements a Model Context Protocol server that exposes 
SemaphoreUI API functionality through MCP tools.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from .api import SemaphoreAPIClient, create_client
from .config import configure_logging, get_config

# Configure logging
configure_logging()
logger = logging.getLogger("semaphore_mcp")

# MCP message types
REQUEST = "request"
RESPONSE = "response"
NOTIFICATION = "notification"


def validate_required_args(args: Dict[str, Any], required_args: List[str]) -> None:
    """Validate that all required args are present."""
    for arg in required_args:
        if arg not in args:
            raise KeyError(f"Missing required argument: {arg}")


def format_json_response(data: Any) -> Dict[str, Any]:
    """Format a JSON response."""
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(data, indent=2)
        }]
    }


def format_error(message: str) -> Dict[str, Any]:
    """Format an error response."""
    return {
        "content": [{
            "type": "error",
            "text": message
        }]
    }


class MCPServer:
    """Model Context Protocol server for SemaphoreUI."""
    
    def __init__(
        self,
        semaphore_url: Optional[str] = None,
        semaphore_token: Optional[str] = None
    ):
        """
        Initialize the MCP server.
        
        Args:
            semaphore_url: SemaphoreUI API URL
            semaphore_token: SemaphoreUI API token
        """
        self.semaphore = create_client(semaphore_url, semaphore_token)
        self.tools = self.register_tools()
        
    def register_tools(self):
        """Register all available tools."""
        self.tools = {
            # Project tools
            "list_projects": self.tool_list_projects,
            "get_project": self.tool_get_project,
            
            # Template tools
            "list_templates": self.tool_list_templates,
            "get_template": self.tool_get_template,
            
            # Task tools
            "list_tasks": self.tool_list_tasks,
            "get_task": self.tool_get_task,
            "run_task": self.tool_run_task,
            "get_task_output": self.tool_get_task_output,
            
            # Environment tools
            "list_environments": self.tool_list_environments,
            "get_environment": self.tool_get_environment,
            "create_environment": self.tool_create_environment,
            "update_environment": self.tool_update_environment,
            "delete_environment": self.tool_delete_environment,
            
            # Inventory tools
            "list_inventory": self.tool_list_inventory,
            "get_inventory": self.tool_get_inventory,
            "create_inventory": self.tool_create_inventory,
            "update_inventory": self.tool_update_inventory,
            "delete_inventory": self.tool_delete_inventory
        }
        return self.tools
    
    async def tool_list_projects(self, arguments):
        """List projects tool implementation."""
        try:
            response = self.semaphore.list_projects()
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_project(self, arguments):
        """Get project tool implementation."""
        validate_required_args(arguments, ["project_id"])
        
        project_id = arguments["project_id"]
        
        try:
            response = self.semaphore.get_project(project_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_list_templates(self, arguments):
        """List templates tool implementation."""
        validate_required_args(arguments, ["project_id"])
        
        project_id = arguments["project_id"]
        
        try:
            response = self.semaphore.list_templates(project_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_template(self, arguments):
        """Get template tool implementation."""
        validate_required_args(arguments, ["project_id", "template_id"])
        
        project_id = arguments["project_id"]
        template_id = arguments["template_id"]
        
        try:
            response = self.semaphore.get_template(project_id, template_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_list_tasks(self, arguments):
        """List tasks tool implementation."""
        validate_required_args(arguments, ["project_id"])
        
        project_id = arguments["project_id"]
        
        try:
            response = self.semaphore.list_tasks(project_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_task(self, arguments):
        """Get task tool implementation."""
        validate_required_args(arguments, ["project_id", "task_id"])
        
        project_id = arguments["project_id"]
        task_id = arguments["task_id"]
        
        try:
            response = self.semaphore.get_task(project_id, task_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_run_task(self, arguments):
        """Run task tool implementation."""
        validate_required_args(arguments, ["project_id", "template_id"])
        
        project_id = arguments["project_id"]
        template_id = arguments["template_id"]
        env_data = arguments.get("env_data", {})
        
        try:
            response = self.semaphore.run_task(project_id, template_id, env_data)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_task_output(self, arguments):
        """Get task output tool implementation."""
        validate_required_args(arguments, ["project_id", "task_id"])
        
        project_id = arguments["project_id"]
        task_id = arguments["task_id"]
        
        try:
            response = self.semaphore.get_task_output(project_id, task_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_list_environments(self, arguments):
        """List environments tool implementation."""
        validate_required_args(arguments, ["project_id"])
        
        project_id = arguments["project_id"]
        
        try:
            environments = self.semaphore.list_environments(project_id)
            return format_json_response(environments)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_environment(self, arguments):
        """Get environment tool implementation."""
        validate_required_args(arguments, ["project_id", "environment_id"])
        
        project_id = arguments["project_id"]
        environment_id = arguments["environment_id"]
        
        try:
            environment = self.semaphore.get_environment(project_id, environment_id)
            return format_json_response(environment)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_create_environment(self, arguments):
        """Create environment tool implementation."""
        validate_required_args(arguments, ["project_id", "name"])
        
        project_id = arguments["project_id"]
        name = arguments["name"]
        env_data = arguments.get("env_data", {})
        
        try:
            response = self.semaphore.create_environment(project_id, name, env_data)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_update_environment(self, arguments):
        """Update environment tool implementation."""
        validate_required_args(arguments, ["project_id", "environment_id"])
        
        project_id = arguments["project_id"]
        environment_id = arguments["environment_id"]
        name = arguments.get("name")
        env_data = arguments.get("env_data")
        
        try:
            response = self.semaphore.update_environment(
                project_id, environment_id, name, env_data
            )
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_delete_environment(self, arguments):
        """Delete environment tool implementation."""
        validate_required_args(arguments, ["project_id", "environment_id"])
        
        project_id = arguments["project_id"]
        environment_id = arguments["environment_id"]
        
        try:
            response = self.semaphore.delete_environment(project_id, environment_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    # Inventory tools implementations
            
    async def tool_list_inventory(self, arguments):
        """List inventory tool implementation."""
        validate_required_args(arguments, ["project_id"])
        
        project_id = arguments["project_id"]
        
        try:
            inventory_items = self.semaphore.list_inventory(project_id)
            return format_json_response(inventory_items)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_get_inventory(self, arguments):
        """Get inventory tool implementation."""
        validate_required_args(arguments, ["project_id", "inventory_id"])
        
        project_id = arguments["project_id"]
        inventory_id = arguments["inventory_id"]
        
        try:
            inventory = self.semaphore.get_inventory(project_id, inventory_id)
            return format_json_response(inventory)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_create_inventory(self, arguments):
        """Create inventory tool implementation."""
        validate_required_args(arguments, ["project_id", "name", "inventory_data"])
        
        project_id = arguments["project_id"]
        name = arguments["name"]
        inventory_data = arguments["inventory_data"]
        
        try:
            response = self.semaphore.create_inventory(project_id, name, inventory_data)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_update_inventory(self, arguments):
        """Update inventory tool implementation."""
        validate_required_args(arguments, ["project_id", "inventory_id"])
        
        project_id = arguments["project_id"]
        inventory_id = arguments["inventory_id"]
        name = arguments.get("name")
        inventory_data = arguments.get("inventory_data")
        
        try:
            response = self.semaphore.update_inventory(
                project_id, inventory_id, name, inventory_data
            )
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))
            
    async def tool_delete_inventory(self, arguments):
        """Delete inventory tool implementation."""
        validate_required_args(arguments, ["project_id", "inventory_id"])
        
        project_id = arguments["project_id"]
        inventory_id = arguments["inventory_id"]
        
        try:
            response = self.semaphore.delete_inventory(project_id, inventory_id)
            return format_json_response(response)
        except Exception as e:
            return format_error(str(e))

    async def handle_message(self, message_str: str) -> Optional[str]:
        """
        Handle an incoming MCP message.
        
        Args:
            message_str: JSON-encoded MCP message
            
        Returns:
            JSON-encoded response if needed, None otherwise
        """
        try:
            message = json.loads(message_str)
            message_type = message.get("type")
            
            if message_type == REQUEST:
                return await self._handle_request(message)
            
            # For now, we don't handle other message types
            return None
            
        except json.JSONDecodeError:
            logger.error(f"Received invalid JSON: {message_str}")
            return self._create_error_response(
                "invalid_request",
                "Invalid JSON message",
                None
            )
        except Exception as e:
            logger.exception("Error handling message")
            return self._create_error_response(
                "internal_error",
                str(e),
                None
            )
    
    async def _handle_request(self, request: Dict[str, Any]) -> str:
        """
        Handle an MCP request message.
        
        Args:
            request: Parsed request message
            
        Returns:
            JSON-encoded response
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")
        
        if method == "tools/list":
            return await self._handle_tools_list(req_id)
        elif method == "tools/call":
            return await self._handle_tools_call(req_id, params)
        else:
            return self._create_error_response(
                "method_not_found",
                f"Method '{method}' not found",
                req_id
            )
    
    async def _handle_tools_list(self, req_id: Any) -> str:
        """Handle tools/list request."""
        tools_list = list(self.tools.keys())
        return self._create_success_response({"tools": tools_list}, req_id)
    
    async def _handle_tools_call(self, req_id: Any, params: Dict[str, Any]) -> str:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        if not tool_name:
            return self._create_error_response(
                "invalid_params", 
                "Missing tool name", 
                req_id
            )
        
        # Check if the tool exists
        if tool_name not in self.tools:
            return self._create_error_response(
                "invalid_params",
                f"Tool '{tool_name}' not found",
                req_id
            )
        
        try:
            # Call the tool
            result = await self.tools[tool_name](tool_args)
            
            # Handle case where result is already a properly formatted error
            if result.get("content") and result["content"][0].get("type") == "error":
                return self._create_error_response(
                    "tool_error",
                    result["content"][0].get("text"),
                    req_id
                )
            
            # Create proper success response with the tool result
            return self._create_success_response(result, req_id)
            
        except KeyError as e:
            return self._create_error_response(
                "invalid_params",
                f"Missing required parameter: {str(e)}",
                req_id
            )
        except Exception as e:
            logger.exception(f"Error calling tool '{tool_name}'")
            return self._create_error_response(
                "internal_error",
                f"Error calling tool: {str(e)}",
                req_id
            )
    
    def _create_success_response(self, result: Dict[str, Any], req_id: Any) -> str:
        """Create a successful MCP response."""
        response = {
            "type": RESPONSE,
            "success": True,
            "id": req_id,
            "result": result
        }
        return json.dumps(response)
    
    def _create_error_response(self, code: str, message: str, req_id: Any) -> str:
        """Create an MCP error response."""
        response = {
            "type": RESPONSE,
            "success": False,
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        return json.dumps(response)

    async def run_stdio(self):
        """Run the MCP server using standard input/output."""
        logger.info("Starting SemaphoreMCP server (stdio mode)")
        
        while True:
            try:
                # Read a line from stdin (corresponds to a message)
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )
                
                # Handle the message and get a response
                response = await self.handle_message(line)
                
                # If there's a response, write it to stdout
                if response:
                    print(response, flush=True)
                    
            except (EOFError, KeyboardInterrupt):
                logger.info("Received EOF or interrupt, shutting down")
                break
            except Exception as e:
                logger.exception("Unexpected error in main loop")
                
                # Try to send an error response
                error_response = self._create_error_response(
                    "internal_error",
                    f"Unexpected error: {str(e)}",
                    None
                )
                print(error_response, flush=True)


async def start_stdio_server(
    semaphore_url: Optional[str] = None,
    semaphore_token: Optional[str] = None
):
    """
    Start an MCP server in stdio mode.
    
    Args:
        semaphore_url: SemaphoreUI API URL (default: from environment)
        semaphore_token: SemaphoreUI API token (default: from environment)
    """
    # Use provided values or fall back to config
    url = semaphore_url or get_config("SEMAPHORE_URL")
    token = semaphore_token or get_config("SEMAPHORE_API_TOKEN")
    
    logger.info(f"Starting MCP server with SemaphoreUI at {url}")
    server = MCPServer(url, token)
    await server.run_stdio()


def main():
    """Entry point for the MCP server."""
    asyncio.run(start_stdio_server())


if __name__ == "__main__":
    main()
