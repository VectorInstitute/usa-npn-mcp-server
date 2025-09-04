"""Entry point for the MCP NPN Server."""

import asyncio
import logging
import sys

import click

from usa_npn_mcp_server.server import serve


@click.command()
@click.option("-v", "--verbose", count=True)
@click.argument(
    "allowed_dirs",
    nargs=-1,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=str),
)
def main(verbose: int = 2, allowed_dirs: tuple[str, ...] = ()) -> None:
    """
    Run the MCP NPN Server.

    Parameters
    ----------
    verbose : int, optional
        Verbosity level for logging (default is 2).
    allowed_dirs : tuple[str, ...], optional
        A tuple of directory paths that are allowed for file export operations.

    Returns
    -------
    None
    """
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
    asyncio.run(serve(allowed_dirs))


if __name__ == "__main__":
    main()
