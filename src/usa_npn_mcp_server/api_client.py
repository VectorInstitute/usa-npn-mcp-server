"""Module with supplementary functions/classes for the NPN MCP server."""

from __future__ import annotations

import logging
import traceback
from datetime import datetime
from functools import wraps
from types import TracebackType
from typing import Any, Dict, Optional, Type
from urllib.parse import urlencode

import httpx

from usa_npn_mcp_server.utils.endpoints import NPNTools
from usa_npn_mcp_server.utils.output_schema import API_SCHEMAS


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
    API_BASE_URL = "https://services.usanpn.org/npn_portal/observations"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=20.0, base_url=self.API_BASE_URL)
        self.obs_responses: list[list[Dict[str, Any]]] = []
        self.obs_com_responses: list[list[Dict[str, Any]]] = []
        self.mag_data_responses: list[list[Dict[str, Any]]] = []
        self.site_level_data_responses: list[list[Dict[str, Any]]] = []
        self.summarized_data_responses: list[list[Dict[str, Any]]] = []

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
            case NPNTools.Observations.endpoint:
                self.obs_responses.append(response)
            case NPNTools.ObservationComment.endpoint:
                self.obs_com_responses.append(response)
            case NPNTools.MagnitudeData.endpoint:
                self.mag_data_responses.append(response)
            case NPNTools.SiteLevelData.endpoint:
                self.site_level_data_responses.append(response)
            case NPNTools.SummarizedData.endpoint:
                self.summarized_data_responses.append(response)
        logger.info(f"Response stored for {endpoint}.")

    def read_last_response(self, name: str) -> Dict[str, Any]:
        """Get the last response from the API by tool name."""
        logger.info(f"Reading {name} resource")
        match name:
            case NPNTools.Observations.name:
                responses = self.obs_responses
            case NPNTools.ObservationComment.name:
                responses = self.obs_com_responses
            case NPNTools.MagnitudeData.name:
                responses = self.mag_data_responses
            case NPNTools.SiteLevelData.name:
                responses = self.site_level_data_responses
            case NPNTools.SummarizedData.name:
                responses = self.summarized_data_responses
        return {"result": responses[-1]} if responses else {"result": None}

    def read_output_schema(self, name: str) -> Dict[str, Any]:
        """Get the schema from the last API response by tool name."""
        logger.info(f"Reading {name} output_schema resource")
        match name:
            case NPNTools.Observations.name:
                responses = self.obs_responses
            case NPNTools.ObservationComment.name:
                responses = self.obs_com_responses
            case NPNTools.MagnitudeData.name:
                responses = self.mag_data_responses
            case NPNTools.SiteLevelData.name:
                responses = self.site_level_data_responses
            case NPNTools.SummarizedData.name:
                responses = self.summarized_data_responses
        if responses:
            # Get the full schema for the tool
            full_schema = API_SCHEMAS[name]["properties"]
            keys = [key for key, val in responses[-1][0].items() if val]
            select_schema = {
                key: full_schema[key] for key in keys if key in full_schema
            }
            logger.info(f"Output schema keys: {keys}")
        return {"result": select_schema} if responses else {"result": None}
