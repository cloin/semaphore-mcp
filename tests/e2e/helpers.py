"""Helper functions for E2E tests."""

import json
from typing import Any


def parse_mcp_response(response: dict[str, Any]) -> Any:
    """Parse MCP tool response to extract data.

    MCP returns responses in format:
    {"content": [{"type": "text", "text": "...json string..."}]}

    This function extracts and parses the JSON from the text field.

    Args:
        response: Raw MCP response dict

    Returns:
        Parsed data from the response
    """
    content = response.get("content", [])
    if content and isinstance(content, list) and len(content) > 0:
        first_content = content[0]
        if isinstance(first_content, dict) and "text" in first_content:
            try:
                return json.loads(first_content["text"])
            except json.JSONDecodeError:
                # Return raw text if not JSON
                return first_content["text"]
    return response
