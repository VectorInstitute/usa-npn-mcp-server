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
    prompt : Prompt
        The prompt object associated with the entry.
    template : str
        The template string for the prompt.
    """

    prompt: Prompt
    template: str
    code_snippet: str


PROMPTS: dict[str, PromptEntry] = {
    "map-data": {
        "prompt": Prompt(
            name="map-data",
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
                PromptArgument(
                    name="subject",
                    description="Describe the phenological investigation you'd like to map.",
                    required=True,
                ),
            ],
        ),
        "template": """
        You are an AI assistant that helps users investigate and map phenological data.
        Your goal is to query the NPN API, analyze the data, save select data to file, and create a map visualization.

        Follow these steps to guide the user:

        1. The user has chosen to investigate phenological data from {start-date} to {end-date}. The subject of the investigation described by the user is: {subject}.

        2. Ask the user for additional parameters (e.g., species_ids, site_ids, states) they'd like to focus on for querying the NPN API using the Site Phenometrics tool.

        3. Query the API as necessary (only site phenometrics will return long/lat values). Always include climate_data=1 to get accompanying climate data. Do not perform advanced filtering using the API tools besides network and state, instead perform filtering in your own custom analysis later.

        4. Present the data summary to the user and any obvious phenology insights from the data summary, ask if the user would like to:
           - Refine the parameters for querying (if yes, return to step 2)
        Otherwise:
           - Export the raw data for further analysis (the user must have the MCP filesystem enabled)
           - Proceed to mapping

        5. When exporting data, use these steps:
           - First enable file export: Use the enable-file-export tool and ask the user for the desired filepath
           - Then export the data: Use the export-raw-data tool with the hash_id from the appropriate query
           - Save data in JSON or JSONL format for easy processing

        6. For mapping, adapt and execute this code template with modifications based on the data selected:
            - If the user has context7 enabled, use that to check any necessary code docs.
            - This prompt ends with an example code snippet used to create a map visualizations

        7. When creating the map:
           - First create a basic map with no coloring to see observation distribution
           - Then ask the user which variable to use for coloring
           - Good color variables: species_common_name, phenophase_name, or other categorical fields with <10 unique values
           - Avoid using: state, latitude, longitude, continuous numeric variables or any variable with "id" in the name

        8. After presenting the map, ask the user what they think of the map and offer to:
           - Adjust the color scheme or variable
           - Filter the data differently
           - Export a different subset of data
           - Finally, direct the user to https://data.usanpn.org/vis-tool/#/ for better interactive visualizations

        <code-snippet>
        {code_snippet}
        </code-snippet>
        """,
        "code_snippet": """
