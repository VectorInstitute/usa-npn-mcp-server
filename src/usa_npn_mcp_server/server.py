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

from usa_npn_mcp_server.api_client import APIClient, NPNTools
from usa_npn_mcp_server.endpoint_classes import (
    ObservationCommentQuery,
    ObservationsQuery,
)


# Base URL for the NPN API observations endpoints.
API_BASE_URL = "https://services.usanpn.org:443/npn_portal/observations/"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def serve() -> None:
    """Start the MCP server for the NPN API."""
    server: Server[None] = Server("usa-npn-mcp-server")
    logger.info("Starting MCP NPN Server...")
    api_client = APIClient(base_url=API_BASE_URL)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        logger.info("Handling list_tools request")
        return [
            Tool(
                name=NPNTools.OBSERVATIONS,
                description="Query NPN API for raw observation data (getObservations), results stored as readable Resource 'observations'",
                inputSchema=ObservationsQuery.model_json_schema(),
            ),
            Tool(
                name=NPNTools.OBSERVATION_COMMENT,
                description="Retrieve the comment for a given observation (getObservationComment), results store as readable Resource 'observation_comment'",
                inputSchema=ObservationCommentQuery.model_json_schema(),
            ),
        ]

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        logger.info("Handling list_resources request")
        return [
            Resource(
                uri=AnyUrl("npn-mcp://observations"),
                name="observations_resource",
                description="Resource updated by 'observations' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
            Resource(
                uri=AnyUrl("npn-mcp://observation_comment"),
                name="observation_comment_resource",
                description="Resource updated by 'observation_comment' Tool and used to read JSON results",
                mimeType="plain/text",
            ),
        ]

    @server.read_resource()
    async def handle_read_resource(
        uri: AnyUrl,
    ) -> Dict[str, list[TextResourceContents | ImageContent]]:
        logger.info(f"Handling read_resource request for URI: {uri}")
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
        logger.info(f"Calling tool {name} with parameters: {arguments}")
        if arguments is None:
            raise ValueError("Arguments cannot be None")
        match name:
            case NPNTools.OBSERVATIONS:
                await api_client.query_api("getObservations", arguments)
            case NPNTools.OBSERVATION_COMMENT:
                await api_client.query_api("getObservationComment", arguments)
            case _:
                logger.error(f"Unknown tool requested: {name}")
                raise ValueError(f"Unknown tool requested: {name}")
        await server.request_context.session.send_resource_updated(
            AnyUrl(f"npn-mcp://{name}")
        )
        return [  # Consider adding output schema as embedded resource
            # Consider adding TextContent with a message
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{name}"),
                    mimeType="plain/text",
                    text=json.dumps(api_client.read_last_response(name=name)),
                ),
            ),
        ]

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
