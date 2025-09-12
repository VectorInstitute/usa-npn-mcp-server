"""Sphinx extension to generate MCP Tool, Prompt, and Resource documentation."""

from typing import Any, Dict, List

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from usa_npn_mcp_server.utils.endpoints import NPNTools
from usa_npn_mcp_server.utils.prompts import PROMPTS
from usa_npn_mcp_server.utils.resources import MCP_RESOURCES


class MCPToolsDirective(SphinxDirective):
    """Directive to insert MCP tools documentation."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> List[nodes.Node]:
        """Generate the tools documentation."""
        # Collect all tools
        tools = []
        for attr_name in dir(NPNTools):
            if not attr_name.startswith("_"):  # Ignore private attributes
                tool = getattr(NPNTools, attr_name)  # Each tool in NPNTools
                if hasattr(tool, "name") and hasattr(tool, "docs_one_liner"):
                    tools.append(tool)

        # Sort tools by name
        tools.sort(key=lambda x: x.name)

        # Create a bullet list node directly
        bullet_list = nodes.bullet_list()

        for tool in tools:
            # Create list item
            list_item = nodes.list_item()

            # Create paragraph with inline code and text
            paragraph = nodes.paragraph()
            paragraph += nodes.literal(text=tool.name)  # `tool-name`
            paragraph += nodes.Text(" - ")
            paragraph += nodes.Text(tool.docs_one_liner)

            list_item += paragraph
            bullet_list += list_item

        return [bullet_list]


class MCPPromptsDirective(SphinxDirective):
    """Directive to insert MCP prompts documentation."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> List[nodes.Node]:
        """Generate the prompts documentation."""
        # Create a bullet list node directly
        bullet_list = nodes.bullet_list()

        for prompt_data in PROMPTS.values():
            prompt = prompt_data["prompt"]

            # Create list item
            list_item = nodes.list_item()

            # Create paragraph with inline code and text
            paragraph = nodes.paragraph()
            paragraph += nodes.literal(text=prompt.name)  # `prompt-name`
            paragraph += nodes.Text(" - ")
            paragraph += nodes.Text(str(prompt.description))

            list_item += paragraph
            bullet_list += list_item

        return [bullet_list]


class MCPResourcesDirective(SphinxDirective):
    """Directive to insert MCP resources documentation."""

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> List[nodes.Node]:
        """Generate the resources documentation."""
        # Create a bullet list node directly
        bullet_list = nodes.bullet_list()

        for resource in MCP_RESOURCES:
            # Use the resource name and strip the "-resource" suffix for display
            display_name = resource.name.replace("-resource", "")

            # Create list item
            list_item = nodes.list_item()

            # Create paragraph with inline code and text
            paragraph = nodes.paragraph()
            paragraph += nodes.literal(text=display_name)  # `resource-name`
            paragraph += nodes.Text(" - ")
            paragraph += nodes.Text(str(resource.description))

            list_item += paragraph
            bullet_list += list_item

        return [bullet_list]


def _generate_tools_list() -> str:
    """Generate markdown-formatted tools list."""
    tools = []
    for attr_name in dir(NPNTools):
        if not attr_name.startswith("_"):
            tool = getattr(NPNTools, attr_name)
            if hasattr(tool, "name") and hasattr(tool, "docs_one_liner"):
                tools.append(tool)

    tools.sort(key=lambda x: x.name)
    return "\n".join([f"- `{tool.name}` - {tool.docs_one_liner}" for tool in tools])


def _generate_prompts_list() -> str:
    """Generate markdown-formatted prompts list."""
    prompts_list = []
    for prompt_data in PROMPTS.values():
        prompt = prompt_data["prompt"]
        prompts_list.append((prompt.name, prompt.description))

    return "\n".join([f"- `{name}` - {desc}" for name, desc in prompts_list])


def _generate_resources_list() -> str:
    """Generate markdown-formatted resources list."""
    resources_list = []
    for resource in MCP_RESOURCES:
        display_name = resource.name.replace("-resource", "")
        resources_list.append((display_name, resource.description))

    return "\n".join([f"- `{name}` - {desc}" for name, desc in resources_list])


def update_markdown_with_generated_content(
    app: Sphinx, docname: str, source: List[str]
) -> None:
    """
    Process source files to replace HTML markers with generated content.

    This handles both Sphinx docs and external files like README.md.
    """
    if not source:
        return

    content = source[0]

    # Replace MCP tools markers
    if "<!-- MCP-TOOLS-START -->" in content and "<!-- MCP-TOOLS-END -->" in content:
        tools_content = _generate_tools_list()
        start_marker = "<!-- MCP-TOOLS-START -->"
        end_marker = "<!-- MCP-TOOLS-END -->"
        start_idx = content.index(start_marker) + len(start_marker)
        end_idx = content.index(end_marker)

        content = content[:start_idx] + "\n" + tools_content + "\n" + content[end_idx:]

    # Replace MCP prompts markers
    if (
        "<!-- MCP-PROMPTS-START -->" in content
        and "<!-- MCP-PROMPTS-END -->" in content
    ):
        prompts_content = _generate_prompts_list()
        start_marker = "<!-- MCP-PROMPTS-START -->"
        end_marker = "<!-- MCP-PROMPTS-END -->"
        start_idx = content.index(start_marker) + len(start_marker)
        end_idx = content.index(end_marker)

        content = (
            content[:start_idx] + "\n" + prompts_content + "\n" + content[end_idx:]
        )

    # Replace MCP resources markers
    if (
        "<!-- MCP-RESOURCES-START -->" in content
        and "<!-- MCP-RESOURCES-END -->" in content
    ):
        resources_content = _generate_resources_list()
        start_marker = "<!-- MCP-RESOURCES-START -->"
        end_marker = "<!-- MCP-RESOURCES-END -->"
        start_idx = content.index(start_marker) + len(start_marker)
        end_idx = content.index(end_marker)

        content = (
            content[:start_idx] + "\n" + resources_content + "\n" + content[end_idx:]
        )

    source[0] = content


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up the Sphinx extension."""
    # Register directives for use in Sphinx docs (index.md)
    app.add_directive("mcp-tools", MCPToolsDirective)
    app.add_directive("mcp-prompts", MCPPromptsDirective)
    app.add_directive("mcp-resources", MCPResourcesDirective)

    # Register source-read event for HTML marker replacement (README.md)
    app.connect("source-read", update_markdown_with_generated_content)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
