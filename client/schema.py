from typing import Dict, Tuple

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import ClientSession
from pydantic import BaseModel
from mcp.types import Tool


class MCPServerConfig(BaseModel):
    command: str
    args: list[str]


class MultiMCPTool(Tool):
    server: str


class MCPClient:
    def __init__(self):
        self.session: Dict[str, ClientSession] = {}
        self.stdio_transport: Dict[
            str, Tuple[MemoryObjectReceiveStream, MemoryObjectSendStream]
        ] = {}
        self.mcp_servers: Dict[str, MCPServerConfig] = {}
