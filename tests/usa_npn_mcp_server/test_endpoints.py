"""Unit tests for endpoint classes in usa_npn_mcp_server."""

from usa_npn_mcp_server.utils.endpoints import (
    IndividualPhenometricsQuery,
    MagnitudePhenometricsQuery,
    ObservationCommentQuery,
    SitePhenometricsQuery,
    SQLQueryModel,
    StatusIntensityQuery,
)


def test_status_intensity_query_model():
    """Test the StatusIntensityQuery model."""
    query = StatusIntensityQuery(
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
    assert query.model_dump() == {
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "bottom_left_x1": 0.0,
        "bottom_left_y1": 0.0,
        "upper_right_x2": 1.0,
        "upper_right_y2": 1.0,
        "species_id": 3,
        "station_id": 1,
        "species_type": "plant",
        "network": "NPN",
        "state": "CA",
        "phenophase_category": "leaf",
        "phenophase_id": 1,
        "functional_type": "annual",
        "climate_data": 1,
    }


def test_observation_comment_query_model():
    """Test the ObservationCommentQuery model."""
    query = ObservationCommentQuery(observation_id=1)
    assert query.observation_id == 1


def test_individual_phenometrics_query_model():
    """Test the IndividualPhenometricsQuery model."""
    query = IndividualPhenometricsQuery(
        start_date="2025-01-01",
        end_date="2025-01-31",
        individual_ids=[1, 2, 3],
    )
    assert query.start_date == "2025-01-01"
    assert query.end_date == "2025-01-31"
    assert query.individual_ids == [1, 2, 3]


def test_site_phenometrics_query_model():
    """Test the SitePhenometricsQuery model."""
    query = SitePhenometricsQuery(
        start_date="2025-01-01",
        end_date="2025-01-31",
        individual_ids=[4, 5, 6],
    )
    assert query.start_date == "2025-01-01"
    assert query.end_date == "2025-01-31"
    assert query.individual_ids == [4, 5, 6]


def test_magnitude_phenometrics_query_model():
    """Test the MagnitudePhenometricsQuery model."""
    query = MagnitudePhenometricsQuery(
        start_date="2025-01-01",
        end_date="2025-01-31",
        frequency=7,
    )
    assert query.start_date == "2025-01-01"
    assert query.end_date == "2025-01-31"
    assert query.frequency == 7


def test_sql_query_model():
    """Test SQLQueryModel used by CheckLiterature and CheckReferenceMaterial tools."""
    query1 = SQLQueryModel(
        sql_query="SELECT * FROM phenoclasses WHERE phenophase_category LIKE '%Flowers'"
    )
    query2 = SQLQueryModel(
        sql_query="SELECT Title, Authors FROM literature WHERE Organism LIKE '%bird%'"
    )
    assert (
        query1.sql_query
        == "SELECT * FROM phenoclasses WHERE phenophase_category LIKE '%Flowers'"
    )
    assert (
        query2.sql_query
        == "SELECT Title, Authors FROM literature WHERE Organism LIKE '%bird%'"
    )
