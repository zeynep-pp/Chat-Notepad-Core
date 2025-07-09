from fastmcp import FastMCP, Client
import asyncio

mcp = FastMCP(
    name="TestServer",
    instructions="""
        This server has information about the recent election in NY.
    """,
)

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
