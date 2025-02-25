"""Conftest."""

import pytest


@pytest.fixture
def sample_observations_result() -> list[dict]:
    """Sample result from getObservations request."""
    return [
        {
            "observation_id": 45164649,
            "update_datetime": -9999,
            "site_id": 56104,
            "latitude": 37.574738,
            "longitude": -77.536865,
            "elevation_in_meters": -9999,
            "state": "VA",
            "species_id": 3,
            "genus": "Acer",
            "species": "rubrum",
            "common_name": "red maple",
            "kingdom": "Plantae",
            "individual_id": 347372,
            "phenophase_id": 371,
            "phenophase_description": "Breaking leaf buds",
            "observation_date": "2025-02-22",
            "day_of_year": 53,
            "phenophase_status": 0,
            "intensity_category_id": 39,
            "intensity_value": -9999,
            "abundance_value": -9999,
        },
        {
            "observation_id": 45164658,
            "update_datetime": -9999,
            "site_id": 56104,
            "latitude": 37.574738,
            "longitude": -77.536865,
            "elevation_in_meters": -9999,
            "state": "VA",
            "species_id": 3,
            "genus": "Acer",
            "species": "rubrum",
            "common_name": "red maple",
            "kingdom": "Plantae",
            "individual_id": 347372,
            "phenophase_id": 390,
            "phenophase_description": "Ripe fruits",
            "observation_date": "2025-02-22",
            "day_of_year": 53,
            "phenophase_status": 0,
            "intensity_category_id": 58,
            "intensity_value": -9999,
            "abundance_value": -9999,
        },
    ]
