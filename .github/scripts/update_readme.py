#!/usr/bin/env python3
"""
Script to automatically update README.md with generated MCP asset descriptions.

This script preserves the HTML comment markers while updating the content between them.
"""

import sys
from pathlib import Path


# Add the source directory to Python path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from usa_npn_mcp_server.utils.endpoints import NPNTools
from usa_npn_mcp_server.utils.prompts import PROMPTS
from usa_npn_mcp_server.utils.resources import MCP_RESOURCES


def generate_tools_list() -> str:
    """Generate markdown-formatted tools list."""
    tools = []
    for attr_name in dir(NPNTools):
        if not attr_name.startswith("_"):
            tool = getattr(NPNTools, attr_name)
            if hasattr(tool, "name") and hasattr(tool, "docs_one_liner"):
                tools.append(tool)

    tools.sort(key=lambda x: x.name)
    return "\n".join([f"- `{tool.name}` - {tool.docs_one_liner}" for tool in tools])


def generate_prompts_list() -> str:
    """Generate markdown-formatted prompts list."""
    prompts_list = []
    for prompt_data in PROMPTS.values():
        prompt = prompt_data["prompt"]
        prompts_list.append((prompt.name, prompt.description))

    return "\n".join([f"- `{name}` - {desc}" for name, desc in prompts_list])


def generate_resources_list() -> str:
    """Generate markdown-formatted resources list."""
    resources_list = []
    for resource in MCP_RESOURCES:
        display_name = resource.name.replace("-resource", "")
        resources_list.append((display_name, resource.description))

    return "\n".join([f"- `{name}` - {desc}" for name, desc in resources_list])


def update_content_between_markers(
    content: str, start_marker: str, end_marker: str, new_content: str
) -> str:
    """
    Update content between HTML markers while preserving the markers themselves.

    Args:
        content: Original file content
        start_marker: HTML start marker (e.g., "<!-- MCP-TOOLS-START -->")
        end_marker: HTML end marker (e.g., "<!-- MCP-TOOLS-END -->")
        new_content: Content to insert between markers

    Returns
    -------
        Updated content with new content between markers
    """
    if start_marker not in content or end_marker not in content:
        return content

    start_idx = content.index(start_marker) + len(start_marker)
    end_idx = content.index(end_marker)

    # Replace content between markers, preserving the markers and maintaining formatting
    return content[:start_idx] + "\n" + new_content + "\n" + content[end_idx:]


def main() -> bool:
    """Update README.md with generated content."""
    readme_path = Path(__file__).parent.parent.parent / "README.md"

    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        sys.exit(1)

    # Read current README content
    original_content = readme_path.read_text()
    updated_content = original_content

    # Update MCP tools section
    tools_content = generate_tools_list()
    updated_content = update_content_between_markers(
        updated_content,
        "<!-- MCP-TOOLS-START -->",
        "<!-- MCP-TOOLS-END -->",
        tools_content,
    )

    # Update MCP resources section
    resources_content = generate_resources_list()
    updated_content = update_content_between_markers(
        updated_content,
        "<!-- MCP-RESOURCES-START -->",
        "<!-- MCP-RESOURCES-END -->",
        resources_content,
    )

    # Update MCP prompts section
    prompts_content = generate_prompts_list()
    updated_content = update_content_between_markers(
        updated_content,
        "<!-- MCP-PROMPTS-START -->",
        "<!-- MCP-PROMPTS-END -->",
        prompts_content,
    )

    # Check if content has changed
    if original_content == updated_content:
        print("No changes needed in README.md")
        return False

    # Write updated content back to file
    readme_path.write_text(updated_content)
    print("README.md updated with generated content")
    return True


if __name__ == "__main__":
    changed = main()
    # Exit with code 0 if no changes, 1 if changes (for GitHub Action conditional logic)
    sys.exit(1 if changed else 0)
