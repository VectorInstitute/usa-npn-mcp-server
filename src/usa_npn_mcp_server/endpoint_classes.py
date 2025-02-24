"""NPN API endpoints available in MCP Server."""

from pydantic import BaseModel, Field


class ObservationsQuery(BaseModel):
    """
    Input parameters for the getObservations endpoint.

    Only a subset of available parameters is included.
    """

    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")
    species_id: str = Field(
        default="",
        description="Comma-separated list of species ids to filter observations",
    )
    station_id: int | None = Field(
        default=None, description="Station identifier to filter observations"
    )
    bottom_left_x1: float | None = Field(
        default=None,
        description="X coordinate of the bottom left corner for bounding box filtering",
    )
    bottom_left_y1: float | None = Field(
        default=None,
        description="Y coordinate of the bottom left corner for bounding box filtering",
    )
    upper_right_x2: float | None = Field(
        default=None,
        description="X coordinate of the upper right corner for bounding box filtering",
    )
    upper_right_y2: float | None = Field(
        default=None,
        description="Y coordinate of the upper right corner for bounding box filtering",
    )


class ObservationCommentQuery(BaseModel):
    """Input parameters for the getObservationComment endpoint."""

    observation_id: int = Field(
        description="The ID of the observation for which to retrieve the comment"
    )
