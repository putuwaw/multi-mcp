from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")


@mcp.tool(
    name="Get weather",
    description="Get the current weather for a specified location",
)
async def get_weather(location: str) -> str:
    """Get the weather for a given location"""
    return f"The weather in {location} is sunny!"


@mcp.prompt(
    name="Review error code",
    description="Review the provided code and suggest fixes for any errors.",
)
def review_code(code: str) -> str:
    return f"Please review this code and fix the error:\n{code}"


@mcp.resource(
    uri="resource://config",
    name="Configuration Resource",
    description="A resource containing configuration data.",
    mime_type="application/json",
)
def get_config() -> dict:
    return {
        "tempature": 0.6,
        "top-k": 1,
        "max_tokens": 2048,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