```python
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
from shapely.geometry import Point
from datetime import datetime, timedelta
import os

# Load data from all New England state files
data_files = {
    'ME': 'red_maple_flowering_maine_2023.jsonl',
    'NH': 'new_hampshire_red_maple_2023.jsonl',
    'VT': 'vermont_red_maple_2023.jsonl',
    'MA': 'massachusetts_red_maple_2023.jsonl',
    'CT': 'connecticut_red_maple_2023.jsonl'
}

all_data = []
state_counts = {}

base_path = "/Users/nlespera/Projects/usa-npn-mcp-server/text/claude-agent-home/"

for state, filename in data_files.items():
    filepath = os.path.join(base_path, filename)
    if os.path.exists(filepath):
        state_data = []
        with open(filepath, "r") as f:
            for line in f:
                entry = json.loads(line)
                state_data.append(entry)
        state_counts[state] = len(state_data)
        all_data.extend(state_data)
        print(f"Loaded {len(state_data)} records from {state}")
    else:
        print(f"File not found: {filename}")

print(f"\nTotal records loaded: {len(all_data)}")
print(f"State breakdown: {state_counts}")

# Filter to only records with valid coordinates and exclude March 18-22 (day 77-81)
filtered_data = []
excluded_count = 0
for entry in all_data:
    # Check for valid coordinates
    if (entry.get('longitude', -9999) == -9999 or
        entry.get('latitude', -9999) == -9999 or
        not entry.get('longitude') or not entry.get('latitude')):
        continue

    # Check for March 18-22 exclusion (day 77-81 in 2023)
    first_doy = entry.get('mean_first_yes_doy', -9999)
    last_doy = entry.get('mean_last_yes_doy', -9999)

    exclude = False
    if first_doy != -9999 and 77 <= first_doy <= 81:
        exclude = True
    if last_doy != -9999 and 77 <= last_doy <= 81:
        exclude = True

    if exclude:
        excluded_count += 1
    else:
        filtered_data.append(entry)

print(f"Records with valid coordinates: {len(filtered_data)}")
print(f"Records excluded for March 18-22: {excluded_count}")

# Create state breakdown for filtered data
filtered_state_counts = {}
for entry in filtered_data:
    state = entry['state']
    filtered_state_counts[state] = filtered_state_counts.get(state, 0) + 1

print(f"Valid records by state: {filtered_state_counts}")

# Load US states background map
us_states = gpd.read_file(
    "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
)

# Create the plot
fig, ax = plt.subplots(figsize=(12, 14))

# Filter US states to show New England states
new_england_states = ['Maine', 'New Hampshire', 'Vermont', 'Massachusetts', 'Rhode Island', 'Connecticut']

# Filter by state name
ne_states = us_states[us_states['name'].isin(new_england_states)]

ne_states.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.3)

# Add state labels
state_centers = {
    'Maine': (-69.0, 45.5),
    'New Hampshire': (-71.5, 44.0),
    'Vermont': (-72.8, 44.0),
    'Massachusetts': (-71.5, 42.3),
    'Rhode Island': (-71.4, 41.6),
    'Connecticut': (-72.7, 41.6)
}

for state, (lon, lat) in state_centers.items():
    ax.text(lon, lat, state.upper(), fontsize=10, fontweight='bold',
           ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.6))

# Add major city labels for reference
cities = {
    'Portland, ME': (-70.26, 43.66),
    'Bangor, ME': (-68.77, 44.80),
    'Boston, MA': (-71.06, 42.36),
    'Concord, NH': (-71.54, 43.21),
    'Montpelier, VT': (-72.58, 44.26),
    'Hartford, CT': (-72.69, 41.77),
    'Providence, RI': (-71.42, 41.82)
}

for city, (lon, lat) in cities.items():
    ax.text(lon, lat, city, fontsize=8, ha='center', va='bottom',
           bbox=dict(boxstyle="round,pad=0.1", facecolor="lightyellow", alpha=0.5))

# Create points from filtered data
points = [Point(entry["longitude"], entry["latitude"]) for entry in filtered_data]
gdf = gpd.GeoDataFrame(filtered_data, geometry=points)

print(f"Mapping {len(gdf)} observations from {len(set([d['site_id'] for d in filtered_data]))} sites")

# Color by phenophase type
if not gdf.empty:
    # Get unique phenophases and assign colors
    unique_phenophases = list(set([d['phenophase_description'] for d in filtered_data]))
    colors = ['#e74c3c', '#3498db', '#f39c12']  # Red, Blue, Orange
    phenophase_colors = {pheno: colors[i] for i, pheno in enumerate(unique_phenophases)}

    print(f"\nPhenophase color mapping:")
    for pheno, color in phenophase_colors.items():
        print(f"  {pheno}: {color}")
    # Plot each phenophase with different colors
    for phenophase in unique_phenophases:
        subset = gdf[gdf['phenophase_description'] == phenophase]
        subset.plot(ax=ax, marker="o", color=phenophase_colors[phenophase],
                   label=phenophase, markersize=100, edgecolor='black', linewidth=1.0)

    # Set map bounds to show all of New England
    ax.set_xlim(-73.8, -66.0)
    ax.set_ylim(40.0, 47.8)
else:
    print("Warning: No valid observations to map")

# Labels and title
plt.xlabel("Longitude")
plt.ylabel("Latitude")
title_text = "Red Maple Flowering Observations in New England 2023"
plt.title(title_text, fontsize=16, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the map
plt.savefig("/Users/nlespera/Projects/usa-npn-mcp-server/text/claude-agent-home/red_maple_new_england_complete_map.png",
           dpi=300, bbox_inches="tight")
plt.show()
```
""",
    }
}


def get_prompts() -> list[Prompt]:
    """
    Extract and return a list of Prompt objects from the PROMPTS dictionary.

    Returns
    -------
        list[Prompt]: A list of Prompt objects extracted from the PROMPTS dictionary.
    """
    return [each["prompt"] for each in PROMPTS.values()]
