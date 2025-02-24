# National Phenology Network MCP Server

----------------------------------------------------------------------------------------

[![code checks](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/code_checks.yml)
[![integration tests](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/docs_deploy.yml/badge.svg)](https://github.com/VectorInstitute/usa-npn-mcp-server/actions/workflows/docs_deploy.yml)
[![codecov](https://codecov.io/github/VectorInstitute/usa-npn-mcp-server/graph/badge.svg?token=83MYFZ3UPA)](https://codecov.io/github/VectorInstitute/usa-npn-mcp-server)
![GitHub License](https://img.shields.io/github/license/VectorInstitute/usa-npn-mcp-server)

### Available Tools

- `observations` - Fetches observations data based on given criteria.
- `observation_comment` - Fetches observation comments data based on given criteria.

## 🧑🏿‍💻 Developing

### Installing dependencies

The development environment can be set up using
[uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). Hence, make sure it is
installed and then run:

```bash
git clone https://github.com/VectorInstitute/usa-npn-mcp-server.git
cd usa-npn-mcp-server
uv sync
source .venv/bin/activate
```

In order to install dependencies for testing (codestyle, unit tests, integration tests),
run:

```bash
uv sync --dev
source .venv/bin/activate
```

These commands set up the `.venv` environment as specified in the `pyproject.toml` and `uv.lock` files.

## Configuration

### Configure for Claude Desktop App

Add to your `claude_desktop_config.json`, found easiest through the Claude Desktop settings:

<details>
<summary>Add to claude config: </summary>

```json
"mcpServers": {
  "npn": {
    "command": "bash",
    "args": [
      "-c",
      # replace /absolute/path/to/usa-npn-mcp-server/ with local path to repo dir
      "source /absolute/path/to/usa-npn-mcp-server/.venv/bin/activate && uv run usa-npn-mcp-server"
    ]
  }
}
```
</details>


You'll need to restart Claude Desktop, you should see a new :electric_plug: icon and/or :hammer: icons in your chat prompt that confirms the MCP Server is detected.

Each time you create a new chat that queries NPN's API through the MCP Server, you will have to agree to permit access to the MCP Server's Tool.

## Debugging

**Debugging with MCP Inspector**: To run a locally hosted MCP interpreter for debugging, use:

   ```bash
   npx @modelcontextprotocol/inspector uvx usa-npn-mcp-server
   ```
  
The first time you run this command you'll be prompted to download `@modelcontextprotocol/inspector`. 

This command starts the MCP inspector within the `uv`-managed environment. The inspector can be used locally in-browser to inspect/test the server.

## Other MCP Servers

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers