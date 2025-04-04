"""Module with supplementary functions/classes for the NPN MCP server."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime
from functools import wraps
from types import TracebackType
from typing import Any, Dict, Optional, Type
from urllib.parse import urlencode

import httpx
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    TextResourceContents,
)
from pydantic import AnyUrl

from usa_npn_mcp_server.utils.endpoints import NPNTools
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
    _cache: dict[str, list[str]] = {}

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=20.0, base_url=self.API_BASE_URL)
        self.status_intensity_responses: list[list[Dict[str, Any]]] = []
        self.observation_comment_responses: list[list[Dict[str, Any]]] = []
        self.magnitude_phenometrics_responses: list[list[Dict[str, Any]]] = []
        self.site_phenometrics_responses: list[list[Dict[str, Any]]] = []
        self.individual_phenometrics_responses: list[list[Dict[str, Any]]] = []

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
        response = await self._get(endpoint, params=arguments)
        match endpoint:
            case NPNTools.StatusIntensity.endpoint:
                self.status_intensity_responses.append(response)
            case NPNTools.ObservationComment.endpoint:
                self.observation_comment_responses.append(response)
            case NPNTools.MagnitudePhenometrics.endpoint:
                self.magnitude_phenometrics_responses.append(response)
            case NPNTools.SitePhenometrics.endpoint:
                self.site_phenometrics_responses.append(response)
            case NPNTools.IndividualPhenometrics.endpoint:
                self.individual_phenometrics_responses.append(response)
        logger.info(f"Response stored for {endpoint}.")

    def read_last_response(self, name: str) -> Dict[str, Any]:
        """Get the last response from the API by tool name."""
        logger.info(f"Reading {name} resource")
        match name:
            case NPNTools.StatusIntensity.name:
                responses = self.status_intensity_responses
            case NPNTools.ObservationComment.name:
                responses = self.observation_comment_responses
            case NPNTools.MagnitudePhenometrics.name:
                responses = self.magnitude_phenometrics_responses
            case NPNTools.SitePhenometrics.name:
                responses = self.site_phenometrics_responses
            case NPNTools.IndividualPhenometrics.name:
                responses = self.individual_phenometrics_responses
        return {"result": responses[-1]} if responses else {"result": None}

    def summarize_response(self, name: str) -> Dict[str, Any]:
        """Get unique variables and entries from last API response by tool name."""
        logger.info(f"Summarizing {name} response")
        match name:
            case NPNTools.StatusIntensity.name:
                responses = self.status_intensity_responses
            case NPNTools.ObservationComment.name:
                responses = self.observation_comment_responses
            case NPNTools.MagnitudePhenometrics.name:
                responses = self.magnitude_phenometrics_responses
            case NPNTools.SitePhenometrics.name:
                responses = self.site_phenometrics_responses
            case NPNTools.IndividualPhenometrics.name:
                responses = self.individual_phenometrics_responses

        if not responses:
            return {"result": None}

        last_response = responses[-1]
        unique_keys_summary: dict[str, set[str]] = {}
        # Collect unique keys and their values
        for entry in last_response:
            for key, value in entry.items():
                if key not in unique_keys_summary:
                    unique_keys_summary[key] = set()
                unique_keys_summary[key].add(value)
        # Convert sets to lists for JSON serialization compatibility
        summary: dict[str, list[str]] = {}
        for key, val in unique_keys_summary.items():
            summary[key] = list(val)
        return {"result": summary}

    def read_output_schema(self, name: str) -> Dict[str, Any]:
        """Get the schema from the last API response by tool name."""
        logger.info(f"Reading {name} output_schema resource")
        responses = []
        match name:
            case NPNTools.StatusIntensity.name:
                responses = self.status_intensity_responses
            case NPNTools.ObservationComment.name:
                responses = self.observation_comment_responses
            case NPNTools.MagnitudePhenometrics.name:
                responses = self.magnitude_phenometrics_responses
            case NPNTools.SitePhenometrics.name:
                responses = self.site_phenometrics_responses
            case NPNTools.IndividualPhenometrics.name:
                responses = self.individual_phenometrics_responses
        if responses[-1]:
            # Get the full schema for the tool
            full_schema = API_SCHEMAS[name]["properties"]
            keys = [key for key, val in responses[-1][0].items() if val]
            select_schema = {
                key: full_schema[key] for key in keys if key in full_schema
            }
            logger.info(f"Output schema keys: {keys}")
        return {"result": select_schema} if responses[-1] else {"result": None}

    def query_response(
        self, name: str
    ) -> list[TextContent | ImageContent | EmbeddedResource]:
        """Get the Server response by query Tool name."""
        logger.info(f"Returning {name} query Tool response.")
        summary = self.summarize_response(name=name)
        schema = self.read_output_schema(name=name)
        result: list[TextContent | ImageContent | EmbeddedResource] = [
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
        return result

    @log_call
    async def create_plot(
        self, data: list[Dict[str, Any]], arguments: Dict[str, Any]
    ) -> str:
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
        return generate_map(
            data=data,
            colour_by=arguments["colour_by"],
        )
