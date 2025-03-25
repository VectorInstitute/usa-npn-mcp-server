"""Plottiing Module for MCP Server plotting functions."""

import base64
import io
from typing import Any, Dict

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import to_hex
from shapely.geometry import Point


def generate_map(data: list[Dict[str, Any]], colour_by: str) -> str:
    """
    Generate a map with lat/long as axes, overlaying a US map with state outlines.

    Parameters
    ----------
    data : list[dict]
        The input data containing latitude and longitude.
    colour_by : str
        The variable to color the points by.

    Returns
    -------
    str
        Base64 encoded image of the map.
    """
    if not data:
        raise ValueError("Data cannot be empty.")

    # Load a GeoDataFrame of US states
    us_states = gpd.read_file(
        "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    )
    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 9))
    us_states.plot(ax=ax, color="white", edgecolor="black")

    # Create a GeoDataFrame for the input data
    points = [
        Point(entry["longitude"], entry["latitude"])
        for entry in data
        if "longitude" in entry and "latitude" in entry
    ]
    gdf = gpd.GeoDataFrame(data, geometry=points)

    if colour_by:
        # Extract unique categories and assign colors
        cats = {entry[colour_by] for entry in data if colour_by in entry}
        colormap = cm.get_cmap("tab10", len(cats))
        cats_colors = {sp: to_hex(colormap(i)) for i, sp in enumerate(cats)}
        # Plot the data points
        for sp in cats:
            subset = gdf[gdf[colour_by] == sp]
            subset.plot(
                ax=ax,
                marker="o",
                color=cats_colors[sp],
                label=sp,
                markersize=14,
            )
        plt.legend(
            title=colour_by,
            bbox_to_anchor=(1.05, 1),  # Position legend outside the plot
            loc="upper left",
            borderaxespad=0,
            frameon=True,
        )
    else:
        gdf.plot(
            ax=ax,
            marker="o",
            color="red",
            label="Observations",
            markersize=14,
        )

    # Dynamically adjust the map extent to center on the observations
    min_lon = gdf.geometry.x.min()
    max_lon = gdf.geometry.x.max()
    min_lat = gdf.geometry.y.min()
    max_lat = gdf.geometry.y.max()
    ax.set_xlim(min_lon - 1, max_lon + 1)
    ax.set_ylim(min_lat - 1, max_lat + 1)

    # Customize the plot
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    if colour_by:
        plt.title(f"Map of Observations Colored by {colour_by}")
    plt.grid(True)

    # Adjust layout to make space for the legend
    plt.tight_layout(rect=(0, 0, 0.85, 1))  # Leave space on the right for the legend

    # Save the map to a byte buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="jpg", bbox_inches="tight")
    plt.close()
    buffer.seek(0)

    # Encode the image in base64
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return encoded_image
