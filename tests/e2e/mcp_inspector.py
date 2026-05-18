"""Helper module for interacting with MCP Inspector CLI."""

import json
import os
import subprocess
import time
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
        self.timeout = int(os.getenv("MCP_INSPECTOR_TIMEOUT", "90"))
        self.retries = int(os.getenv("MCP_INSPECTOR_RETRIES", "2"))
        self.retry_delay = float(os.getenv("MCP_INSPECTOR_RETRY_DELAY", "2"))

    def _is_retryable_error(self, output: str) -> bool:
        """Return whether Inspector output looks like a transient MCP timeout."""
        return "MCP error -32001" in output or "Request timed out" in output

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

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=self.timeout,
                )
                # Parse JSON from stdout
                return json.loads(result.stdout)
            except subprocess.CalledProcessError as e:
                output = e.stderr or e.stdout or ""
                if attempt < self.retries and self._is_retryable_error(output):
                    last_error = e
                    time.sleep(self.retry_delay)
                    continue
                raise MCPInspectorError(f"Inspector command failed: {output}") from e
            except json.JSONDecodeError as e:
                raise MCPInspectorError(
                    f"Failed to parse inspector output: {result.stdout}"
                ) from e
            except subprocess.TimeoutExpired as e:
                if attempt < self.retries:
                    last_error = e
                    time.sleep(self.retry_delay)
                    continue
                raise MCPInspectorError("Inspector command timed out") from e

        raise MCPInspectorError(
            "Inspector command failed after retries"
        ) from last_error

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
                # Use json.dumps for complex types (dict, list, bool, None)
                # but keep strings as-is to avoid double-quoting
                if isinstance(value, str):
                    str_value = value
                else:
                    str_value = json.dumps(value)
                args.extend(["--tool-arg", f"{key}={str_value}"])

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
