"""NPN API endpoints available in MCP Server."""

from typing import Any, List, Literal, Optional

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
        default=1,
        description="Flag to indicate whether all climate data fields should be returned. Accepts 0 or 1. Almost always beneficial to see climate data in relation to phenometric data.",
    )


class StatusIntensityQuery(BaseQuery):
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


class IndividualPhenometricsQuery(BaseQuery):
    """
    Input parameters for the getSummarizedData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSummarizedData
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class SitePhenometricsQuery(BaseQuery):
    """
    Input parameters for the getSiteLevelData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSiteLevelData
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class MagnitudePhenometricsQuery(BaseQuery):
    """
    Input parameters for the getMagnitudeData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getMagnitudeData
    """

    frequency: int = Field(
        ...,
        description="Number of days by which to delineate the period of time. Should be less or equal to number of days between start_date and end_date.",
    )


class BasePlotModel(BaseModel):
    """Base class for plotting input parameters."""

    tool_name: str = Field(
        description="Name of the tool used to generate the data for the plot.",
    )
    plot_type: Literal["bar", "line", "scatter", "map"] = Field(
        description="Type of plot to generate.",
    )
    colour_by: str = Field(
        ...,
        description="Variable to be used for colour coding the data points.",
    )
    title: Optional[str] = Field(
        description="Title for the plot.",
    )


class NonMapPlotModel(BasePlotModel):
    """Input parameters for plotting data."""

    y_variable: Optional[str] = Field(
        description="Variable to be plotted on the y-axis.",
    )
    y_lab: Optional[str] = Field(
        description="Label for the y-axis of the plot.",
    )
    plot_type: Literal["bar", "line", "scatter"] = Field(
        description="Type of plot to generate.",
    )
    x_variable: Optional[str] = Field(
        description="Variable to be plotted on the x-axis.",
    )
    x_lab: Optional[str] = Field(
        description="Label for the x-axis of the plot.",
    )


class MapModel(BasePlotModel):
    """Input parameters for mapping data."""

    plot_type: Literal["map"] = Field(
        description="Type of plot to generate.",
    )
    tool_name: Literal["site-phenometrics"] = Field(
        description="Name of the tool used to generate the data for the plot.",
    )
    colour_by: str = Field(
        default="",
        description="Variable to be used for colour coding the data points. Default is empty string for no colouring.",
    )


class CheckReferenceMaterialSQLQueryModel(BaseModel):
    """Input parameters for checking reference material tool."""

    sql_query: str = Field(
        ...,
        description="SQL query to run against the SQLite3 database to fetch relevant data.",
    )


class FilterVariableQueryModel(BaseModel):
    """Input parameters for checking reference material tool."""

    tool_name: str = Field(
        ...,
        description="Name of the tool used to generate the data to be filtered.",
    )
    variables: List[str] = Field(
        ...,
        description="List of variable names to be filtered from the raw data.",
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
    StatusIntensity : Tool
        Tool for querying raw observation data.
    ObservationComment : Tool
        Tool for retrieving comments for observations.
    MagnitudePhenometrics : Tool
        Tool for querying magnitude phenometrics.
    SitePhenometrics : Tool
        Tool for querying site phenometrics.
    IndividualPhenometrics : Tool
        Tool for querying individual phenometrics.
    Mapping : Tool
        Tool for constructing maps from query results.
    CheckReferenceMaterial : Tool
        Tool for translating natural language into API-compliant terms
    """

    StatusIntensity = NPNTool(
        name="status-intensity",
        description="Query NPN API for intensity and status data aka raw observation data (from getObservations endpoint), results stored as readable Resource 'status_intensity'. Other query tools that aggregate like Site Phenometrics, Individual Phenometrics, and Magnitude Phenometrics are built on top of this tool and should be instead of this tool. This tool should only be used for a small subset of dates because it returns large results.",
        input_schema=StatusIntensityQuery.model_json_schema(),
        endpoint="getObservations",
    )
    ObservationComment = NPNTool(
        name="observation-comment",
        description="Retrieve the comment for a given observation (from getObservationComment endpoint), results store as readable Resource 'observation_comment'",
        input_schema=ObservationCommentQuery.model_json_schema(),
        endpoint="getObservationComment",
    )
    MagnitudePhenometrics = NPNTool(
        name="magnitude-phenometrics",
        description="Query NPN API for magnitude phenometrics aka magnitude data (from getMagnitudeData endpoint), results stored as readable Resource 'magnitude_phenometrics'",
        input_schema=MagnitudePhenometricsQuery.model_json_schema(),
        endpoint="getMagnitudeData",
    )
    SitePhenometrics = NPNTool(
        name="site-phenometrics",
        description="Query NPN API for site phenometrics aka site level data (from getSiteLevelData endpoint), results stored as readable Resource 'site_phenometrics'",
        input_schema=SitePhenometricsQuery.model_json_schema(),
        endpoint="getSiteLevelData",
    )
    IndividualPhenometrics = NPNTool(
        name="individual-phenometrics",
        description="Query NPN API for individual phenometrics aka summarized data (from getSummarizedData endpoint), results stored as readable Resource 'individual_phenometrics'",
        input_schema=IndividualPhenometricsQuery.model_json_schema(),
        endpoint="getSummarizedData",
    )
    Mapping = NPNTool(
        name="mapping",
        description="Construct a map from results of a previous Site Phenometrics query to the NPN API, using longitude, latitude and specified variables to plot onto map of USA.",
        input_schema=MapModel.model_json_schema(),
        endpoint="",
    )
    CheckReferenceMaterial = NPNTool(
        name="check-reference-material",
        description="""
            Query an SQL database for reference material that can be used to translate natural language into specific ids and terms needed for querying the NPN API with other tools. There is no need to check the 'datasets' table unless specific observer groups are mentioned. The Tables have the following structure:

            Table: species, Length: 1882, Headers: ['species_id', 'common_name', 'genus', 'genus_id', 'genus_common_name', 'species', 'kingdom', 'itis_taxonomic_sn', 'functional_type', 'class_id', 'class_common_name', 'class_name', 'order_id', 'order_common_name', 'order_name', 'family_id', 'family_name', 'family_common_name', 'species_type']
            Description: Contains info on species

            Table: phenophases, Length: 383, Headers: ['definition_id', 'dataset_id', 'phenophase_id', 'phenophase_name', 'definition', 'start_date', 'end_date', 'comments']
            Description: Contains info on phenophases

            Table: phenoclasses, Length: 199, Headers: ['phenophase_id', 'phenophase_name', 'phenophase_category', 'pheno_class_id']
            Description: Contains info on phenoclasses (a grouping of phenophases)

            Table: datasets, Length: 14, Headers: ['dataset_id', 'dataset_name', 'dataset_description', 'dataset_comments', 'dataset_documentation_url']
            Description: Contains info on datasets and their contributors

            Table: networks, Length: 833, Headers: ['network_id', 'network_name']
            Description: Contains info on observation groups or networks (aka partner groups)
""",
        input_schema=CheckReferenceMaterialSQLQueryModel.model_json_schema(),
        endpoint="",
    )

    FilterVariables = NPNTool(
        name="filter-variables",
        description="Filter specific variables from raw data.",
        input_schema=FilterVariableQueryModel.model_json_schema(),
        endpoint="",
    )
