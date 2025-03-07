"""
Module defining the NPN MCP server functionalities.

Include setting up the server, defining tools for querying the NPN API,
and handling requests for observation data and comments.

The server is built using MCP (Model Content Protocol) to facilitate
communication for the USA National Phenology Network (NPN) API.
"""

import json
import logging
from typing import Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
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
from usa_npn_mcp_server.utils.endpoints import NPNTools


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
        logger.info("Handling list_tools request")
        return [
            Tool(
                name=NPNTools.Observations.name,
                description=NPNTools.Observations.description,
                inputSchema=NPNTools.Observations.input_schema,
            ),
            Tool(
                name=NPNTools.ObservationComment.name,
                description=NPNTools.ObservationComment.description,
                inputSchema=NPNTools.ObservationComment.input_schema,
            ),
            Tool(
                name=NPNTools.SummarizedData.name,
                description=NPNTools.SummarizedData.description,
                inputSchema=NPNTools.SummarizedData.input_schema,
            ),
            Tool(
                name=NPNTools.MagnitudeData.name,
                description=NPNTools.MagnitudeData.description,
                inputSchema=NPNTools.MagnitudeData.input_schema,
            ),
            Tool(
                name=NPNTools.SiteLevelData.name,
                description=NPNTools.SiteLevelData.description,
                inputSchema=NPNTools.SiteLevelData.input_schema,
            ),
        ]

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        """Client can call this to get a list of available resources."""
        logger.info("Handling list_resources request")
        return [
            Resource(
                uri=AnyUrl(f"npn-mcp://{NPNTools.Observations.name}"),
                name=f"{NPNTools.Observations.name}_resource",
                description="Resource updated by 'observations' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
            Resource(
                uri=AnyUrl(f"npn-mcp://{NPNTools.ObservationComment.name}"),
                name=f"{NPNTools.ObservationComment.name}_resource",
                description="Resource updated by 'observation_comment' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
            Resource(
                uri=AnyUrl(f"npn-mcp://{NPNTools.SummarizedData.name}"),
                name=f"{NPNTools.SummarizedData.name}_resource",
                description="Resource updated by 'summarized_data' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
            Resource(
                uri=AnyUrl(f"npn-mcp://{NPNTools.MagnitudeData.name}"),
                name=f"{NPNTools.MagnitudeData.name}_resource",
                description="Resource updated by 'magnitude_data' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
            Resource(
                uri=AnyUrl(f"npn-mcp://{NPNTools.SiteLevelData.name}"),
                name=f"{NPNTools.SiteLevelData.name}_resource",
                description="Resource updated by 'site_level_data' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
        ]

    @server.read_resource()
    async def handle_read_resource(
        uri: AnyUrl,
    ) -> Dict[str, list[TextResourceContents | ImageContent]]:
        """Client can call this to read a resource."""
        logger.info(f"Handling read_resource request for URI: {uri}")
        # Throw error if the URI scheme is not supported
        if uri.scheme != "npn-mcp":
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
        name = str(uri).replace("npn-mcp://", "")
        last_resource = api_client.read_last_response(name=name)
        return {
            "contents": [
                TextResourceContents(
                    uri=uri,
                    mimeType="plain/text",
                    text=json.dumps(last_resource),
                ),
            ]
        }

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Dict[str, str] | None
    ) -> list[TextContent | ImageContent | EmbeddedResource]:
        """Client can call this to use a tool."""
        logger.info(f"Calling tool {name} with parameters: {arguments}")
        if arguments is None:
            raise ValueError("Arguments cannot be None")
        # Call tool by name
        match name:
            case NPNTools.Observations.name:
                await api_client.query_api(NPNTools.Observations.endpoint, arguments)
            case NPNTools.ObservationComment.name:
                await api_client.query_api(
                    NPNTools.ObservationComment.endpoint, arguments
                )
            case NPNTools.SummarizedData.name:
                await api_client.query_api(NPNTools.SummarizedData.endpoint, arguments)
            case NPNTools.MagnitudeData.name:
                await api_client.query_api(NPNTools.MagnitudeData.endpoint, arguments)
            case NPNTools.SiteLevelData.name:
                await api_client.query_api(NPNTools.SiteLevelData.endpoint, arguments)
            case _:
                logger.error(f"Unknown tool requested: {name}")
                raise ValueError(f"Unknown tool requested: {name}")
        # Notify client of resource update
        await server.request_context.session.send_resource_updated(
            AnyUrl(f"npn-mcp://{name}")
        )
        return [
            # Consider adding TextContent with a message about state
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{name}_output_schema"),
                    mimeType="plain/text",
                    text=json.dumps(api_client.read_output_schema(name=name)),
                ),
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{name}"),
                    mimeType="plain/text",
                    text=json.dumps(api_client.read_last_response(name=name)),
                ),
            ),
        ]

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
