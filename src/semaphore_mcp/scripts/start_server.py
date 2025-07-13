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
        "--verbose", "-v", help="Enable verbose logging", action="store_true"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        import logging

        logging.getLogger("semaphore_mcp").setLevel(logging.DEBUG)

    start_server(args.url, args.token)


if __name__ == "__main__":
    main()
