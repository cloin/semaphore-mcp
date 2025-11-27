#!/usr/bin/env python3
"""
Script to start the SemaphoreMCP server using FastMCP.
"""

import argparse
import os

from semaphore_mcp.server import start_server


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Start the SemaphoreMCP server")

    parser.add_argument(
        "--url",
        help="SemaphoreUI API URL (default: from SEMAPHORE_URL env or http://localhost:3000)",
        default=os.environ.get("SEMAPHORE_URL", "http://localhost:3000"),
    )
    parser.add_argument(
        "--token",
        help="SemaphoreUI API token (default: from SEMAPHORE_API_TOKEN env)",
        default=os.environ.get("SEMAPHORE_API_TOKEN"),
    )
    parser.add_argument(
        "--transport",
        help="Transport type: stdio or http (default: from MCP_TRANSPORT env or stdio)",
        choices=["stdio", "http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
    )
    parser.add_argument(
        "--host",
        help="Host to bind to for HTTP transport (default: from MCP_HOST env or 0.0.0.0)",
        default=os.environ.get("MCP_HOST", "0.0.0.0"),
    )
    parser.add_argument(
        "--port",
        help="Port for HTTP transport (default: from MCP_PORT env or 8000)",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
    )
    parser.add_argument(
        "--verbose", "-v", help="Enable verbose logging", action="store_true"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        import logging

        logging.getLogger("semaphore_mcp").setLevel(logging.DEBUG)

    start_server(
        semaphore_url=args.url,
        semaphore_token=args.token,
        transport=args.transport,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
