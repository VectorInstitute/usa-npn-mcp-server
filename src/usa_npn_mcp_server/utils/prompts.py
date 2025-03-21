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
    "make-calendar": {
        "prompt": Prompt(
            name="make-calendar",
            description="Create a calendar of phenophase activity for a species over a given time-frame.",
            arguments=[
                PromptArgument(
                    name="species",
                    description="Species to create a calendar for (species_ID)",
                    required=True,
                ),
                PromptArgument(
                    name="start-date",
                    description="The start date of the calendar (e.g., '2023-01-01')",
                    required=True,
                ),
                PromptArgument(
                    name="end-date",
                    description="The end date of the calendar (e.g., '2023-12-31')",
                    required=True,
                ),
            ],
        ),
        "template": """
        You are an AI assistant that helps users to explore phenological data in their Workspace.
        Your goal is to generate a calendar that summarizes key phenophases for a given species over a specified time-frame.
        You use the tool for Magnitude Phenometrics to query the NPN API and generate data for the calendar based on user input.
        The frequency parameter should be set by you and be an integer that splits the calendar into 10-15 equal parts.
        The calendar will include key phenophases and their corresponding dates and lengths delineated by colour.
        You should guide the scenario to completion.
        1. The user has chosen the topic: {species} calendar from {start-date} to {end-date}.
        2. Generate a frequency parameter that is fitting for the start date and end date.
        3. Explain the goal of helping the user to explore their data.
        4. Present the user with the tool parameters you are going to use and ask the user if they would like to adjust any parameters.
        5. Use the tool for Magnitude Phenometrics to query the NPN API.
        6. Inspect the data.
        7. Pause for user input with a small summary of the data that will be used to generate a calendar. Ask if the user would like to you to generate the calender with the data.
        8. Generate a calendar that summarizes key phenophases for a given species over a specified time-frame. Present the calendar to the user.
""",
    },
    "explore_data": {
        "prompt": Prompt(
            name="explore_data",
            description="Perform a query to the NPN API for some data and perform some user-guided analysis of the data.",
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
                PromptArgument(
                    name="species_ids",
                    description="Species to explore, ','-delimited species_IDs, e.g., '1,2,3'",
                    required=False,
                ),
                PromptArgument(
                    name="site_ids",
                    description="Site IDs to explore, ','-delimited site_IDs, e.g., '1,2,3'",
                    required=False,
                ),
                PromptArgument(
                    name="states",
                    description="States to explore, ','-delimited 2-letter state abbreviations (e.g., 'CA,TX')",
                    required=False,
                ),
            ],
        ),
        "template": """
        You are an AI assistant that helps users to explore phenological data in their Workspace.
        Your goal is to query the NPN API using the Magnitude, Site, and Individual Phenometrics tools, summarize the data returned, and plot a map of the site phenometrics data using the simpleplot tool.
        Follow these steps to guide the user:
        1. The user has chosen to explore phenological data from {start-date} to {end-date}.
        2. Use the provided parameters (species_ids, site_ids, states) to query the NPN API using the Magnitude, Site, and Individual Phenometrics tools.
        3. Summarize the data returned from the queries, highlighting key insights and trends.
        4. Present the data summary to the user, and ask if they would like to refine the parameters or perform additional analysis.
        5. Guide the user through any further steps based on their input, ensuring they achieve their data exploration goals.
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
