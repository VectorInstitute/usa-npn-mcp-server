"""Test the query_api function in the usa_npn_mcp_server.api_client module."""

import pytest

from usa_npn_mcp_server.api_client import APIClient
from usa_npn_mcp_server.utils.endpoints import NPNTools


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_observations(mocker):
    """Test the query_api function to fetch observations."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"observations": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        NPNTools.Observations.endpoint,
        arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )
    assert data == '{"observations": []}'


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_observation_comment(mocker):
    """Test the query_api function to fetch observation comments."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"comments": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        NPNTools.ObservationComment.endpoint,
        arguments={"observation_id": 1},
    )
    assert data == '{"comments": []}'


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_summarized_data(mocker):
    """Test the query_api function to fetch summarized data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"summarized_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        NPNTools.SummarizedData.endpoint,
        arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )
    assert data == '{"summarized_data": []}'


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_site_level_data(mocker):
    """Test the query_api function to fetch site-level data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"site_level_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        NPNTools.SiteLevelData.endpoint,
        arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )
    assert data == '{"site_level_data": []}'


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_magnitude_data(mocker):
    """Test the query_api function to fetch site-level data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"magnitude_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    data = await APIClient.query_api(
        NPNTools.MagnitudeData.endpoint,
        arguments={
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "frequency": 7,
        },
    )
    assert data == '{"site_level_data": []}'
