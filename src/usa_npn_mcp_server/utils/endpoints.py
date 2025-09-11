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

    Inherits all attributes from BaseQuery.
    """

    pass


class ObservationCommentQuery(BaseModel):
    """
    Input parameters for the getObservationComment endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getObservationComment

    Attributes
    ----------
    observation_id : int
        The ID of the observation for which to retrieve the comment.
    """

    observation_id: int = Field(
        description="The ID of the observation for which to retrieve the comment"
    )


class IndividualPhenometricsQuery(BaseQuery):
    """
    Input parameters for the getSummarizedData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSummarizedData

    Attributes
    ----------
    individual_ids : Optional[List[int]], optional
        List of unique individual identifiers.
        Inherits all other attributes from BaseQuery.
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class SitePhenometricsQuery(BaseQuery):
    """
    Input parameters for the getSiteLevelData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getSiteLevelData

    Attributes
    ----------
    individual_ids : Optional[List[int]], optional
        List of unique individual identifiers.
        Inherits all other attributes from BaseQuery.
    """

    individual_ids: Optional[List[int]] = Field(
        default=None,
        description="List of unique identifiers of the individuals for which the observations are made.",
    )


class MagnitudePhenometricsQuery(BaseQuery):
    """
    Input parameters for the getMagnitudeData endpoint.

    URL: https://services.usanpn.org/npn_portal/observations/getMagnitudeData

    Attributes
    ----------
    frequency : int
        Number of days by which to delineate the period of time.
        Should be less or equal to number of days between start_date and end_date.
        Inherits all other attributes from BaseQuery.
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
    color_by: str = Field(
        ...,
        description="Variable to be used for color coding the data points.",
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
    color_by: str = Field(
        default="",
        description="Variable to be used for color coding the data points. Default is empty string for no coloring.",
    )


class SQLQueryModel(BaseModel):
    """Input parameters for checking reference material tool."""

    sql_query: str = Field(
        ...,
        description="SQL query to run against the SQLite3 database to fetch relevant data.",
    )


class GetRawDataQuery(BaseModel):
    """Input parameters for getting raw cached data."""

    hash_id: str = Field(
        ..., description="Hash ID of cached query to retrieve raw data from"
    )


class ExportRawDataQuery(BaseModel):
    """Input parameters for exporting raw cached data to file."""

    hash_id: str = Field(..., description="Hash ID of cached query to export")
    file_format: Literal["json", "jsonl"] = Field(
        ..., description="Export format: json or jsonl"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Optional filename. If not provided, auto-generated from hash_id",
    )
    output_path: Optional[str] = Field(
        default=None,
        description="Output path for the file (relative to root or absolute within allowed roots). If not provided, saves to the first available root directory.",
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
    docs_one_liner : Optional[str]
        A short one-line description for documentation purposes.
    input_schema : dict[str, Any]
        The input schema for the tool.
    endpoint : str
        The exact API endpoint for the tool.
    """

    name: str
    description: str
    docs_one_liner: Optional[str] = Field(
        default=None,
        description="Short one-line description for documentation purposes (not exposed via MCP)",
    )
    input_schema: dict[str, Any]
    endpoint: str


