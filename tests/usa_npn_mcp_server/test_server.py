"""Test the query_api function in the usa_npn_mcp_server.api_client module."""

import pytest

from usa_npn_mcp_server.api_client import APIClient
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
async def test_check_reference_material_integration(mocker):
    """Test the check_reference_material function in the server."""
    mocker.patch(
        "usa_npn_mcp_server.api_client.APIClient.read_ancillary_file",
        return_value='[{"species_id": 1, "common_name": "Oak"}]',
    )
    async with APIClient() as client:
        result = await client.check_reference_material(
            arguments={"sql_query": "SELECT * FROM species WHERE species_id = 1"}
        )
        assert len(result) == 1
        assert "Oak" in result[0].text
