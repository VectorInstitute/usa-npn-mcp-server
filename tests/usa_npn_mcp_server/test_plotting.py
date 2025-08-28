"""Tests for the plotting.py module."""

import base64
import io
from unittest.mock import Mock, patch

import pytest

from usa_npn_mcp_server.utils.plotting import generate_map


class TestGenerateMap:
    """Test the generate_map function."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
            {"latitude": 40.7128, "longitude": -74.0060, "species": "Oak"},
            {"latitude": 34.0522, "longitude": -118.2437, "species": "Pine"},
            {"latitude": 41.8781, "longitude": -87.6298, "species": "Oak"},
        ]

    @pytest.fixture
    def mock_geopandas(self):
        """Mock geopandas and related dependencies."""
        with (
            patch("usa_npn_mcp_server.utils.plotting.gpd") as mock_gpd,
            patch("usa_npn_mcp_server.utils.plotting.plt") as mock_plt,
            patch("usa_npn_mcp_server.utils.plotting.Point") as mock_point,
        ):
            # Mock the US states data
            mock_us_states = Mock()
            mock_us_states.plot = Mock()
            mock_gpd.read_file.return_value = mock_us_states

            # Mock GeoDataFrame
            mock_gdf = Mock()
            mock_gdf.geometry = Mock()
            mock_gdf.geometry.x = Mock()
            mock_gdf.geometry.y = Mock()
            mock_gdf.geometry.x.min.return_value = -120
            mock_gdf.geometry.x.max.return_value = -70
            mock_gdf.geometry.y.min.return_value = 30
            mock_gdf.geometry.y.max.return_value = 45
            mock_gdf.plot = Mock()
            mock_gdf.__getitem__ = Mock(return_value=mock_gdf)
            mock_gpd.GeoDataFrame.return_value = mock_gdf

            # Mock matplotlib
            mock_ax = Mock()
            mock_fig = Mock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Mock the buffer for image saving
            mock_buffer = io.BytesIO(b"fake_image_data")

            with patch(
                "usa_npn_mcp_server.utils.plotting.io.BytesIO", return_value=mock_buffer
            ):
                yield {
                    "gpd": mock_gpd,
                    "plt": mock_plt,
                    "point": mock_point,
                    "ax": mock_ax,
                    "gdf": mock_gdf,
                    "us_states": mock_us_states,
                }

    @pytest.mark.asyncio
    async def test_generate_map_with_color_by(self, sample_data, mock_geopandas):
        """Test generate_map with color_by parameter."""
        result = await generate_map(sample_data, colour_by="species")

        # Verify the result is a base64 encoded string
        assert isinstance(result, str)
        # Try to decode it to ensure it's valid base64
        base64.b64decode(result)

        # Verify key function calls
        mock_geopandas["gpd"].read_file.assert_called_once()
        mock_geopandas["plt"].subplots.assert_called_once_with(figsize=(15, 9))
        mock_geopandas["us_states"].plot.assert_called_once()
        mock_geopandas["plt"].savefig.assert_called_once()
        mock_geopandas["plt"].close.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_map_without_color_by(self, sample_data, mock_geopandas):
        """Test generate_map without color_by parameter."""
        result = await generate_map(sample_data, colour_by=None)

        # Verify the result is a base64 encoded string
        assert isinstance(result, str)
        base64.b64decode(result)

        # Verify the GeoDataFrame plot was called for simple plotting
        mock_geopandas["gdf"].plot.assert_called()

    @pytest.mark.asyncio
    async def test_generate_map_empty_data_raises_error(self):
        """Test that generate_map raises error for empty data."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            await generate_map([], colour_by="species")

    @pytest.mark.asyncio
    async def test_generate_map_no_coordinates_raises_error(self):
        """Test that generate_map raises error when data lacks coordinates."""
        data = [{"species": "Oak"}, {"species": "Pine"}]
        with pytest.raises(ValueError, match="Latitude and Longitude cannot be empty"):
            await generate_map(data, colour_by="species")

    @pytest.mark.asyncio
    async def test_generate_map_partial_coordinates(self, mock_geopandas):
        """Test generate_map handles data with some missing coordinates."""
        data = [
            {"latitude": 40.7128, "longitude": -74.0060, "species": "Oak"},
            {"species": "Pine"},  # Missing coordinates
            {"latitude": 41.8781, "longitude": -87.6298, "species": "Maple"},
        ]

        result = await generate_map(data, colour_by="species")

        # Should still work with partial data
        assert isinstance(result, str)
        base64.b64decode(result)

    @pytest.mark.asyncio
    async def test_generate_map_with_colormap(self, sample_data):
        """Test that the colormap is properly applied when color_by is specified."""
        with (
            patch("usa_npn_mcp_server.utils.plotting.gpd") as mock_gpd,
            patch("usa_npn_mcp_server.utils.plotting.plt") as mock_plt,
            patch("usa_npn_mcp_server.utils.plotting.Point"),
            patch("usa_npn_mcp_server.utils.plotting.cm") as mock_cm,
            patch("usa_npn_mcp_server.utils.plotting.to_hex") as mock_to_hex,
        ):
            # Setup mocks
            mock_us_states = Mock()
            mock_us_states.plot = Mock()
            mock_gpd.read_file.return_value = mock_us_states

            mock_gdf = Mock()
            mock_gdf.geometry = Mock()
            mock_gdf.geometry.x = Mock()
            mock_gdf.geometry.y = Mock()
            mock_gdf.geometry.x.min.return_value = -120
            mock_gdf.geometry.x.max.return_value = -70
            mock_gdf.geometry.y.min.return_value = 30
            mock_gdf.geometry.y.max.return_value = 45
            mock_gdf.plot = Mock()
            mock_gdf.__getitem__ = Mock(return_value=mock_gdf)
            mock_gpd.GeoDataFrame.return_value = mock_gdf

            mock_ax = Mock()
            mock_fig = Mock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Mock colormap
            mock_colormap = Mock()
            mock_cm.get_cmap.return_value = mock_colormap
            mock_to_hex.return_value = "#FF0000"

            mock_buffer = io.BytesIO(b"fake_image_data")
            with patch(
                "usa_npn_mcp_server.utils.plotting.io.BytesIO", return_value=mock_buffer
            ):
                await generate_map(sample_data, colour_by="species")

            # Verify colormap was created
            mock_cm.get_cmap.assert_called_once_with("tab10", 2)  # 2 unique species
            # Verify to_hex was called for color conversion
            assert mock_to_hex.called

    @pytest.mark.asyncio
    async def test_generate_map_plot_customization(self, sample_data, mock_geopandas):
        """Test that plot customization methods are called."""
        await generate_map(sample_data, colour_by="species")

        # Verify plot customization calls
        mock_geopandas["ax"].set_xlim.assert_called_once_with(-121, -69)
        mock_geopandas["ax"].set_ylim.assert_called_once_with(29, 46)
        mock_geopandas["plt"].xlabel.assert_called_once_with("Longitude")
        mock_geopandas["plt"].ylabel.assert_called_once_with("Latitude")
        mock_geopandas["plt"].title.assert_called_once()
        mock_geopandas["plt"].grid.assert_called_once_with(True)
        mock_geopandas["plt"].tight_layout.assert_called_once()
        mock_geopandas["plt"].legend.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_map_saves_correct_format(self, sample_data, mock_geopandas):
        """Test that the map is saved in the correct format."""
        await generate_map(sample_data, colour_by=None)

        # Verify savefig was called with correct format
        call_args = mock_geopandas["plt"].savefig.call_args
        assert call_args[1]["format"] == "jpeg"
        assert call_args[1]["bbox_inches"] == "tight"
