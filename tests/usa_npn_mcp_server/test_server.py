"""Test the query_api function in the usa_npn_mcp_server.api_client module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from usa_npn_mcp_server.api_client import APIClient
from usa_npn_mcp_server.server import _initialize_roots
from usa_npn_mcp_server.utils.endpoints import NPNTools


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_tool_integration(mocker):
    """Test the handle_call_tool function in the server."""
    mock_response = [{"elevation_in_meters": 1, "status": "active"}]
    mocker.patch(
        "usa_npn_mcp_server.api_client.APIClient._get",
        return_value=mock_response,
    )
    async with APIClient() as client:
        hash_id = await client.query_api(
            endpoint=NPNTools.StatusIntensity.endpoint,
            arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
        )
        response = client.summarize_response(hash_id=hash_id)
        assert "discrete" in response["result"]
        assert "status" in response["result"]["discrete"]
        assert "continuous" in response["result"]
        assert "elevation_in_meters" in response["result"]["continuous"]


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_reference_material_integration(mocker):
    """Test the query_reference_material function in the server."""
    mocker.patch(
        "usa_npn_mcp_server.api_client.APIClient.read_ancillary_file",
        return_value='[{"species_id": 1, "common_name": "Oak"}]',
    )
    async with APIClient() as client:
        result = await client.query_reference_material(
            arguments={"sql_query": "SELECT * FROM species WHERE species_id = 1"}
        )
        assert len(result) == 1
        assert "Oak" in result[0].text


class TestInitializeRoots:
    """Test suite for _initialize_roots function."""

    def test_initialize_roots_with_dirs_parameter(self):
        """Test initialization with directories passed as parameters."""
        with (
            tempfile.TemporaryDirectory() as temp_dir1,
            tempfile.TemporaryDirectory() as temp_dir2,
        ):
            api_client = MagicMock()
            allowed_dirs = (temp_dir1, temp_dir2)

            _initialize_roots(allowed_dirs, api_client)

            # Check that update_allowed_roots was called
            api_client.update_allowed_roots.assert_called_once()

            # Get the roots that were passed
            roots = api_client.update_allowed_roots.call_args[0][0]
            assert len(roots) == 2

            # Check first root
            assert str(roots[0].uri) == f"file://{os.path.abspath(temp_dir1)}"
            assert roots[0].name == os.path.basename(temp_dir1)

            # Check second root
            assert str(roots[1].uri) == f"file://{os.path.abspath(temp_dir2)}"
            assert roots[1].name == os.path.basename(temp_dir2)

    def test_initialize_roots_with_environment_variable(self):
        """Test initialization with directories from environment variable."""
        with (
            tempfile.TemporaryDirectory() as temp_dir1,
            tempfile.TemporaryDirectory() as temp_dir2,
        ):
            api_client = MagicMock()
            env_value = f"{temp_dir1}{os.pathsep}{temp_dir2}"

            with patch.dict(os.environ, {"NPN_MCP_ALLOWED_DIRS": env_value}):
                _initialize_roots((), api_client)

            # Check that update_allowed_roots was called
            api_client.update_allowed_roots.assert_called_once()

            # Get the roots that were passed
            roots = api_client.update_allowed_roots.call_args[0][0]
            assert len(roots) == 2

    def test_initialize_roots_with_nonexistent_directory(self):
        """Test initialization with non-existent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api_client = MagicMock()
            allowed_dirs = (temp_dir, "/nonexistent/path/that/should/not/exist")

            _initialize_roots(allowed_dirs, api_client)

            # Should only have one valid root
            api_client.update_allowed_roots.assert_called_once()
            roots = api_client.update_allowed_roots.call_args[0][0]
            assert len(roots) == 1
            assert str(roots[0].uri) == f"file://{os.path.abspath(temp_dir)}"

    def test_initialize_roots_with_root_directory(self):
        """Test initialization with root directory (basename is empty)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api_client = MagicMock()

            # Store the actual basename before mocking
            temp_dir_basename = os.path.basename(temp_dir)

            # We'll patch os.path.basename to simulate root directories
            with patch("usa_npn_mcp_server.server.os.path.basename") as mock_basename:
                # Configure the mock to return specific values for each call
                mock_basename.side_effect = (
                    lambda x: "" if x == "/" else temp_dir_basename
                )

                allowed_dirs = ("/", temp_dir)

                # Also patch os.path.exists to return True
                with patch("usa_npn_mcp_server.server.os.path.exists") as mock_exists:
                    mock_exists.return_value = True

                    _initialize_roots(allowed_dirs, api_client)

                    api_client.update_allowed_roots.assert_called_once()
                    roots = api_client.update_allowed_roots.call_args[0][0]
                    assert len(roots) == 2

                    # First root should have indexed name
                    assert roots[0].name == "Root_0"
                    # Second root should have normal basename
                    assert roots[1].name == temp_dir_basename

    def test_initialize_roots_multiple_root_directories(self):
        """Test that multiple root directories get unique indexed names."""
        api_client = MagicMock()

        # We'll patch os.path.basename to simulate root directories
        with patch("usa_npn_mcp_server.server.os.path.basename") as mock_basename:
            mock_basename.return_value = ""  # Always return empty (root directory)

            allowed_dirs = ("/", "/mnt", "/opt")

            # Also patch os.path.exists to return True for our fake paths
            with patch("usa_npn_mcp_server.server.os.path.exists") as mock_exists:
                mock_exists.return_value = True

                _initialize_roots(allowed_dirs, api_client)

                api_client.update_allowed_roots.assert_called_once()
                roots = api_client.update_allowed_roots.call_args[0][0]
                assert len(roots) == 3

                # Check that each root has a unique indexed name
                assert roots[0].name == "Root_0"
                assert roots[1].name == "Root_1"
                assert roots[2].name == "Root_2"

    def test_initialize_roots_no_directories(self):
        """Test initialization with no directories."""
        api_client = MagicMock()

        _initialize_roots((), api_client)

        # update_allowed_roots should not be called
        api_client.update_allowed_roots.assert_not_called()

    def test_initialize_roots_all_nonexistent(self):
        """Test initialization when all provided directories don't exist."""
        api_client = MagicMock()
        allowed_dirs = ("/fake/dir1", "/fake/dir2", "/fake/dir3")

        _initialize_roots(allowed_dirs, api_client)

        # update_allowed_roots should not be called since no valid directories
        api_client.update_allowed_roots.assert_not_called()

    def test_initialize_roots_params_override_env(self):
        """Test that parameters override environment variable."""
        with (
            tempfile.TemporaryDirectory() as param_dir,
            tempfile.TemporaryDirectory() as env_dir,
        ):
            api_client = MagicMock()

            # Set environment variable
            with patch.dict(os.environ, {"NPN_MCP_ALLOWED_DIRS": env_dir}):
                # Pass directory via parameter
                _initialize_roots((param_dir,), api_client)

            # Should use parameter, not environment
            api_client.update_allowed_roots.assert_called_once()
            roots = api_client.update_allowed_roots.call_args[0][0]
            assert len(roots) == 1
            assert str(roots[0].uri) == f"file://{os.path.abspath(param_dir)}"

    def test_initialize_roots_mixed_paths(self):
        """Test with a mix of absolute and relative paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)

            # Save current directory
            original_cwd = os.getcwd()
            try:
                # Change to temp_dir to test relative paths
                os.chdir(temp_dir)

                api_client = MagicMock()
                # Mix of absolute and relative paths
                allowed_dirs = (temp_dir, "subdir", os.path.abspath(subdir))

                _initialize_roots(allowed_dirs, api_client)

                api_client.update_allowed_roots.assert_called_once()
                roots = api_client.update_allowed_roots.call_args[0][0]

                # Should have 3 roots (temp_dir, relative subdir, absolute subdir)
                assert len(roots) == 3

                # All should resolve to valid absolute paths
                for root in roots:
                    assert str(root.uri).startswith("file://")
                    path = str(root.uri)[7:]  # Remove file://
                    assert os.path.isabs(path)
                    assert os.path.exists(path)

            finally:
                os.chdir(original_cwd)
