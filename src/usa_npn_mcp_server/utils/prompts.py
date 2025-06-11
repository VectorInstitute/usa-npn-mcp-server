"""Module for defining prompts for the NPN MCP server."""

from typing import TypedDict

from mcp.types import (
    Prompt,
    PromptArgument,
)


class PromptEntry(TypedDict):
    """
    A dictionary type that represents a prompt entry.

    Attributes
    ----------
        prompt (Prompt): The prompt object associated with the entry.
        template (str): The template string for the prompt.
    """

    prompt: Prompt
    template: str


PROMPTS: dict[str, PromptEntry] = {
    "map_data": {
        "prompt": Prompt(
            name="map_data",
            description="Generate a map of the data using the NPN API.",
            arguments=[
                PromptArgument(
                    name="start-date",
                    description="The start date (e.g., '2023-01-01')",
                    required=True,
                ),
                PromptArgument(
                    name="end-date",
                    description="The end date (e.g., '2023-12-31')",
                    required=True,
                ),
            ],
        ),
        "template": """
        You are an AI assistant that helps users to map phenological data in their Workspace.
        Your goal is to query the NPN API using the Magnitude, Site, or Individual Phenometrics tools, provide the user with the summary of the data returned, and then plot a map of the site phenometrics data using the Mapping tool.
        Follow these steps to guide the user:
        1. The user has chosen to map phenological data from {start-date} to {end-date}.
        2. Ask for additional parameters (eg species_ids, site_ids, states) to query the NPN API using the Site Phenometrics tool.
        3. Summarize the data returned from the query, highlighting key insights and trends.
        4. Present the data summary to the user, and ask if they would like to refine the parameters or perform additional analysis before mapping.
        5. If they would like the adjust their search parameters, ask for the parameters to refine the search on and return to step 2. If the user would like to proceed, skip this step.
        6. Determine whether null results need to be filtered from the data that is mapped (ex. values of -9999 often mean null).
        7. Start by producing a map with None (default) for the colour_by parameter to get a sense of where observations occur.
        8. Think about what parameters would fit best for the mapping, particularly the variable to colour by. It is best to use a variable with not too many distinct values and something that is categorical. Don't use state.
        9. Use the Mapping tool with the appropriate parameters to generate a map of the site phenometrics data.
        10. Present the map to the user, and ask if they would like to perform any further analysis or adjustments. Recommend the user visit https://data.usanpn.org/vis-tool/#/ for more comprehensive and interactive visualization of NPN Data.
        """,
    },
    "weekly_report": {
        "prompt": Prompt(
            name="weekly_report",
            description="Generate a weekly report of phenological data using the NPN API Tools.",
            arguments=[
                PromptArgument(
                    name="start-date",
                    description="The start date (e.g., '2023-01-01')",
                    required=True,
                ),
            ],
        ),
        "template": """
Create a weekly report of Phenological observations starting from {start-date} and ending either 7 days later or today, whichever is fewer days since the start date. The report should include the following:

1. **Visualizations Artifact**: Generate visualizations of observation data, including but not limited to:
    - Taxonomic distributions.
    - Abundance and proportion of phenophases, species, and sites observed.
    - Timing of animal species phenophases in relation to plant phenophases and climate measures.
    - Geographical explorations of the data.
    - Provide 3-5 exploratory visualizations of specific observations and specific variables in the dataset to explore relationships between:
        - Phenological observations and climate data.
        - Phenophase data of one organism to phenophase data of another.
        - Ex explore abundance of matting of butterflies in relation to the timing of flowering of plants in the same area.

2. **Text Report Artifact**: Create a complementary text report that:
    - Expands on the visualizations.
    - Highlights trends or specific observations that were interesting during the week.

### Analysis Steps:
- Query the National Phenology Network (NPN) data for the past week's observations using the NPN Tools. First gain a sense of the data using the Site, Individual and Magnitude phenometrics Tools and then look at subsets of the data with the Status and Intensity Tool. Use the check-reference Tool to check for specific ids or necessary info for species, sites or phenophases to help interpret the data.
- Compare the observations to the same week's data from:
  - Last year.
  - 8 years ago.
  - 15 years ago.
- Be sure to include each of the following in your analysis:
    - Identify any significant phenological signals or trends
    - Examine specific variables in the dataset to explore relationships between:
        - Phenological observations and climate data.
        - Phenophase data of one organism to phenophase data of another.
    - Compare the timing of phenophases across different species and sites.
    - Analyze the data to identify:
        - Any shifts in phenological events over time.
        - Changes in the timing of phenophases in relation to climate variables.
        - Any correlations between species and their phenophases.
    - Investigate any literature that may have studied the same species or sites and can provide additional context to add to the artifacts.
    - Additional insights to focus on:
        - Upcoming phenophase observations that are expected to occur in the next week. Query the following week from last year (next week but from last year) to gain insight into expected phenophases.
        - Any observations that may be outliers or unexpected based on historical, climate, or ecological data.
        - Any data collection recommendations for next week.
    - Discuss the implications of this week's differences in observations compared to previous years in the context of climate change and ecological interactions.

Be sure to geographically contextualize any analysis that you perform (ie, highlight that all observations contributing to a plot are from within the same state or highlight the regions of observations using colour or text)
        """,
    },
}


def get_prompts() -> list[Prompt]:
    """
    Extract and return a list of Prompt objects from the PROMPTS dictionary.

    Returns
    -------
        list[Prompt]: A list of Prompt objects extracted from the PROMPTS dictionary.
    """
    return [each["prompt"] for each in PROMPTS.values()]
