---
hide-toc: true
---

# USA-NPN MCP Server Documentation

```{toctree}
:hidden:

user_guide
reference/api/usa_npn_mcp_server
```

Welcome to the documentation for the USA National Phenology Network (USA-NPN) MCP Server. This server is intended for phenologists and developers to access, analyze, and manage phenological data efficiently and work with AI Agents in phenology. This MCP Server is also designed to reduce barriers to citizen scientists interested in phenology and looking for a natural language tool, this can nurture phenology interests and drive data collection improvement efforts.

The MCP Server is designed to support:

- **Phenologists**: Researchers and practitioners studying the timing of biological events, often in relation to environmental changes and climate.
- **Developers**: Engineers and data scientists integrating phenological data into applications or workflows.
- **Citizen Scientists**: Members of the public interested in phenological data exploration currently experiencing technical barriers.


## Key Features

- **Data Access Tools**: Access phenological data through specialized tools including status/intensity observations, site and individual phenometrics, magnitude data, and mapping capabilities.
- **Customizable Queries**: Filter and query data based on dates, species, location, phenophase etc.
- **Visualizations**: Mapping and plotting of phenological data.
- **Data Analysis**: Tools for analyzing trends and patterns in phenological data.
- **File Export**: Export raw data to JSON or JSONL files within configured directories.
- **Documentation**: Comprehensive examples and guides for using the server's features.

### Available MCP Tools

- `status-intensity` - Fetches status and intensity data (raw observation data).
- `individual-phenometrics` - Fetches individual phenometrics (summarized data).
- `site_phenometrics` - Fetches site phenometrics (site-level data).
- `magnitude-phenometrics` - Fetches magnitude phenometrics (magnitude data).
- `observation-comment` - Fetches observation comments based on observation_id.
- `mapping` - Maps site phenometrics onto a map of the USA with optional colour labelling.
- `check-reference-material` - Checks database containing NPN API reference material using a generated sql query.
- `check-literature` - Queries database of structured summaries from 175 papers that use phenology and phenometrics data.
- `export-raw-data` - Exports raw data to JSON or JSONL files in allowed directories.
- `get-raw-data` - Fetches raw data instead of summaries as from other tools.

### Available MCP Resources

- `recent-queries` - List of recent query hash IDs and metadata for cached data access.
- `available-roots` - List of available root directories for file export operations.

### Available MCP Prompts

- `map_data` - Structured workflow for working interactively with user to query site phenometrics and map the results, initialized with start-date and end-date.

## Overview

- **[User Guide](./user_guide.md)**: Step-by-step instructions for accessing and using the MCP Server's features. Also, learn more about MCP and AI Agents.
- **[API Reference](./reference/api/usa_npn_mcp_server.rst)**: Complete documentation of all classes, functions, and tools available in the MCP Server.
