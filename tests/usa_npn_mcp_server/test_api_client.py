"""Unit tests for APIClient core methods."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
from mcp.types import EmbeddedResource, TextContent

from usa_npn_mcp_server.api_client import APIClient


class TestAPIClientCoreMethods:
    """Test suite for APIClient core data processing methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_client = APIClient()
        self.sample_data = [
            {
                "observation_id": 1,
                "individual_id": 101,
                "species_id": 3,
                "elevation_in_meters": 1200.5,
                "phenophase_status": 1,
                "status": "active",
                "observation_date": "2025-01-15",
                "year": 2025,
                "patch": 1,
                "comments": "Healthy growth",
                "network_id": 1,
                "station_id": 201,
            },
            {
                "observation_id": 2,
                "individual_id": 102,
                "species_id": 3,
                "elevation_in_meters": 1150.0,
                "phenophase_status": 0,
                "status": "inactive",
                "observation_date": "2025-01-16",
                "year": 2025,
                "patch": 2,
                "comments": None,
                "network_id": 1,
                "station_id": 202,
            },
            {
                "observation_id": 3,
                "individual_id": 103,
                "species_id": 4,
                "elevation_in_meters": 1300.75,
                "phenophase_status": 1,
                "status": "active",
                "observation_date": "2025-01-17",
                "year": 2025,
                "patch": 1,
                "comments": "Excellent condition",
                "network_id": 2,
                "station_id": 203,
            },
        ]

    def test_collect_unique_keys_basic(self):
        """Test basic unique key collection from data."""
        unique_keys, full_dataset = self.api_client._collect_unique_keys(
            self.sample_data
        )

        # Check all keys are present
        expected_keys = {
            "observation_id",
            "individual_id",
            "species_id",
            "elevation_in_meters",
            "phenophase_status",
            "status",
            "observation_date",
            "year",
            "patch",
            "comments",
            "network_id",
            "station_id",
        }
        assert set(unique_keys.keys()) == expected_keys

        # Check unique values collection
        assert unique_keys["species_id"] == {3, 4}
        assert unique_keys["status"] == {"active", "inactive"}
        assert unique_keys["patch"] == {1, 2}

        # Check full dataset collection
        assert len(full_dataset["observation_id"]) == 3
        assert full_dataset["observation_id"] == [1, 2, 3]
        assert full_dataset["elevation_in_meters"] == [1200.5, 1150.0, 1300.75]

    def test_collect_unique_keys_empty_data(self):
        """Test unique key collection with empty data."""
        unique_keys, full_dataset = self.api_client._collect_unique_keys([])

        assert unique_keys == {}
        assert full_dataset == {}

    def test_collect_unique_keys_with_nulls(self):
        """Test unique key collection with null values."""
        data_with_nulls = [
            {"id": 1, "name": "test1", "value": None},
            {"id": 2, "name": None, "value": 10},
            {"id": 3, "name": "test3", "value": 20},
        ]

        unique_keys, full_dataset = self.api_client._collect_unique_keys(
            data_with_nulls
        )

        assert unique_keys["name"] == {"test1", None, "test3"}
        assert unique_keys["value"] == {None, 10, 20}
        assert len(full_dataset["name"]) == 3

    def test_process_unique_values_basic(self):
        """Test processing unique values into discrete and continuous categories."""
        unique_keys, full_dataset = self.api_client._collect_unique_keys(
            self.sample_data
        )
        discrete, continuous, only_null = self.api_client._process_unique_values(
            unique_keys, full_dataset
        )

        # Check discrete variables
        assert "status" in discrete
        assert set(discrete["status"]) == {"active", "inactive"}  # Be order agnostic
        assert "observation_date" in discrete

        # Check continuous variables
        assert "elevation_in_meters" in continuous
        elevation_stats = continuous["elevation_in_meters"]
        assert elevation_stats["length"] == 3
        assert elevation_stats["min"] == 1150.0
        assert elevation_stats["max"] == 1300.75
        assert 1200 < elevation_stats["mean"] < 1250

        # Check ID-like variables processing
        assert "observation_id" in discrete
        if isinstance(discrete["observation_id"], dict):
            # Truncated format for many IDs
            assert "sample" in discrete["observation_id"]
            assert "total_count" in discrete["observation_id"]
        else:
            # List format for few IDs
            assert discrete["observation_id"] == [1, 2, 3]

    def test_process_unique_values_only_null(self):
        """Test processing values that are only -9999 (null indicator)."""
        data_with_null_only = [
            {"id": 1, "null_field": -9999},
            {"id": 2, "null_field": -9999},
        ]
        unique_keys, full_dataset = self.api_client._collect_unique_keys(
            data_with_null_only
        )
        discrete, continuous, only_null = self.api_client._process_unique_values(
            unique_keys, full_dataset
        )

        assert "null_field" in only_null
        assert "null_field" not in discrete
        assert "null_field" not in continuous

    def test_process_id_like_variables_small_set(self):
        """Test ID processing with small set of values."""
        discrete_summary = {}
        values = {1, 2, 3, 4}

        self.api_client._process_id_like_variables("test_id", values, discrete_summary)

        assert "test_id" in discrete_summary
        assert discrete_summary["test_id"] == [1, 2, 3, 4]

    def test_process_id_like_variables_large_set(self):
        """Test ID processing with large set of values (truncation)."""
        discrete_summary = {}
        values = set(range(1, 21))  # Too many values should trigger truncation

        self.api_client._process_id_like_variables("test_id", values, discrete_summary)

        assert "test_id" in discrete_summary
        result = discrete_summary["test_id"]
        assert isinstance(result, dict)
        assert "sample" in result
        assert "total_count" in result
        assert "truncated" in result
        assert result["total_count"] == 20
        assert result["truncated"] is True
        assert len(result["sample"]) == 15

    def test_process_continuous_variables_basic(self):
        """Test continuous variable processing."""
        full_dataset = {"elevation": [1000.0, 1200.5, 1150.0, 1300.75, 950.25]}
        continuous_summary = {}

        self.api_client._process_continuous_variables(
            "elevation", full_dataset, continuous_summary
        )

        assert "elevation" in continuous_summary
        stats = continuous_summary["elevation"]
        assert stats["length"] == 5
        assert stats["min"] == 950.25
        assert stats["max"] == 1300.75
        assert "mean" in stats
        assert "median" in stats
        assert "1st_quartile" in stats
        assert "3rd_quartile" in stats

    def test_process_continuous_variables_with_nulls(self):
        """Test continuous variable processing with -9999 null values."""
        full_dataset = {"elevation": [1000.0, -9999, 1200.5, -9999, 1150.0]}
        continuous_summary = {}

        self.api_client._process_continuous_variables(
            "elevation", full_dataset, continuous_summary
        )

        assert "elevation" in continuous_summary
        stats = continuous_summary["elevation"]
        assert stats["length"] == 3  # Only non-null values
        assert stats["min"] == 1000.0
        assert stats["max"] == 1200.5

    def test_process_continuous_variables_all_nulls(self):
        """Test continuous variable processing with all null values."""
        full_dataset = {"elevation": [-9999, -9999, -9999]}
        continuous_summary = {}

        self.api_client._process_continuous_variables(
            "elevation", full_dataset, continuous_summary
        )

        # Should not add to continuous_summary if all values are null
        assert "elevation" not in continuous_summary

    @pytest.mark.asyncio
    async def test_get_raw_data_basic(self):
        """Test basic raw data retrieval."""
        # Setup cache with test data
        hash_id = "test_hash_123"
        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {"start_date": "2025-01-01"}, self.sample_data
        )

        result = await self.api_client.get_raw_data({"hash_id": hash_id})

        assert len(result) == 2  # Title and data
        assert isinstance(result[0], TextContent)
        assert isinstance(result[1], TextContent)
        assert "status-intensity" in result[0].text
        assert "3 records" in result[0].text

        # Check that data is included
        data_content = json.loads(result[1].text)
        assert len(data_content) == 3
        assert data_content[0]["observation_id"] == 1

    @pytest.mark.asyncio
    async def test_get_raw_data_truncated(self):
        """Test raw data retrieval with truncation for large datasets."""
        # Create large dataset
        large_data = [{"id": i, "value": f"data_{i}"} for i in range(1500)]
        hash_id = "test_hash_large"

        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {"start_date": "2025-01-01"}, large_data
        )

        result = await self.api_client.get_raw_data({"hash_id": hash_id})

        assert len(result) == 3  # Title, warning, and truncated data
        assert "TRUNCATED" in result[0].text
        assert "1,000 records out of 1500" in result[1].text

        # Check truncation
        data_content = json.loads(result[2].text)
        assert len(data_content) == 1000

    @pytest.mark.asyncio
    async def test_get_raw_data_nonexistent_hash(self):
        """Test raw data retrieval with non-existent hash."""
        with pytest.raises(ValueError, match="No cached data found"):
            await self.api_client.get_raw_data({"hash_id": "nonexistent"})

    @pytest.mark.asyncio
    async def test_enable_file_export_default_directory(self):
        """Test enabling file export with default directory."""
        result = await self.api_client.enable_file_export({})

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "File export enabled" in result[0].text
        assert self.api_client.export_enabled is True
        assert self.api_client.export_directory is not None

    @pytest.mark.asyncio
    async def test_enable_file_export_custom_directory(self):
        """Test enabling file export with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await self.api_client.enable_file_export(
                {"export_directory": temp_dir}
            )

            assert self.api_client.export_directory == temp_dir
            assert self.api_client.export_enabled is True
            assert temp_dir in result[0].text

    @pytest.mark.asyncio
    async def test_enable_file_export_create_directory(self):
        """Test enabling file export creates non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_export_dir")

            await self.api_client.enable_file_export({"export_directory": new_dir})

            assert os.path.exists(new_dir)
            assert self.api_client.export_directory == new_dir

    @pytest.mark.asyncio
    async def test_export_raw_data_json(self):
        """Test exporting raw data as JSON."""
        # Setup
        with tempfile.TemporaryDirectory() as temp_dir:
            await self.api_client.enable_file_export({"export_directory": temp_dir})

            hash_id = "test_hash_export"
            self.api_client.cache_manager.add_entry(
                hash_id,
                "status-intensity",
                {"start_date": "2025-01-01"},
                self.sample_data,
            )

            result = await self.api_client.export_raw_data(
                {
                    "hash_id": hash_id,
                    "file_format": "json",
                    "filename": "test_export.json",
                }
            )

            # Check result
            assert len(result) == 1
            assert "Successfully exported 3 records" in result[0].text

            # Check file exists and content
            file_path = os.path.join(temp_dir, "test_export.json")
            assert os.path.exists(file_path)

            with open(file_path, "r") as f:
                exported_data = json.load(f)

            assert len(exported_data) == 3
            assert exported_data[0]["observation_id"] == 1

    @pytest.mark.asyncio
    async def test_export_raw_data_jsonl(self):
        """Test exporting raw data as JSONL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            await self.api_client.enable_file_export({"export_directory": temp_dir})

            hash_id = "test_hash_export"
            self.api_client.cache_manager.add_entry(
                hash_id,
                "status-intensity",
                {"start_date": "2025-01-01"},
                self.sample_data,
            )

            result = await self.api_client.export_raw_data(
                {"hash_id": hash_id, "file_format": "jsonl"}
            )

            # Check auto-generated filename
            assert "Successfully exported 3 records" in result[0].text

            # Find the exported file
            files = [f for f in os.listdir(temp_dir) if f.endswith(".jsonl")]
            assert len(files) == 1

            file_path = os.path.join(temp_dir, files[0])
            with open(file_path, "r") as f:
                lines = f.readlines()

            assert len(lines) == 3
            # Each line should be valid JSON
            for line in lines:
                data = json.loads(line.strip())
                assert "observation_id" in data

    @pytest.mark.asyncio
    async def test_export_raw_data_not_enabled(self):
        """Test exporting when file export is not enabled."""
        hash_id = "test_hash"
        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {}, self.sample_data
        )

        with pytest.raises(ValueError, match="File export not enabled"):
            await self.api_client.export_raw_data(
                {"hash_id": hash_id, "file_format": "json"}
            )

    @pytest.mark.asyncio
    async def test_export_raw_data_nonexistent_hash(self):
        """Test exporting with non-existent hash."""
        await self.api_client.enable_file_export({})

        with pytest.raises(ValueError, match="No cached data found"):
            await self.api_client.export_raw_data(
                {"hash_id": "nonexistent", "file_format": "json"}
            )

    def test_query_response_basic(self):
        """Test basic query response generation."""
        # Setup cache
        hash_id = "test_hash_query"
        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {"start_date": "2025-01-01"}, self.sample_data
        )

        with patch.object(self.api_client, "read_output_schema") as mock_schema:
            mock_schema.return_value = {
                "result": {"observation_id": {"type": "integer"}}
            }

            result = self.api_client.query_response(hash_id)

            assert len(result) == 4  # Description, schema, description, summary

            # Check text content
            assert isinstance(result[0], TextContent)
            assert "status-intensity" in result[0].text
            assert hash_id in result[0].text

            # Check embedded resources
            assert isinstance(result[1], EmbeddedResource)
            assert isinstance(result[3], EmbeddedResource)

    def test_query_response_nonexistent_hash(self):
        """Test query response with non-existent hash."""
        with pytest.raises(ValueError, match="No cached data found"):
            self.api_client.query_response("nonexistent_hash")

    @pytest.mark.asyncio
    async def test_handle_regular_tool(self):
        """Test regular tool handling."""
        tool_name = "status-intensity"
        arguments = {"start_date": "2025-01-01", "end_date": "2025-01-31"}

        with (
            patch.object(self.api_client, "query_api") as mock_query_api,
            patch.object(self.api_client, "query_response") as mock_query_response,
        ):
            mock_query_api.return_value = "test_hash_123"
            mock_query_response.return_value = [
                TextContent(type="text", text="Test response")
            ]

            result = await self.api_client._handle_regular_tool(tool_name, arguments)

            mock_query_api.assert_called_once_with("getObservations", arguments)
            mock_query_response.assert_called_once_with(hash_id="test_hash_123")
            assert result == [TextContent(type="text", text="Test response")]

    @pytest.mark.asyncio
    async def test_handle_special_tools_check_reference(self):
        """Test special tool handling for check-reference-material."""
        arguments = {"sql_query": "SELECT * FROM species"}

        with patch.object(self.api_client, "check_reference_material") as mock_check:
            mock_check.return_value = [TextContent(type="text", text="Reference data")]

            result = await self.api_client._handle_special_tools(
                "check-reference-material", arguments
            )

            mock_check.assert_called_once_with(arguments)
            assert result == [TextContent(type="text", text="Reference data")]

    @pytest.mark.asyncio
    async def test_handle_special_tools_get_raw_data(self):
        """Test special tool handling for get-raw-data."""
        arguments = {"hash_id": "test_hash"}

        with patch.object(self.api_client, "get_raw_data") as mock_get_raw:
            mock_get_raw.return_value = [TextContent(type="text", text="Raw data")]

            result = await self.api_client._handle_special_tools(
                "get-raw-data", arguments
            )

            mock_get_raw.assert_called_once_with(arguments)
            assert result == [TextContent(type="text", text="Raw data")]

    @pytest.mark.asyncio
    async def test_handle_special_tools_export_data(self):
        """Test special tool handling for export-raw-data."""
        arguments = {"hash_id": "test_hash", "file_format": "json"}

        with patch.object(self.api_client, "export_raw_data") as mock_export:
            mock_export.return_value = [
                TextContent(type="text", text="Export complete")
            ]

            result = await self.api_client._handle_special_tools(
                "export-raw-data", arguments
            )

            mock_export.assert_called_once_with(arguments)
            assert result == [TextContent(type="text", text="Export complete")]

    @pytest.mark.asyncio
    async def test_handle_special_tools_enable_export(self):
        """Test special tool handling for enable-file-export."""
        arguments = {"export_directory": "/tmp/exports"}

        with patch.object(self.api_client, "enable_file_export") as mock_enable:
            mock_enable.return_value = [TextContent(type="text", text="Export enabled")]

            result = await self.api_client._handle_special_tools(
                "enable-file-export", arguments
            )

            mock_enable.assert_called_once_with(arguments)
            assert result == [TextContent(type="text", text="Export enabled")]

    @pytest.mark.asyncio
    async def test_handle_mapping_tool_basic(self):
        """Test mapping tool handling."""
        # Setup cache with test data
        hash_id = "test_mapping_hash"
        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {}, self.sample_data
        )

        arguments = {
            "hash_id": hash_id,
            "plot_type": "map",
            "colour_by": "elevation_in_meters",
            "tool_name": "status-intensity",
        }

        with patch.object(self.api_client, "create_plot") as mock_create_plot:
            mock_create_plot.return_value = [
                TextContent(type="text", text="Plot created")
            ]

            result = await self.api_client._handle_mapping_tool(arguments)

            mock_create_plot.assert_called_once_with(self.sample_data, arguments)
            assert result == [TextContent(type="text", text="Plot created")]

    @pytest.mark.asyncio
    async def test_handle_mapping_tool_no_hash_id(self):
        """Test mapping tool handling without hash_id."""
        arguments = {"plot_type": "map", "colour_by": "elevation"}

        with pytest.raises(
            ValueError, match="Mapping tool now requires hash_id parameter"
        ):
            await self.api_client._handle_mapping_tool(arguments)

    @pytest.mark.asyncio
    async def test_handle_mapping_tool_invalid_hash(self):
        """Test mapping tool handling with invalid hash_id."""
        arguments = {"hash_id": "nonexistent", "plot_type": "map"}

        with pytest.raises(ValueError, match="No cached data found"):
            await self.api_client._handle_mapping_tool(arguments)

    def test_read_output_schema_basic(self):
        """Test reading output schema for cached data."""
        # Setup cache
        hash_id = "test_schema_hash"
        test_data = [{"observation_id": 1, "species_id": 3, "empty_field": None}]
        self.api_client.cache_manager.add_entry(
            hash_id, "status-intensity", {}, test_data
        )

        with patch("usa_npn_mcp_server.api_client.API_SCHEMAS") as mock_schemas:
            mock_schemas.__getitem__.return_value = {
                "properties": {
                    "observation_id": {"type": "integer", "description": "Unique ID"},
                    "species_id": {"type": "integer", "description": "Species ID"},
                    "empty_field": {"type": "string", "description": "Empty field"},
                    "missing_field": {"type": "string", "description": "Not in data"},
                }
            }

            result = self.api_client.read_output_schema(hash_id)

            # Should only include fields that have non-null values in data
            schema = result["result"]
            assert "observation_id" in schema
            assert "species_id" in schema
            assert "empty_field" not in schema  # Was null in data
            assert "missing_field" not in schema  # Not in data

    def test_read_output_schema_nonexistent_hash(self):
        """Test reading output schema with non-existent hash."""
        with pytest.raises(ValueError, match="No cached data found"):
            self.api_client.read_output_schema("nonexistent_hash")

    def test_read_output_schema_empty_data(self):
        """Test reading output schema with empty data."""
        hash_id = "test_empty_hash"
        self.api_client.cache_manager.add_entry(hash_id, "status-intensity", {}, [])

        result = self.api_client.read_output_schema(hash_id)
        assert result["result"] is None
