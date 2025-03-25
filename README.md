# National Phenology Network MCP Server

----------------------------------------------------------------------------------------

[![code checks](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/code_checks.yml)
[![integration tests](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/docs_deploy.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/docs_deploy.yml)
![GitHub License](https://img.shields.io/github/license/VectorInstitute/usa-npn-mcp-server)

### Available Tools

- `status_intensity` - Fetches status and intensity data (raw observation data).
- `individual_phenometrics` - Fetches individual phenometrics (summarized data).
- `site_phenometrics` - Fetches site phenometrics (site-level data).
- `magnitude_phenometrics` - Fetches magnitude phenometrics (magnitude data).
- `observation_comment` - Fetches observation comments based on observation_id.
- `mapping` - Maps site phenometrics onto a map of the USA with optional colour labelling.

## Example usage

![alt text](assets/example_usage.gif)

## Configuration

### Configure for Claude Desktop App

You will need to modify your `claude_desktop_config.json` to make it aware of the MCP Server:

<details>
<summary>How to easily find claude_desktop_config.json on macOS:</summary>

1. Open Claude Desktop app
2. Click on "Claude" in the menu bar and select "Settings"
3. In the Settings window, click on the "Developer" tab in the left sidebar
4. Click the "Edit Config" button
5. This will open a Finder window showing the location of the `claude_desktop_config.json` file
6. Open the file with your preferred text editor
</details>

<details>
<summary>Add to claude config:</summary>

```json
"mcpServers": {
  "npn": {
    "command": "bash",
    "args": [
      "-c",
      # replace /absolute/path/to/usa-npn-mcp-server/ with local path to repo dir
      "source /absolute/path/to/usa-npn-mcp-server/.venv/bin/activate && uv run usa_npn_mcp_server"
    ]
  }
}
```
</details>


After saving the changes, restart Claude Desktop. You should see a new :electric_plug: icon and/or :hammer: icons in your chat prompt that confirms the MCP Server is detected.

![alt text](assets/mcp_recognized.png)

Each time you create a new chat that uses a Tool from the MCP Server, you will have to agree to permit access to the MCP Server's Tool.

![alt text](assets/accept_tool.png)

## 🧑🏿‍💻 Developing

### Clone the repository

Using HTTPS (recommended for most users):
   ```bash
   git clone https://github.com/VectorInstitute/usa-npn-mcp-server.git
   ```

Using SSH (if you have SSH keys configured with GitHub):
   ```bash
   git clone git@github.com:VectorInstitute/usa-npn-mcp-server.git
   ```

After cloning with either method:
  ```bash
  cd usa-npn-mcp-server
  ```

### Installing dependencies

The development environment can be set up using
[uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). Hence, make sure it is installed and then run:

```bash
uv sync
source .venv/bin/activate
```

In order to install dependencies for testing (codestyle, unit tests, integration tests),
run:

```bash
uv sync --dev
source .venv/bin/activate
```

These commands set up and activate the `.venv` environment as specified in the `pyproject.toml` and `uv.lock` files.

## Debugging

**Debugging with MCP Inspector**: To run a locally hosted MCP interpreter for debugging, use:

   ```bash
   npx @modelcontextprotocol/inspector uv run usa_npn_mcp_server
   ```

The first time you run this command you'll be prompted to download `@modelcontextprotocol/inspector`.

This command starts the MCP inspector within the `uv`-managed environment. The inspector can be used locally in-browser to inspect/test the server.

## Other MCP Servers

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers
