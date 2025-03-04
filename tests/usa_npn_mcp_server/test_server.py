"""Test the query_api function in the usa_npn_mcp_server.api_client module."""

import pytest

from usa_npn_mcp_server.api_client import APIClient


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_observations(mocker):
    """Test the query_api function before external API call to fetch observations."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"observations": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        "getObservations",
        arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )
    assert data == '{"observations": []}'
