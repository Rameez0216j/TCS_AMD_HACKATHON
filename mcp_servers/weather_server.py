# weather_server.py
from fastmcp import FastMCP

# Initialize FastMCP for Weather tracking
mcp = FastMCP("Weather Server")

@mcp.tool
def get_weather(location: str) -> str:
    """
    Retrieves the current weather report and temperature details for a given city.
    """
    loc = location.lower()
    if "london" in loc:
        return "The weather in London is currently rainy, 14°C with 82% humidity."
    elif "new york" in loc or "nyc" in loc:
        return "The weather in New York is cloudy, 18°C with 55% humidity."
    else:
        return f"The weather in {location} is currently bright and sunny, 25°C."

if __name__ == "__main__":
    mcp.run(transport="stdio")