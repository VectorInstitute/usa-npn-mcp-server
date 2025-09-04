"""
Module defining the NPN MCP server functionalities.

Include setting up the server, defining tools for querying the NPN API,
and handling requests for observation data and comments.

The server is built using MCP (Model Content Protocol) to facilitate
communication for the USA National Phenology Network (NPN) API.
"""

import json
import logging
import os
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
    Root,
    ServerCapabilities,
    TextContent,
    TextResourceContents,
    Tool,
    ToolsCapability,
)
from pydantic import AnyUrl, FileUrl

from usa_npn_mcp_server.api_client import APIClient
from usa_npn_mcp_server.utils.prompts import PROMPTS, get_prompts


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def _initialize_roots(allowed_dirs: tuple[str, ...], api_client: APIClient) -> None:
    """
    Initialize allowed directories/roots for the API client.

    Parameters
    ----------
    allowed_dirs : tuple[str, ...]
        A tuple of directory paths to be initialized as allowed roots.
    api_client : APIClient
        The API client instance to update with the allowed roots.

    Returns
    -------
    None
    """
    # Check for allowed directories from parameters or environment
    dirs_list = list(allowed_dirs) if allowed_dirs else []

    # If no directories provided via parameters, check environment variable
    if not dirs_list and os.environ.get("NPN_MCP_ALLOWED_DIRS"):
        # Use os.pathsep for cross-platform path separator (: on Unix, ; on Windows)
        dirs_list = os.environ["NPN_MCP_ALLOWED_DIRS"].split(os.pathsep)

    # Convert to Root objects for the API client
    if dirs_list:
        roots = []
        for idx, dir_path in enumerate(dirs_list):
            abs_path = os.path.abspath(dir_path)
            if os.path.exists(abs_path):
                roots.append(
                    Root(
                        uri=FileUrl(f"file://{abs_path}"),
                        name=os.path.basename(abs_path) or f"Root_{idx}",
                    )
                )
            else:
                logger.warning(f"Specified directory does not exist: {dir_path}")
        if roots:
            api_client.update_allowed_roots(roots)
            logger.info(
                f"Initialized with {len(roots)} allowed directories for file export"
            )
        else:
            logger.info("No valid directories found for file export")
    else:
        logger.info("No allowed directories specified. File export will be disabled.")


async def serve(allowed_dirs: tuple[str, ...] = ()) -> None:
    """
    Start the MCP server for the NPN API.

    Parameters
    ----------
    allowed_dirs : tuple[str, ...], optional
        A tuple of directory paths that are allowed for file export operations.
        If not provided, defaults to an empty tuple, and file export will be disabled
        unless directories are specified with NPN_MCP_ALLOWED_DIRS environment variable.
    """
    server: Server[None] = Server("usa-npn-mcp-server")
    logger.info("Starting MCP NPN Server...")
    api_client = APIClient()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """
        Client can call this to get a list of available tools.

        Returns
        -------
        list[Tool]
            A list of available tools with their names, descriptions, and input schemas.
        """
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
        """
        Client can call this to get a list of available resources.

        Returns
        -------
        list[Resource]
            A list of available resources including recent queries and available roots.
        """
        return [
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

    @server.read_resource()
    async def handle_read_resource(
        uri: AnyUrl,
    ) -> Dict[str, list[TextResourceContents]]:
        """
        Client can call this to read a resource.

        Parameters
        ----------
        uri : AnyUrl
            The URI of the resource to read.

        Returns
        -------
        Dict[str, list[TextResourceContents]]
            A dictionary containing the resource contents.
        """
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
        elif resource_name == "available-roots":
            # Return available roots for file operations
            roots_info = []
            for root in api_client.get_allowed_roots():
                roots_info.append(
                    {
                        "name": root.name or "Unnamed Root",
                        "uri": str(root.uri),
                        "path": str(root.uri)[7:]
                        if str(root.uri).startswith("file://")
                        else str(root.uri),
                    }
                )
            contents = [
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=json.dumps(
                        {
                            "roots_available": len(roots_info) > 0,
                            "roots": roots_info,
                            "message": "File export operations will use these roots"
                            if roots_info
                            else "No roots available. MCP client needs to provide roots for file operations.",
                        },
                        indent=2,
                    ),
                )
            ]
        else:
            raise ValueError(f"Unknown resource: {resource_name}")

        return {"contents": contents}

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Union[Dict[str, str], None]
    ) -> Any:
        """
        Client can call this to use a tool.

        Parameters
        ----------
        name : str
            The name of the tool to call.
        arguments : Union[Dict[str, str], None]
            The arguments to pass to the tool.

        Returns
        -------
        Any
            The result of the tool execution.
        """
        return await api_client.handle_call_tool(name=name, arguments=arguments)

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        """
        Client can call this to get a list of available prompts.

        Returns
        -------
        list[Prompt]
            A list of available prompt objects.
        """
        return get_prompts()

    @server.get_prompt()
    async def handle_get_prompt(
        prompt_name: str, arguments: Union[Dict[str, str], None]
    ) -> GetPromptResult:
        """
        Client can call this to get a prompt by name with formatted arguments.

        Parameters
        ----------
        prompt_name : str
            The name of the prompt to retrieve.
        arguments : Union[Dict[str, str], None]
            Arguments to format into the prompt template.

        Returns
        -------
        GetPromptResult
            A formatted prompt result ready for use.
        """
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

    # Initialize allowed directories/roots
    _initialize_roots(allowed_dirs, api_client)

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
