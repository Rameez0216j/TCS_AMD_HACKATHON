# math_server.py
import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Initialize FastMCP for Math operations
mcp = FastMCP("Math Server")


@mcp.tool
def add(a: float, b: float) -> float:
    """
    Adds two numbers together.
    """
    return a + b


@mcp.tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers together.
    """
    return a * b


if __name__ == "__main__":
    # Run the server on the default stdio transport protocol
    mcp.run(transport="stdio")
