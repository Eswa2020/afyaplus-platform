# hello_mcp.py - the smallest possible MCP server: one tool
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("afyaplus-hello")

@mcp.tool()
def say_hello(name: str) -> str:
    """Greet a person by name. Use this to test that the server is alive."""
    return f"Hello {name}, the AfyaPlus MCP server is running."

if __name__ == "__main__":
    mcp.run()