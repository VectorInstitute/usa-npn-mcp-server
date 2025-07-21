"""
Module defining the NPN MCP server functionalities.

Include setting up the server, defining tools for querying the NPN API,
and handling requests for observation data and comments.

The server is built using MCP (Model Content Protocol) to facilitate
communication for the USA National Phenology Network (NPN) API.
"""

import json
import logging
from typing import Any, Dict, Union

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptMessage,
    Resource,
    ResourcesCapability,
    ServerCapabilities,
    TextContent,
    TextResourceContents,
    Tool,
    ToolsCapability,
)
from pydantic import AnyUrl

from usa_npn_mcp_server.api_client import APIClient
from usa_npn_mcp_server.utils.prompts import PROMPTS, get_prompts


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def serve() -> None:
    """Start the MCP server for the NPN API."""
    server: Server[None] = Server("usa-npn-mcp-server")
    logger.info("Starting MCP NPN Server...")
    api_client = APIClient()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Client can call this to get a list of available tools."""
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
            )
            for tool in api_client.get_tool_list()
        ]

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """Client can call this to get a list of available resources."""
        resources = [
            Resource(
                uri=AnyUrl(f"npn-mcp://{tool.name}"),
                name=f"{tool.name}-resource",
                description=f"Resource updated by {tool.name} Tool.",
                mimeType="plain/text",
            )
            for tool in api_client.get_tool_list()
        ]

        # Add the recent-queries resource
        resources.append(
            Resource(
                uri=AnyUrl("npn-mcp://recent-queries"),
                name="recent-queries-resource",
                description="List of recent query hash IDs and metadata for cached data access.",
                mimeType="application/json",
            )
        )

        return resources

    @server.read_resource()
    async def handle_read_resource(
        uri: AnyUrl,
    ) -> Dict[str, list[TextResourceContents]]:
        """Client can call this to read a resource."""
        if uri.scheme != "npn-mcp":
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        resource_name = str(uri).replace("npn-mcp://", "")

        if resource_name == "recent-queries":
            # Return cache statistics for recent queries
            cache_stats = api_client.cache_manager.get_cache_stats()
            contents = [
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=json.dumps(cache_stats, indent=2),
                )
            ]
        else:
            # Legacy resource handling - provide deprecation notice
            contents = [
                TextResourceContents(
                    uri=uri,
                    mimeType="plain/text",
                    text=f"Resource access for '{resource_name}' has been updated to use hash-based caching. Use 'recent-queries' resource to see available cached data with hash IDs, then use 'get-raw-data' tool with specific hash IDs.",
                )
            ]

        return {"contents": contents}

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Union[Dict[str, str], None]
    ) -> Any:
        """Client can call this to use a tool."""
        return await api_client.handle_call_tool(name=name, arguments=arguments)

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        return get_prompts()

    @server.get_prompt()
    async def handle_get_prompt(
        prompt_name: str, arguments: Union[Dict[str, str], None]
    ) -> GetPromptResult:
        if prompt_name not in PROMPTS:
            raise ValueError(f"Prompt '{prompt_name}' not found.")
        if arguments is None:
            arguments = {}
        prompt = str(PROMPTS[prompt_name]["template"]).format(**arguments)
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )

    # Initialize server to listen for resource changes
    options = InitializationOptions(
        server_name="usa-npn-mcp-server",
        server_version="0.1.0",
        capabilities=ServerCapabilities(
            resources=ResourcesCapability(subscribe=True, listChanged=True),
            tools=ToolsCapability(listChanged=True),
        ),
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
