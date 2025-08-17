import math
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")


@mcp.tool(
    name="square_root",
    description="Calculate square root"
)
async def square_root(number: float) -> float:
    """Calculate square root"""
    return math.sqrt(number)


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
