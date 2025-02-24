"""
Module defining the NPN MCP server functionalities.

Include setting up the server, defining tools for querying the NPN API,
and handling requests for observation data and comments.

The server is built using MCP (Model Content Protocol) to facilitate
communication for the USA National Phenology Network (NPN) API.
"""

import json
import logging
from enum import Enum

import httpx
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    # Prompt,
    # PromptArgument,
    # GetPromptResult,
    # PromptMessage,
)

from usa_npn_mcp_server.endpoint_classes import (
    ObservationCommentQuery,
    ObservationsQuery,
)


# Base URL for the NPN API observations endpoints.
API_BASE_URL = "https://services.usanpn.org:443/npn_portal/observations/"

logger = logging.getLogger(__name__)


class NPNTools(str, Enum):
    """
    An enumeration of tools available for querying the NPN API.

    Attributes
    ----------
    OBSERVATIONS : str
        Tool for querying raw observation data.
    OBSERVATION_COMMENT : str
        Tool for retrieving comments associated with specific observations.
    """

    OBSERVATIONS = "observations"
    OBSERVATION_COMMENT = "observation_comment"


async def base_fetch(endpoint: str, **kwargs):
    """
    Fetch data from a specified NPN API endpoint using JSON.

    Builds the URL from the base URL, endpoint, and query parameters.

    Parameters
    ----------
    - endpoint (str): The API endpoint to fetch data from.
    - **kwargs: Query parameters to pass to the API.
    """
    # Ensure 'request_src' is always 'vectorMCP'
    kwargs["request_src"] = "vectorMCP"
    # Remove None or empty values from parameters and put together API httpx URL query
    query_params = {k: v for k, v in kwargs.items() if v is not None and v != ""}
    query_string = "&".join(
        f"{k}={requests.utils.quote(str(v))}" for k, v in query_params.items()
    )
    query_url = f"{API_BASE_URL}{endpoint}.json?{query_string}"  # Always using json for the moment
    logger.info(f"Fetching data from URL: {query_url}")
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        try:
            response = await client.get(query_url)
            response.raise_for_status()
            # Return the JSON data as a JSON string.
            json_data = response.json()
            return json.dumps(json_data)
        except Exception as exc:
            logger.error(f"Error fetching data: {exc}")
            return json.dumps({"message": f"Error fetching data: {str(exc)}"})


async def serve() -> None:
    """Start the MCP server for the NPN API."""
    server = Server("usa-npn-mcp-server")
    logger.info("Starting MCP NPN Server...")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=NPNTools.OBSERVATIONS,
                description="Query NPN API for raw observation data (getObservations)",
                inputSchema=ObservationsQuery.schema(),
            ),
            Tool(
                name=NPNTools.OBSERVATION_COMMENT,
                description="Retrieve the comment for a given observation (getObservationComment)",
                inputSchema=ObservationCommentQuery.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        # Clean up the arguments.
        query_params = {k: v for k, v in arguments.items() if v is not None}
        logger.info(f"Calling tool {name} with parameters: {query_params}")
        match name:
            case NPNTools.OBSERVATIONS:
                data = await base_fetch("getObservations", **query_params)
                return [TextContent(type="text", text=f"Returned:\n{data}")]
            case NPNTools.OBSERVATION_COMMENT:
                data = await base_fetch("getObservationComment", **query_params)
                return [TextContent(type="text", text=f"Returned:\n{data}")]
            case _:
                logger.error(f"Unknown tool requested: {name}")
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
