"""Module with supplementary functions/classes for the NPN MCP server."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import sys
import traceback
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from statistics import mean, median
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union
from urllib.parse import urlencode

import httpx
import numpy as np
import pandas as pd
from mcp.types import (
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


class CacheManager:
    """Manages hash-based caching with size and time limits.

    Default is 100 mb and 15 mins.
    """

    def __init__(self, max_size_mb: int = 100, max_age_minutes: int = 15):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age = timedelta(minutes=max_age_minutes)

    def generate_hash(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate MD5 hash from tool name and parameters."""
        # Create consistent hash from tool name + sorted params
        content = f"{tool_name}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def add_entry(
        self,
        hash_id: str,
        tool_name: str,
        params: Dict[str, Any],
        raw_data: list[Dict[str, Any]],
    ) -> None:
        """Add new cache entry with metadata."""
        data_size = sys.getsizeof(json.dumps(raw_data))

        entry = {
            "raw_data": raw_data,
            "metadata": {
                "tool_name": tool_name,
                "params": params,
                "timestamp": datetime.now(),
                "size_bytes": data_size,
                "record_count": len(raw_data),
            },
        }

        self.cache[hash_id] = entry
        self.cleanup_cache()

    def get_entry(self, hash_id: str) -> Optional[Dict[str, Any]]:
        """Get cache entry if it exists and hasn't expired."""
        if hash_id not in self.cache:
            return None

        entry = self.cache[hash_id]
        if datetime.now() - entry["metadata"]["timestamp"] > self.max_age:
            del self.cache[hash_id]
            return None

        return entry

    def cleanup_cache(self) -> None:
        """Remove expired entries and enforce size limits."""
        now = datetime.now()

        # Remove expired entries
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if now - entry["metadata"]["timestamp"] > self.max_age
        ]
        for key in expired_keys:
            del self.cache[key]

        # Check total size and remove oldest if necessary
        while self.get_total_size() > self.max_size_bytes and self.cache:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["metadata"]["timestamp"],
            )
            del self.cache[oldest_key]

    def get_total_size(self) -> int:
        """Get total cache size in bytes."""
        return sum(entry["metadata"]["size_bytes"] for entry in self.cache.values())

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for the recent-queries resource."""
        entries_list: List[Dict[str, Any]] = []

        for hash_id, entry in self.cache.items():
            metadata = entry["metadata"]
            entries_list.append(
                {
                    "hash_id": hash_id,
                    "tool_name": metadata["tool_name"],
                    "timestamp": metadata["timestamp"].isoformat(),
                    "record_count": metadata["record_count"],
                    "size_kb": round(metadata["size_bytes"] / 1024, 2),
                    "params_summary": {
                        k: v
                        for k, v in metadata["params"].items()
                        if k in ["start_date", "end_date", "species_id", "state"]
                    },
                }
            )

        # Sort by timestamp, newest first
        entries_list.sort(key=lambda x: x["timestamp"], reverse=True)

        stats: Dict[str, Any] = {
            "total_entries": len(self.cache),
            "total_size_mb": round(self.get_total_size() / (1024 * 1024), 2),
            "entries": entries_list,
        }
        return stats


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
            NPNTools.GetRawData,
            NPNTools.ExportRawData,
            NPNTools.EnableFileExport,
        ]
        self.cache_manager = CacheManager()
        self.export_directory: Optional[str] = None
        self.export_enabled = False

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
        # Restructure query params containing comma-separated lists
        for key, value in list(params.items()):
            if isinstance(value, str) and "," in value:
                elements = value.strip("[]").split(",")
                del params[key]
                for idx, element in enumerate(elements):
                    params[f"{key}[{idx}]"] = element
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

    async def query_api(self, endpoint: str, arguments: Dict[str, Any]) -> str:
        """
        Query the API and store the response with hash-based caching.

        Parameters
        ----------
            endpoint (str): The API endpoint to query.
            arguments (Dict[str, Any]): The arguments to pass to the API.

        Returns
        -------
            str: The hash ID of the cached response.
        """
        name = next(
            (tool.name for tool in self._tool_list if tool.endpoint == endpoint), None
        )
        if not name:
            raise ValueError(f"No matching tool name found for endpoint: {endpoint}")

        response = await self._get(endpoint, params=arguments)

        # Generate hash and store in new cache system
        hash_id = self.cache_manager.generate_hash(name, arguments)
        self.cache_manager.add_entry(hash_id, name, arguments, response)

        logger.info(f"Response stored for {name} with hash ID: {hash_id}")
        return hash_id

    def summarize_response(self, hash_id: str) -> Dict[str, Any]:
        """Get unique variables and entries from cached API response by hash ID."""
        logger.info(f"Summarizing response for hash ID: {hash_id}")

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        raw_data = entry["raw_data"]
        if not raw_data:
            return {"result": None}

        unique_keys_summary, full_dataset = self._collect_unique_keys(raw_data)
        discrete_summary, continuous_summary, only_null = self._process_unique_values(
            unique_keys_summary, full_dataset
        )

        summary: dict[str, Any] = {
            "discrete": {
                key: val
                for key, val in discrete_summary.items()
                if key not in continuous_summary and key not in only_null
            },
            "continuous": continuous_summary,
            "only_null": only_null,
        }
        return {"result": summary}

    def _collect_unique_keys(
        self, raw_data: list[Dict[str, Any]]
    ) -> tuple[Dict[str, set[Any]], Dict[str, list[Any]]]:
        """Collect unique keys and their values from raw data."""
        unique_keys_summary: Dict[str, set[Any]] = {}
        full_dataset: Dict[str, list[Any]] = {}

        for entry_data in raw_data:
            if isinstance(entry_data, dict):
                for key, value in entry_data.items():
                    if key not in unique_keys_summary:
                        unique_keys_summary[key] = set()
                        full_dataset[key] = []
                    unique_keys_summary[key].add(value)
                    full_dataset[key].append(value)

        return unique_keys_summary, full_dataset

    def _process_unique_values(
        self,
        unique_keys_summary: Dict[str, set[Any]],
        full_dataset: Dict[str, list[Any]],
    ) -> tuple[Dict[str, Any], Dict[str, Dict[str, float]], List[str]]:
        """Process unique values into discrete and continuous summaries."""
        discrete_summary: Dict[str, Any] = {}
        continuous_summary: Dict[str, Dict[str, float]] = {}
        only_null: List[str] = []

        id_like_variables = [
            "observation_id",
            "individual_id",
            "station_id",
            "site_id",
            "species_id",
            "phenophase_id",
            "dataset_id",
            "network_id",
        ]
        int_encoded = ["phenophase_status", "patch", "itis_number", "year"]
        continuous = [
            "elevation_in_meters",
            "mean_first_yes_year",
            "mean_first_yes_doy",
            "mean_first_yes_julian_date",
            "se_first_yes_in_days",
            "mean_numdays_since_prior_no",
            "se_numdays_since_prior_no",
            "mean_last_yes_year",
            "mean_last_yes_doy",
            "mean_last_yes_julian_date",
            "se_last_yes_in_days",
            "mean_numdays_until_next_no",
            "se_numdays_until_next_no",
        ]

        for key, values in unique_keys_summary.items():
            if values == {-9999}:
                only_null.append(key)
            elif key in id_like_variables:
                self._process_id_like_variables(key, values, discrete_summary)
            elif "_id" in key or key in int_encoded:
                discrete_summary[key] = list(values)
            elif key in continuous or all(
                isinstance(v, (int, float)) and v != -9999 for v in values
            ):
                self._process_continuous_variables(
                    key, full_dataset, continuous_summary
                )
            else:
                discrete_summary[key] = list(values)

        return discrete_summary, continuous_summary, only_null

    def _process_id_like_variables(
        self, key: str, values: set[Any], discrete_summary: Dict[str, Any]
    ) -> None:
        """Process ID-like variables for truncation."""
        values_list = list(values)
        if len(values_list) > 15:
            discrete_summary[key] = {
                "sample": values_list[:15],
                "total_count": len(values_list),
                "truncated": True,
                "message": f"Showing first 15 of {len(values_list)} unique values",
            }
        else:
            discrete_summary[key] = values_list

    def _process_continuous_variables(
        self,
        key: str,
        full_dataset: Dict[str, list[Any]],
        continuous_summary: Dict[str, Dict[str, float]],
    ) -> None:
        """Process continuous variables for statistical summaries."""
        values_list = [v for v in full_dataset[key] if v != -9999]
        if values_list:
            continuous_summary[key] = {
                "length": len(values_list),
                "min": min(values_list),
                "max": max(values_list),
                "mean": mean(values_list),
                "median": median(values_list),
                "1st_quartile": np.percentile(values_list, 25),
                "3rd_quartile": np.percentile(values_list, 75),
            }

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

    def read_output_schema(self, hash_id: str) -> Dict[str, Any]:
        """Get the schema from cached API response by hash ID."""
        logger.info(f"Reading output schema for hash ID: {hash_id}")

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        tool_name = entry["metadata"]["tool_name"]
        raw_data = entry["raw_data"]

        if not raw_data:
            return {"result": None}

        # Get the full schema for the tool
        full_schema = API_SCHEMAS[tool_name]["properties"]

        if isinstance(raw_data[0], dict):
            keys = [key for key, val in raw_data[0].items() if val]
        else:
            keys = []

        select_schema = {key: full_schema[key] for key in keys if key in full_schema}
        logger.info(f"Output schema keys: {keys}")
        return {"result": select_schema} if select_schema else {"result": None}

    def query_response(
        self, hash_id: str
    ) -> list[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get the Server response by query hash ID."""
        logger.info(f"Returning query response for hash ID: {hash_id}")

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        tool_name = entry["metadata"]["tool_name"]
        summary = self.summarize_response(hash_id=hash_id)
        schema = self.read_output_schema(hash_id=hash_id)

        result: list[Union[TextContent, ImageContent, EmbeddedResource]] = [
            TextContent(
                type="text",
                text=f"Output variables of API response for {tool_name} tool (Hash: {hash_id})",
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{tool_name}_output_schema"),
                    mimeType="plain/text",
                    text=json.dumps(schema),
                ),
            ),
            TextContent(
                type="text",
                text=f"Summary of unique entries across API response for {tool_name} tool",
            ),
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=AnyUrl(f"npn-mcp://{tool_name}"),
                    mimeType="plain/text",
                    text=json.dumps(summary),
                ),
            ),
        ]

        return result

    async def get_raw_data(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get raw data from cache with size limits."""
        hash_id = arguments["hash_id"]

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        raw_data = entry["raw_data"]
        metadata = entry["metadata"]

        # Apply 10K record limit
        if len(raw_data) > 10000:
            truncated_data = raw_data[:10000]
            result = [
                TextContent(
                    type="text",
                    text=f"Raw data for {metadata['tool_name']} (TRUNCATED)",
                ),
                TextContent(
                    type="text",
                    text=f"Warning: Data truncated to 10,000 records out of {len(raw_data)} total records.",
                ),
                TextContent(
                    type="text",
                    text=json.dumps(truncated_data, indent=2),
                ),
            ]
        else:
            result = [
                TextContent(
                    type="text",
                    text=f"Raw data for {metadata['tool_name']} ({len(raw_data)} records)",
                ),
                TextContent(
                    type="text",
                    text=json.dumps(raw_data, indent=2),
                ),
            ]

        return result

    async def enable_file_export(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Enable file export functionality."""
        export_dir = arguments.get("export_directory")

        # Use current working directory if not provided
        if export_dir is None:
            export_dir = os.getcwd()

        # Validate directory exists or can be created
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir, exist_ok=True)
            except Exception as e:
                raise ValueError(
                    f"Cannot create export directory {export_dir}: {str(e)}"
                ) from e

        self.export_directory = export_dir
        self.export_enabled = True

        return [
            TextContent(
                type="text",
                text=f"File export enabled. Export directory set to: {export_dir}",
            )
        ]

    @log_call
    async def export_raw_data(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Export raw data to file."""
        import os  # Import here to avoid formatter removal

        if not self.export_enabled:
            raise ValueError(
                "File export not enabled. Use 'enable-file-export' tool first."
            )

        hash_id = arguments["hash_id"]
        file_format = arguments["file_format"]
        filename = arguments.get("filename")

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        raw_data = entry["raw_data"]
        metadata = entry["metadata"]

        # Generate filename if not provided
        if not filename:
            timestamp = metadata["timestamp"].strftime("%Y%m%d_%H%M%S")
            filename = (
                f"{metadata['tool_name']}_{hash_id[:8]}_{timestamp}.{file_format}"
            )

        if self.export_directory is None:
            raise ValueError("Export directory not set")
        filepath = os.path.join(self.export_directory, filename)

        try:
            with open(filepath, "w") as f:
                if file_format == "json":
                    json.dump(raw_data, f, indent=2)
                else:  # jsonl
                    for record in raw_data:
                        f.write(json.dumps(record) + "\n")

            return [
                TextContent(
                    type="text",
                    text=f"Successfully exported {len(raw_data)} records to: {filepath}",
                )
            ]
        except Exception as e:
            raise ValueError(f"Failed to export data: {str(e)}") from e

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
        # Note: Maps are no longer cached in the old system, are generated on-demand
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
        # Note: Reference material results are returned directly, not cached
        return result

    async def handle_call_tool(
        self, name: str, arguments: Union[Dict[str, str], None]
    ) -> Any:
        """Client can call this to use a tool."""
        logger.info(f"Calling tool {name} with parameters: {arguments}")
        if arguments is None:
            raise ValueError("Arguments cannot be None")

        if name not in [tool.name for tool in self.get_tool_list()]:
            raise ValueError(f"Tool {name} not found.")

        if name in [
            NPNTools.CheckReferenceMaterial.name,
            NPNTools.GetRawData.name,
            NPNTools.ExportRawData.name,
            NPNTools.EnableFileExport.name,
            NPNTools.Mapping.name,
        ]:
            return await self._handle_special_tools(name, arguments)

        # Regular API query tools - return hash ID
        return await self._handle_regular_tool(name, arguments)

    async def _handle_special_tools(self, name: str, arguments: Dict[str, str]) -> Any:
        """Handle special tools with unique logic."""
        if name == NPNTools.CheckReferenceMaterial.name:
            return await self.check_reference_material(arguments)
        if name == NPNTools.GetRawData.name:
            return await self.get_raw_data(arguments)
        if name == NPNTools.ExportRawData.name:
            return await self.export_raw_data(arguments)
        if name == NPNTools.EnableFileExport.name:
            return await self.enable_file_export(arguments)
        if name == NPNTools.Mapping.name:
            return await self._handle_mapping_tool(arguments)

        raise ValueError(f"No result generated for tool: {name}")

    async def _handle_mapping_tool(self, arguments: Dict[str, str]) -> Any:
        """Handle the Mapping tool."""
        hash_id = arguments.get("hash_id")
        if not hash_id:
            raise ValueError(
                "Mapping tool now requires hash_id parameter from cached query"
            )

        entry = self.cache_manager.get_entry(hash_id)
        if not entry:
            raise ValueError(f"No cached data found for hash ID: {hash_id}")

        data = entry["raw_data"]
        return await self.create_plot(data, arguments)

    async def _handle_regular_tool(self, name: str, arguments: Dict[str, str]) -> Any:
        """Handle regular API query tools."""
        tool = next(tool for tool in self.get_tool_list() if tool.name == name)
        hash_id = await self.query_api(tool.endpoint, arguments)
        return self.query_response(hash_id=hash_id)
