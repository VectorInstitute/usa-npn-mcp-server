"""Module with supplementary functions/classes for the NPN MCP server."""

from __future__ import annotations

import json
import logging
import sqlite3
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from statistics import mean, median
from types import TracebackType
from typing import Any, Dict, Optional, Type, Union
from urllib.parse import urlencode

import httpx
import numpy as np
import pandas as pd
from mcp.types import (
    BlobResourceContents,
    EmbeddedResource,
    ImageContent,
    TextContent,
    TextResourceContents,
)
from pydantic import AnyUrl

from usa_npn_mcp_server.utils.endpoints import NPNTool, NPNTools
from usa_npn_mcp_server.utils.output_schema import API_SCHEMAS
from usa_npn_mcp_server.utils.plotting import generate_map


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NPN_API_Client")


def log_call(func: Any) -> Any:
    """
        Log function calls and their execution times, including exceptions.

    Parameters
    ----------
        func: The function to be decorated.

    Returns
    -------
        Callable: The decorated function.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        function_name = func.__name__
        start = datetime.now()
        logger.info(f"Calling {function_name} with args: {args[1:]} kwargs: {kwargs}")
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.now() - start).total_seconds()
            logger.info(f"Successfully completed {function_name} in {duration:.2f}s")
            return result
        except Exception as ex:
            duration = (datetime.now() - start).total_seconds()
            logger.error(
                f"Error running {function_name} after {duration:.2f}s: {str(ex)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise

    return wrapper


class APIClient:
    """API Client for mediating MCP server and NPN API interactions."""

    # Base URL for the NPN API observations endpoints.
    API_BASE_URL: str = "https://services.usanpn.org/npn_portal/observations"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=60.0, base_url=self.API_BASE_URL)
        self._tool_list: list[NPNTool] = [
            NPNTools.StatusIntensity,
            NPNTools.ObservationComment,
            NPNTools.MagnitudePhenometrics,
            NPNTools.SitePhenometrics,
            NPNTools.IndividualPhenometrics,
            NPNTools.Mapping,
            NPNTools.CheckReferenceMaterial,
        ]
        self._cache: Dict[
            str,
            Dict[
                str,
                Any,
            ],
        ] = {
            str(tool.name): {
                "raw": list[Dict[str, Any]](),
                "responses": list[
                    list[Union[TextContent, ImageContent, EmbeddedResource]]
                ](),
                "maps": list[
                    list[Union[TextContent, ImageContent, EmbeddedResource]]
                ](),
            }
            for tool in self._tool_list
        }

    async def __aenter__(self) -> APIClient:
        """
        Asynchronous context manager entry method.

        Returns
        -------
            self: The instance of the class.
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Asynchronous context manager exit method.

        This method is called when exiting the runtime context of the asynchronous
        context manager. It ensures that the `close` method is awaited to properly
        release any resources.

        Args:
            exc_type (Optional[Type[BaseException]]): The exception type if an exception
                was raised, otherwise None.
            exc_val (Optional[BaseException]): The exception instance if an exception
                was raised, otherwise None.
            exc_tb (Optional[TracebackType]): The traceback object if an exception
                was raised, otherwise None.

        Returns
        -------
            None
        """
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    def get_tool_list(self) -> list[NPNTool]:
        """Get the list of available tools."""
        return self._tool_list

    @log_call
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a logged GET request to the NPN API.

        Parameters
        ----------
            endpoint (str): The API endpoint to query.
            params (Dict[str, Any]): The parameters to pass to the API.

        Returns
        -------
            Dict[str, Any]: The JSON response from the API.
        -----------

        Raises
        ------
            Exception: If the request fails or if the response contains an error.
        """
        if params is None:
            params = {}
        # Ensure 'request_src' is always 'vectorMCP'
        params["request_src"] = "vectorMCP"
        query_params = urlencode(params)
        request_url = f"{self.API_BASE_URL}/{endpoint}.json?{query_params}"
        response = await self.client.get(request_url)
        logger.info(f"Querying APIClient's _get with: {request_url}")
        try:
            response.raise_for_status()
        except Exception as ex:
            logger.error(f"Error in APIClient's _get: {ex}")
            raise Exception(response.json().get("error", str(ex))) from ex
        return response.json()

    async def query_api(self, endpoint: str, arguments: Dict[str, Any]) -> None:
        """
        Query the API and store the response.

        Parameters
        ----------
            endpoint (str): The API endpoint to query.
            arguments (Dict[str, Any]): The arguments to pass to the API.
        """
        name = next(
            (tool.name for tool in self._tool_list if tool.endpoint == endpoint), None
        )
        if not name:
            raise ValueError(f"No matching tool name found for endpoint: {endpoint}")
        response = await self._get(endpoint, params=arguments)
        self._cache[name]["raw"].append(response)
        logger.info(f"Response stored for {name}.")

    def summarize_response(self, name: str) -> Dict[str, Any]:
        """Get unique variables and entries from last API response by tool name."""
        logger.info(f"Summarizing {name} response")
        if name not in self._cache:
            raise ValueError(f"Tool not in cache: {name}")
        if "raw" not in self._cache[name]:
            raise ValueError(f"No cached response found for {name}")
        last_response = self._cache[name]["raw"][-1:]
        if not last_response:
            return {"result": None}

        unique_keys_summary: dict[str, set[Any]] = {}
        full_dataset: dict[str, list[Any]] = {}
        discrete_summary: dict[str, list[Any]] = {}
        continuous_summary: dict[str, dict[str, float]] = {}
        only_null: list[str] = []

        # Collect unique keys and their values
        for entry in last_response:  # Ensure entry is a dictionary
            if isinstance(entry, dict):
                for key, value in entry.items():
                    if key not in unique_keys_summary:
                        unique_keys_summary[key] = set()
                        full_dataset[key] = []
                    unique_keys_summary[key].add(value)
                    full_dataset[key].append(value)

        int_encoded = ["phenophase_status", "patch", "itis_number", "year"]
        # Process unique values to identify continuous variables and null-only variables
        for key, values in unique_keys_summary.items():
            if values == {-9999}:
                only_null.append(key)
            elif "_id" in key or key in int_encoded:
                discrete_summary[key] = list(values)
            elif key == "elevation_in_meters" or all(
                isinstance(v, (int, float)) and v != -9999 for v in values
            ):
                values_list = [v for v in full_dataset[key] if v != -9999]
                continuous_summary[key] = {
                    "length": len(values_list),
                    "min": min(values_list),
                    "max": max(values_list),
                    "mean": mean(values_list),
                    "median": median(values_list),
                    "1st_quartile": np.percentile(values_list, 25),
                    "3rd_quartile": np.percentile(values_list, 75),
                }
            else:
                discrete_summary[key] = list(values)

        # Convert sets to lists for JSON serialization compatibility
        summary: dict[str, Any] = {
            "discrete": {
                key: list(val)
                for key, val in discrete_summary.items()
                if key not in continuous_summary and key not in only_null
            },
            "continuous": continuous_summary,
            "only_null": only_null,
        }
        return {"result": summary}

    def read_ancillary_file(self, sql_query: str) -> str:
        """
        Read the ancillary file from the database.

        Parameters
        ----------
            sql_query (str): The SQL query to execute.

        Returns
        -------
            str: The result of the SQL query.
        """
        db_path = Path(__file__).parent / "data" / "ancillary_data.db"
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(sql_query, conn)
        conn.close()
        result = df.to_dict(orient="records")
        if not result:
            raise ValueError(f"No results found for query: {sql_query}")
        return json.dumps(result)

    def read_output_schema(self, name: str) -> Dict[str, Any]:
        """Get the schema from the last API response by tool name."""
        logger.info(f"Reading {name} output_schema resource")
        if name not in self._cache:
            raise ValueError(f"Tool not in cache: {name}")
        if "raw" not in self._cache[name]:
            raise ValueError(f"No cached response found for {name}")
        last_response = self._cache[name]["raw"][-1:]
        if not last_response[0]:
            return {"result": None}
        # Get the full schema for the tool
        full_schema = API_SCHEMAS[name]["properties"]
        if isinstance(last_response[0], dict):
            keys = [key for key, val in last_response[0].items() if val]
        else:
            keys = []
        select_schema = {key: full_schema[key] for key in keys if key in full_schema}
        logger.info(f"Output schema keys: {keys}")
        return {"result": select_schema} if select_schema else {"result": None}

    def query_response(
        self, name: str
    ) -> list[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get the Server response by query Tool name."""
        logger.info(f"Returning {name} query Tool response.")
        summary = self.summarize_response(name=name)
        schema = self.read_output_schema(name=name)
        result: list[Union[TextContent, ImageContent, EmbeddedResource]] = [
            TextContent(
                type="text",
                text=f"Output variables of API response for {name} tool",
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{name}_output_schema"),
                    mimeType="plain/text",
                    text=json.dumps(schema),
                ),
            ),
            TextContent(
                type="text",
                text=f"Summary of unique entries across API response for {name} tool",
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{name}"),
                    mimeType="plain/text",
                    text=json.dumps(summary),
                ),
            ),
        ]
        self._cache[name]["responses"].append(
            result
        )  # Ensure type matches cache definition
        return result

    @log_call
    async def create_plot(
        self, data: list[Dict[str, Any]], arguments: Dict[str, Any]
    ) -> list[Union[TextContent, ImageContent]]:
        """
        Create a matplotlib plot of a particular category over time.

        Imaged returned as a base64 encoded JPG image.

        Parameters
        ----------
            data (list[Dict[str, Any]]): The input data returned from API query.
            y_variable (str): The variable to use as the y-axis in the plot.

        Returns
        -------
            str: The JPG image of the plot as a base64 encoded string.
        """
        if not data:
            raise ValueError("Data cannot be empty.")
        if not arguments:
            raise ValueError("Arguments cannot be empty.")
        if not arguments["plot_type"] == "map":
            raise ValueError("Plot type cannot be anything but map right now.")
        plot_result = await generate_map(
            data=data,
            colour_by=arguments["colour_by"],
        )
        result: list[Union[TextContent, ImageContent]] = [
            TextContent(
                type="text",
                text=f"Map of {arguments['tool_name']} data coloured by {arguments['colour_by']}.",
            ),
            ImageContent(type="image", data=plot_result, mimeType="image/jpeg"),
        ]
        self._cache[arguments["tool_name"]]["maps"].append(result)
        return result

    @log_call
    async def check_reference_material(
        self, arguments: Dict[str, Any]
    ) -> list[TextContent]:
        """Check references using a sql_query."""
        if not arguments:
            raise ValueError("Arguments cannot be empty.")
        if not arguments["sql_query"]:
            raise ValueError("SQL query cannot be empty.")
        sql_query = arguments["sql_query"]
        logger.info(f"Checking references with SQL query: {sql_query}")
        result: list[TextContent] = [
            TextContent(
                type="text",
                text=self.read_ancillary_file(sql_query=sql_query),
            )
        ]
        self._cache[NPNTools.CheckReferenceMaterial.name]["responses"].append(result)
        return result

    async def _get_last_raw_data(self, name: str) -> list[Dict[str, Any]]:
        """Get the last raw data for a specific tool name."""
        logger.info(f"Getting last raw data for {name}.")
        if name not in self._cache:
            raise ValueError(f"Tool not in cache: {name}")
        if "raw" not in self._cache[name]:
            raise ValueError(f"No cached response found for {name}")
        if not self._cache[name]["raw"]:
            raise ValueError(f"No raw data found for {name}")
        result: list[Dict[str, Any]] = self._cache[name]["raw"][-1:]
        return result

    async def get_cached(
        self, name: str
    ) -> list[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get the cached response for a specific tool name."""
        logger.info(f"Getting cached response for {name}.")
        if name not in self._cache:
            raise ValueError(f"Tool not in cache: {name}")
        if "responses" not in self._cache[name]:
            raise ValueError(f"No cached response found for {name}")
        last_resource = self._cache[name]["responses"][-1]
        contents: list[Union[TextContent, ImageContent, EmbeddedResource]] = []
        for item in last_resource:
            if isinstance(item, ImageContent):
                contents.append(
                    EmbeddedResource(
                        type="resource",
                        resource=BlobResourceContents(
                            uri=AnyUrl(f"npn-mcp://{name}"),
                            mimeType=item.mimeType,
                            blob=item.data,
                        ),
                    )
                )
            elif isinstance(item, TextContent):
                contents.append(
                    TextContent(
                        type="text",
                        text=item.text,
                    )
                )
            elif isinstance(item, EmbeddedResource):
                contents.append(item)
        return contents  # Ensure return type matches function definition

    async def handle_call_tool(
        self, name: str, arguments: Union[Dict[str, str], None]
    ) -> Any:
        """Client can call this to use a tool."""
        logger.info(f"Calling tool {name} with parameters: {arguments}")
        if arguments is None:
            raise ValueError("Arguments cannot be None")
        result = None
        if name not in [tool.name for tool in self.get_tool_list()]:
            raise ValueError(f"Tool {name} not found.")
        tool = next(tool for tool in self.get_tool_list() if tool.name == name)
        if name == NPNTools.CheckReferenceMaterial.name:
            result = await self.check_reference_material(arguments)
        elif name == NPNTools.Mapping.name:
            data = await self._get_last_raw_data(name=arguments["tool_name"])
            if not data:
                raise ValueError(f"No data found for {name}")
            result = await self.create_plot(data, arguments)
        else:
            await self.query_api(tool.endpoint, arguments)
        if result:  # Return reference check or image if available
            return result
        # Otherwise return summary of response from valid query tool
        return self.query_response(name=name)
