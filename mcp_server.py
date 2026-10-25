"""Expose FitFindr listing search through MCP."""

from mcp.server.fastmcp import FastMCP
from tools import search_listings as _search_listings_impl

mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search mock clothing listings by description keywords, optional size,
    and an inclusive maximum price in US dollars.
    Return ranked listing dictionaries, or [] when nothing matches.
    """
    return _search_listings_impl(description, size, max_price)


if __name__ == "__main__":
    mcp.run()
