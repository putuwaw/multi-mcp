import math
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


mcp = FastMCP("Demo")


class SquareRootOutput(BaseModel):
    result: float
    is_error: bool


class SquareRootInput(BaseModel):
    number: float


@mcp.tool(
    name="square_root",
    description="Calculate square root",
    structured_output=True,
)
async def square_root(input: SquareRootInput) -> SquareRootOutput:
    """Calculate square root"""
    if input.number < 0:
        return SquareRootOutput(result=0.0, is_error=True)
    return SquareRootOutput(result=math.sqrt(input.number), is_error=False)


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
