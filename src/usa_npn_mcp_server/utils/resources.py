"""Module for defining MCP resources for the NPN MCP server."""

from typing import List

from mcp.types import Resource
from pydantic import AnyUrl


# Define available MCP resources
MCP_RESOURCES: List[Resource] = [
    Resource(
        uri=AnyUrl("npn-mcp://recent-queries"),
        name="recent-queries-resource",
        description="List of recent query hash IDs and metadata for cached data access.",
        mimeType="application/json",
    ),
    Resource(
        uri=AnyUrl("npn-mcp://available-roots"),
        name="available-roots-resource",
        description="List of available root directories for file export operations.",
        mimeType="application/json",
    ),
]
