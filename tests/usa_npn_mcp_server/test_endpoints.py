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
        species_id="1,2,3",
        station_id=1,
        bottom_left_x1=0.0,
        bottom_left_y1=0.0,
        upper_right_x2=1.0,
        upper_right_y2=1.0,
    )
    assert query.start_date == "2025-01-01"
    assert query.end_date == "2025-01-31"
    assert query.species_id == "1,2,3"
    assert query.station_id == 1
    assert query.bottom_left_x1 == 0.0
    assert query.bottom_left_y1 == 0.0
    assert query.upper_right_x2 == 1.0
    assert query.upper_right_y2 == 1.0


def test_observation_comment_query_model():
    """Test the ObservationCommentQuery model."""
    query = ObservationCommentQuery(observation_id=1)
    assert query.observation_id == 1
