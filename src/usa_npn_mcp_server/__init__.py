"""Entry point for the MCP NPN Server."""

import asyncio
import logging
import sys

import click

from usa_npn_mcp_server.server import serve


@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose: int = 2) -> None:
    """Run the MCP NPN Server."""
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    asyncio.run(serve())


if __name__ == "__main__":
    main()