class NPNTools:
    """
    An enumeration of tools available for querying the NPN API.

    Class Attributes
    ----------------
    StatusIntensity : NPNTool
        Tool for querying intensity and status data from the NPN API.
    ObservationComment : NPNTool
        Tool for retrieving comments associated with observations from the NPN API.
    MagnitudePhenometrics : NPNTool
        Tool for querying magnitude phenometrics data from the NPN API.
    SitePhenometrics : NPNTool
        Tool for querying site phenometrics data from the NPN API.
    IndividualPhenometrics : NPNTool
        Tool for querying individual phenometrics data from the NPN API.
    Mapping : NPNTool
        Tool for constructing maps from site phenometrics data.
    CheckReferenceMaterial : NPNTool
        Tool for checking what reference material is available to translate natural
        language into specific ids and terms needed for querying the NPN API.
    CheckLiterature : NPNTool
        Tool for checking 175 structured summaries of studies that used data collected
        by the National Phenology Network.
    GetRawData : NPNTool
        Tool for retrieving raw data from cache using a hash ID.
    ExportRawData : NPNTool
        Tool for exporting cached raw data to a JSON or JSONL file.
    """

    StatusIntensity = NPNTool(
        name="status-intensity",
        description="""
About the tool: Retrieves raw, unprocessed observation records from citizen and professional scientists documenting day-by-day phenological status (yes/no) and intensity measurements for individual plants and animal species. Each record represents a single observation event showing whether specific phenophases (like 'breaking leaf buds' or 'full bloom') were occurring on a particular date for a specific individual organism at a monitoring site.

When to use: Only for detailed analysis of specific observation events, quality control, or when you need the granular day-to-day data that underlies the aggregated metrics. Most users should use Individual, Site, or Magnitude Phenometrics instead.

Key applications: Data validation, understanding observer reporting patterns, analyzing day-to-day phenological transitions, custom aggregations not available in other tools.
Performance warning: This tool can return massive datasets (potentially millions of records). Always limit queries to small date ranges (≤30 days recommended) and specific geographic areas or species to prevent system crashes. Use aggregated tools (Individual/Site/Magnitude Phenometrics) for broader analyses.

Data interpretation: Values of -9999 represent missing/null data. Records include observation date, individual ID, phenophase status, intensity measurements, and site metadata.""",
        docs_one_liner="Fetches status and intensity data (raw observation data).",
        input_schema=StatusIntensityQuery.model_json_schema(),
        endpoint="getObservations",
    )
    ObservationComment = NPNTool(
        name="observation-comment",
        description="Retrieve the comment for a given observation (from getObservationComment endpoint), results store as readable Resource 'observation_comment'",
        docs_one_liner="Fetches observation comments based on observation_id.",
        input_schema=ObservationCommentQuery.model_json_schema(),
        endpoint="getObservationComment",
    )
    MagnitudePhenometrics = NPNTool(
        name="magnitude-phenometrics",
        docs_one_liner="Fetches magnitude phenometrics (magnitude data).",
        description="""
About the tool: Summarizes the intensity and abundance of phenological activity across multiple individuals, sites, or time periods using aggregated status and intensity data. Shows 'how much' phenological activity is occurring (not just when), providing insights into the magnitude, synchrony, and temporal patterns of biological processes.

When to use: Understanding broad ecological patterns, studying synchrony between interacting species, analyzing peak activity timing, or investigating how environmental changes affect the intensity of biological processes across populations.

Key applications:

- Species synchrony analysis: Quantifying how synchronized phenological timing is between interacting species (pollinators and plants, herbivores and host plants, predators and prey)
- Peak activity timing: Identifying when maximum biological activity occurs across populations
- Climate change impacts: Studying how warming affects the magnitude and timing of phenological events
- Biodiversity patterns: Understanding temporal overlap in species activity within ecosystems
- Population-level responses: Analyzing how abundant or widespread phenological activity is across landscapes
- Conservation planning: Identifying critical timing windows for species management

Scientific context: Based on current research showing that phenological synchrony between species is shifting due to climate change, with implications for ecosystem functioning and species interactions. This tool helps quantify these critical ecological relationships.

Requires: Date range and frequency parameters (daily, weekly, etc.) are essential. Recommended to specify species and phenophases of interest to avoid overwhelming results.
Research applications:

- 'Are migrating birds arriving when their insect food sources are most abundant?'
- 'How synchronous is flowering across plant species in prairie communities?'
- 'Has climate change affected the temporal overlap between butterfly emergence and host plant activity?'

Data interpretation: Results show time-series data of phenological abundance/intensity aggregated by specified frequency. Values represent proportion of 'yes' records, animal abundance measures, or intensity metrics across the selected populations.""",
        input_schema=MagnitudePhenometricsQuery.model_json_schema(),
        endpoint="getMagnitudeData",
    )
    SitePhenometrics = NPNTool(
        name="site-phenometrics",
        docs_one_liner="Fetches site phenometrics (site-level data).",
        description="""
About the tool: Aggregates individual phenological data to provide average start and end dates of phenological activity for each species at each monitoring site. Represents the 'typical' timing for a species at a location by averaging across all individuals of that species at the site.

When to use: Creating phenological calendars, analyzing site-specific timing patterns, comparing phenology across locations, understanding regional growing seasons, or studying how local climate affects species timing.

Key applications:

- Phenological calendars: Creating seasonal timing guides for specific locations
- Growing season analysis: Quantifying length of active growing periods for sites/regions
- Climate relationship studies: Investigating how phenological timing relates to temperature, precipitation, and seasonal patterns
- Site comparisons: Comparing phenological timing across elevation gradients, latitude gradients, or different habitat types
- Regional management: Planning for activities like controlled burns, invasive species management, or ecotourism
- Agricultural applications: Understanding wild plant timing to inform crop management decisions

Scientific context: Site phenometrics average out individual variation to reveal location-specific phenological signatures. Essential for understanding how climate drivers affect species timing at landscape scales.

Research applications:

- 'When do oak leaves typically emerge at Yellowstone vs. Great Smoky Mountains?'
- 'How long is the typical growing season for maple species in Minnesota?'
- 'When should we expect peak wildflower blooms in different Colorado elevation zones?'

Data interpretation: Each record represents one species at one site for the specified time period. Start/end dates are averages across individuals. Sites represent uniform habitat areas ≤15 acres. Values of -9999 represent missing/null data.""",
        input_schema=SitePhenometricsQuery.model_json_schema(),
        endpoint="getSiteLevelData",
    )
    IndividualPhenometrics = NPNTool(
        name="individual-phenometrics",
        docs_one_liner="Fetches individual phenometrics (summarized data).",
        description="""
About the tool: Provides start and end dates of phenological activity for individual plants and animal species, derived from status data. Each record represents one 'phenological episode' - a period of continuous activity for a specific phenophase on an individual organism (like when one specific maple tree's leaves went from bud break to full leaf drop).

When to use: To understand phenological patterns within species, analyze individual plant behavior, study variation between organisms of the same species, or investigate multiple episodes of activity within a single growing season.

Key applications:

- Studying phenological diversity within populations
- Analyzing individual plant responses to local microclimates
- Documenting multiple flowering/leafing episodes in water-limited ecosystems
- Understanding species-specific phenological strategies
- Quality control for site-level aggregations
- Research on plant physiological responses to environmental triggers

Important considerations:

- For plants: Shows actual start/end dates for individual organisms
- For animals: Shows presence/absence periods at species level (since individual animals aren't tracked)
- Requires date range specification (typically calendar year)
- Multiple episodes may occur for same individual/phenophase within one season (e.g., after frost damage or drought recovery)
- Essential for understanding the biological basis of site-level patterns

Data interpretation: Records show individual_id, phenophase onset/end dates, and episode duration. -9999 values indicate missing data.""",
        input_schema=IndividualPhenometricsQuery.model_json_schema(),
        endpoint="getSummarizedData",
    )
    Mapping = NPNTool(
        name="mapping",
        description="Construct a map from results of a previous Site Phenometrics query to the NPN API, using longitude, latitude and specified variables to plot onto map of USA.",
        docs_one_liner="Maps site phenometrics onto a map of the USA with optional color labeling.",
        input_schema=MapModel.model_json_schema(),
        endpoint="",
    )
    CheckReferenceMaterial = NPNTool(
        name="check-reference-material",
        docs_one_liner="Checks database containing NPN API reference material using a generated SQL query.",
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
        input_schema=SQLQueryModel.model_json_schema(),
        endpoint="",
    )

    CheckLiterature = NPNTool(
        name="check-literature",
        docs_one_liner="Queries database of structured summaries from 175 papers that use phenology and phenometrics data.",
        description="""
            Query an SQL database for structured summaries of studies that used data collected by National Phenology Network. The tables have the following structure:

            Table: literature, Length: 175, Headers: ['Title', 'Authors', 'DOI', 'DOI link', 'Venue', 'Citation count', 'Year', 'Filename', 'Measured variables', 'Temporal Range', 'Spatial Scope', 'Data Filtering', 'Statistical Tests', 'Modelling', 'Software Tools', 'Limitations', 'Main findings', 'Research gaps', 'Future research', 'Independent variables', 'Dependent variables', 'Organism', 'Summary of discussion', 'API Query', "Supporting quotes for 'Measured variables'", "Supporting tables for 'Measured variables'", "Reasoning for 'Measured variables'", "Supporting quotes for 'Temporal Range'", "Supporting tables for 'Temporal Range'", "Reasoning for 'Temporal Range'", "Supporting quotes for 'Spatial Scope'", "Supporting tables for 'Spatial Scope'", "Reasoning for 'Spatial Scope'", "Supporting quotes for 'Data Filtering'", "Supporting tables for 'Data Filtering'", "Reasoning for 'Data Filtering'", "Supporting quotes for 'Statistical Tests'", "Supporting tables for 'Statistical Tests'", "Reasoning for 'Statistical Tests'", "Supporting quotes for 'Modelling'", "Supporting tables for 'Modelling'", "Reasoning for 'Modelling'", "Supporting quotes for 'Software Tools'", "Supporting tables for 'Software Tools'", "Reasoning for 'Software Tools'", "Supporting quotes for 'Limitations'", "Supporting tables for 'Limitations'", "Reasoning for 'Limitations'", "Supporting quotes for 'Main findings'", "Supporting tables for 'Main findings'", "Reasoning for 'Main findings'", "Supporting quotes for 'Research gaps'", "Supporting tables for 'Research gaps'", "Reasoning for 'Research gaps'", "Supporting quotes for 'Future research'", "Supporting tables for 'Future research'", "Reasoning for 'Future research'", "Supporting quotes for 'Independent variables'", "Supporting tables for 'Independent variables'", "Reasoning for 'Independent variables'", "Supporting quotes for 'Dependent variables'", "Supporting tables for 'Dependent variables'", "Reasoning for 'Dependent variables'", "Supporting quotes for 'Organism'", "Supporting tables for 'Organism'", "Reasoning for 'Organism'", "Supporting quotes for 'Summary of discussion'", "Supporting tables for 'Summary of discussion'", "Reasoning for 'Summary of discussion'", "Supporting quotes for 'API Query'", "Supporting tables for 'API Query'", "Reasoning for 'API Query'"]
            Description: Contains structured summaries of 175 papers that use phenology and phenometrics, included in the table is the reasoning and sourcing for each summary column.
        """,
        input_schema=SQLQueryModel.model_json_schema(),
        endpoint="",
    )

    GetRawData = NPNTool(
        name="get-raw-data",
        description="Retrieve raw data from cache using hash ID. Limited to 300 records with truncation message if exceeded. Use 'recent-queries' resource to see available hash IDs.",
        docs_one_liner="Fetches raw data instead of summaries as from other tools.",
        input_schema=GetRawDataQuery.model_json_schema(),
        endpoint="",
    )

    ExportRawData = NPNTool(
        name="export-raw-data",
        description="Export cached raw data to JSON or JSONL file. Requires MCP client to provide roots (allowed directories) for file operations.",
        docs_one_liner="Exports raw data to JSON or JSONL files in allowed directories.",
        input_schema=ExportRawDataQuery.model_json_schema(),
        endpoint="",
    )
