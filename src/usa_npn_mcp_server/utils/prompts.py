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
}


def get_prompts() -> list[Prompt]:
    """
    Extract and return a list of Prompt objects from the PROMPTS dictionary.

    Returns
    -------
        list[Prompt]: A list of Prompt objects extracted from the PROMPTS dictionary.
    """
    return [each["prompt"] for each in PROMPTS.values()]
