"""Helper module for interacting with MCP Inspector CLI."""

import json
import subprocess
from typing import Any


class MCPInspectorError(Exception):
    """Error when calling MCP Inspector."""

    pass


class MCPInspector:
    """Wrapper for MCP Inspector CLI operations."""

    def __init__(self, server_url: str, transport: str = "http"):
        """Initialize MCP Inspector client.

        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8000)
            transport: Transport protocol (sse or http)
        """
        # For streamable-http transport, append /mcp endpoint if not present
        if transport == "http" and not server_url.endswith("/mcp"):
            server_url = server_url.rstrip("/") + "/mcp"
        self.server_url = server_url
        self.transport = transport

    def _run_inspector(self, args: list[str]) -> dict[str, Any]:
        """Run MCP Inspector CLI and return parsed JSON output.

        Args:
            args: Additional arguments to pass to inspector

        Returns:
            Parsed JSON response from inspector

        Raises:
            MCPInspectorError: If inspector command fails
        """
        cmd = [
            "npx",
            "@modelcontextprotocol/inspector",
            "--cli",
            self.server_url,
            "--transport",
            self.transport,
        ] + args

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )
            # Parse JSON from stdout
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise MCPInspectorError(
                f"Inspector command failed: {e.stderr or e.stdout}"
            ) from e
        except json.JSONDecodeError as e:
            raise MCPInspectorError(
                f"Failed to parse inspector output: {result.stdout}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise MCPInspectorError("Inspector command timed out") from e

    def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools.

        Returns:
            List of tool definitions
        """
        result = self._run_inspector(["--method", "tools/list"])
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call a specific tool.

        Args:
            name: Tool name
            arguments: Tool arguments as dict

        Returns:
            Tool response
        """
        args = ["--method", "tools/call", "--tool-name", name]

        if arguments:
            for key, value in arguments.items():
                # Convert value to string for CLI
                args.extend(["--tool-arg", f"{key}={json.dumps(value)}"])

        return self._run_inspector(args)

    def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources.

        Returns:
            List of resource definitions
        """
        result = self._run_inspector(["--method", "resources/list"])
        return result.get("resources", [])

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all available prompts.

        Returns:
            List of prompt definitions
        """
        result = self._run_inspector(["--method", "prompts/list"])
        return result.get("prompts", [])
