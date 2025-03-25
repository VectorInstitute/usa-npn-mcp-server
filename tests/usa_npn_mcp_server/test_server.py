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

    async with APIClient() as client:
        await client.query_api(
            endpoint=NPNTools.Observations.endpoint,
            arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
        )
        data = client.read_last_response(name=NPNTools.Observations.name)
        assert data == {"result": {"observations": []}}


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_observation_comment(mocker):
    """Test the query_api function to fetch observation comments."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"comments": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
    async with APIClient() as client:
        await client.query_api(
            endpoint=NPNTools.ObservationComment.endpoint,
            arguments={"observation_id": 1},
        )
        data = client.read_last_response(name=NPNTools.ObservationComment.name)
        assert data == {"result": {"comments": []}}


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_summarized_data(mocker):
    """Test the query_api function to fetch summarized data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"summarized_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with APIClient() as client:
        await client.query_api(
            endpoint=NPNTools.SummarizedData.endpoint,
            arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
        )
        data = client.read_last_response(name=NPNTools.SummarizedData.name)
        assert data == {"result": {"summarized_data": []}}


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_site_level_data(mocker):
    """Test the query_api function to fetch site-level data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"site_level_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with APIClient() as client:
        await client.query_api(
            endpoint=NPNTools.SiteLevelData.endpoint,
            arguments={"start_date": "2025-01-01", "end_date": "2025-01-31"},
        )
        data = client.read_last_response(name=NPNTools.SiteLevelData.name)
        assert data == {"result": {"site_level_data": []}}


@pytest.mark.integration_test
@pytest.mark.asyncio
async def test_query_magnitude_data(mocker):
    """Test the query_api function to fetch magnitude data."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"magnitude_data": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    async with APIClient() as client:
        await client.query_api(
            endpoint=NPNTools.MagnitudeData.endpoint,
            arguments={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "frequency": 7,
            },
        )
        data = client.read_last_response(name=NPNTools.MagnitudeData.name)
        assert data == {"result": {"magnitude_data": []}}
