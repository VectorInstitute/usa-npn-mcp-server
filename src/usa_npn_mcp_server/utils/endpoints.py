"""NPN API endpoints available in MCP Server."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class BaseQuery(BaseModel):
    """Base class for endpoint queries."""

    start_date: str = Field(
        ..., description="Start date in YYYY-MM-DD format. Must be used with end_date."
    )
    end_date: str = Field(
        ..., description="End date in YYYY-MM-DD format. Must be used with start_date."
    )
    bottom_left_x1: Optional[float] = Field(
        default=None,
        description="X coordinate of the bottom left corner for bounding box filtering.",
    )
    bottom_left_y1: Optional[float] = Field(
        default=None,
        description="Y coordinate of the bottom left corner for bounding box filtering.",
    )
    upper_right_x2: Optional[float] = Field(
        default=None,
        description="X coordinate of the upper right corner for bounding box filtering.",
    )
    upper_right_y2: Optional[float] = Field(
        default=None,
        description="Y coordinate of the upper right corner for bounding box filtering.",
    )
    species_id: Optional[int] = Field(
        default=None, description="Unique species identifier."
    )
    station_id: Optional[int] = Field(
        default=None,
        description="Unique identifier associated with an observer’s location.",
    )
    species_type: Optional[str] = Field(
        default=None,
        description="Species type(s) the organism belongs to. Must match values from getAnimalTypes and getPlantTypes.",
    )
    network: Optional[str] = Field(
        default=None,
        description="Name of the network(s)/group(s) where the organism is observed. Must match values from getPartnerNetworks.",
    )
    state: Optional[str] = Field(
        default=None,
        description="State where the observation occurred. Uses two-character postal abbreviation.",
    )
    phenophase_category: Optional[str] = Field(
        default=None,
        description="Phenophase category. Must match values from getPhenophase.",
    )
    phenophase_id: Optional[int] = Field(
        default=None, description="Unique identifier of the phenophase."
    )
    functional_type: Optional[str] = Field(
        default=None,
        description="Functional types of the species. Must match values from getSpeciesFunctionalTypes.",
    )
    climate_data: Optional[int] = Field(
        default=None,
        description="Flag to indicate whether all climate data fields should be returned. Accepts 0 or 1.",
    )


class ObservationsQuery(BaseQuery):
    """
    Input parameters for the getObservations endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getObservations
    """

    pass


class ObservationCommentQuery(BaseModel):
    """Input parameters for the getObservationComment endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getObservationComment
    """

    observation_id: int = Field(
        description="The ID of the observation for which to retrieve the comment"
    )


class SummarizedDataQuery(BaseQuery):
    """
    Input parameters for the getSummarizedData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSummarizedData
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class SiteLevelDataQuery(BaseQuery):
    """
    Input parameters for the getSiteLevelData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSiteLevelData
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class MagnitudeDataQuery(BaseQuery):
    """
    Input parameters for the getMagnitudeData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getMagnitudeData
    """

    frequency: int = Field(
        ...,
        description="Number of days by which to delineate the period of time. Should be less or equal to number of days between start_date and end_date.",
    )


class NPNTool(BaseModel):
    """
    A class representing a tool available in the MCP server.

    Attributes
    ----------
    name : str
        The name of the tool.
    description : str
        A description of the tool.
    inputSchema : str
        The input schema for the tool.
    endpoint : str
        The exact API endpoint for the tool.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    endpoint: str


class NPNTools:
    """
    An enumeration of tools available for querying the NPN API.

    Attributes
    ----------
    Observations : Tool
        Tool for querying raw observation data.
    ObservationComment : Tool
        Tool for retrieving comments for observations.
    MagnitudeData : Tool
        Tool for querying magnitude data.
    SiteLevelData : Tool
        Tool for querying site level data.
    SummarizedData : Tool
        Tool for querying summarized data.
    """

    Observations = NPNTool(
        name="observations",
        description="Query NPN API for intensity and status data aka raw observation data (from getObservations endpoint), results stored as readable Resource 'observations'",
        input_schema=ObservationsQuery.model_json_schema(),
        endpoint="getObservations",
    )
    ObservationComment = NPNTool(
        name="observation_comment",
        description="Retrieve the comment for a given observation (from getObservationComment endpoint), results store as readable Resource 'observation_comment'",
        input_schema=ObservationCommentQuery.model_json_schema(),
        endpoint="getObservationComment",
    )
    MagnitudeData = NPNTool(
        name="magnitude_data",
        description="Query NPN API for magnitude phenometrics aka magnitude data (from getMagnitudeData endpoint), results stored as readable Resource 'magnitude_data'",
        input_schema=MagnitudeDataQuery.model_json_schema(),
        endpoint="getMagnitudeData",
    )
    SiteLevelData = NPNTool(
        name="site_level_data",
        description="Query NPN API for site phenometrics aka site level data (from getSiteLevelData endpoint), results stored as readable Resource 'site_level_data'",
        input_schema=SiteLevelDataQuery.model_json_schema(),
        endpoint="getSiteLevelData",
    )
    SummarizedData = NPNTool(
        name="summarized_data",
        description="Query NPN API for individual phenometrics aka summarized data (from getSummarizedData endpoint), results stored as readable Resource 'summarized_data'",
        input_schema=SummarizedDataQuery.model_json_schema(),
        endpoint="getSummarizedData",
    )
