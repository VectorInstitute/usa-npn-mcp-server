"""Unit tests for endpoint classes in usa_npn_mcp_server."""

from usa_npn_mcp_server.utils.endpoints import (
    ObservationCommentQuery,
    ObservationsQuery,
)


def test_observations_query_model():
    """Test the ObservationsQuery model."""
    query = ObservationsQuery(
        start_date="2025-01-01",
        end_date="2025-01-31",
        bottom_left_x1=0.0,
        bottom_left_y1=0.0,
        upper_right_x2=1.0,
        upper_right_y2=1.0,
        species_id=3,
        station_id=1,
        species_type="plant",
        network="NPN",
        state="CA",
        phenophase_category="leaf",
        phenophase_id=1,
        functional_type="annual",
        climate_data=1,
    )
    assert query.start_date == "2025-01-01"
    assert query.end_date == "2025-01-31"
    assert query.bottom_left_x1 == 0.0
    assert query.bottom_left_y1 == 0.0
    assert query.upper_right_x2 == 1.0
    assert query.upper_right_y2 == 1.0
    assert query.species_id == 3
    assert query.station_id == 1
    assert query.species_type == "plant"
    assert query.network == "NPN"
    assert query.state == "CA"
    assert query.phenophase_category == "leaf"
    assert query.phenophase_id == 1
    assert query.functional_type == "annual"
    assert query.climate_data == 1


def test_observation_comment_query_model():
    """Test the ObservationCommentQuery model."""
    query = ObservationCommentQuery(observation_id=1)
    assert query.observation_id == 1
