import asyncio
import json
from contextlib import AsyncExitStack
from typing import List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from schema import (
    MCPClient,
    MCPServerConfig,
)
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    TextResourceContents,
    BlobResourceContents,
)
from ollama import Tool, chat, Message


async def main():
    client = MCPClient()
    list_tools: List[Tool] = []
    model_name = "llama3.2:3b"

    with open("server.json", "r") as f:
        server_json = json.load(f)
        mcp_servers: dict = server_json["mcpServers"]
        for server, value in mcp_servers.items():
            client.mcp_servers[server] = MCPServerConfig.model_validate(value)

    async with AsyncExitStack() as stack:
        for server, value in client.mcp_servers.items():
            server_params = StdioServerParameters(
                command=value.command,
                args=value.args,
            )

            transport = await stack.enter_async_context(stdio_client(server_params))
            read_stream, write_stream = transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()
            client.session[server] = session
            print(f"Successfully connected to server: {server}")

            response = await session.list_tools()
            tools = response.tools

            for tool in tools:
                tool = Tool(
                    function=Tool.Function(
                        # add server name to prevent name conflicts between different servers
                        name=f"{server}_{tool.name}",
                        description=tool.description,
                        parameters=Tool.Function.Parameters(
                            type=tool.inputSchema.get("type", "object"),
                            properties=tool.inputSchema.get("properties", {}),
                            required=tool.inputSchema.get("required"),
                        ),  # type: ignore
                    )
                )
                list_tools.append(tool)

        messages: List[Message] = []
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit" or user_input.lower() == "quit":
                break

            messages.append(Message(role="user", content=user_input))

            response = chat(
                model=model_name,
                messages=messages,
                tools=list_tools,
            )

            messages.append(response.message)
            if response.message.tool_calls:
                for tool in response.message.tool_calls:
                    server_name = tool.function.name.split("_")[0]
                    original_tool_name = tool.function.name.split("_", 1)[1]

                    print(
                        f"Calling tool: {tool.function.name} with arguments: {tool.function.arguments}"
                    )
                    output = await client.session[server_name].call_tool(
                        original_tool_name, dict(tool.function.arguments)
                    )

                    final_output = ""
                    for content in output.content:
                        if isinstance(content, TextContent):
                            final_output += content.text
                        elif isinstance(content, ImageContent):
                            final_output += f"[Image: {content.data}]"
                        elif isinstance(content, EmbeddedResource):
                            if isinstance(content.resource, TextResourceContents):
                                final_output += f"[Resource: {content.resource.text}]"
                            elif isinstance(content.resource, BlobResourceContents):
                                final_output += f"[Resource: {content.resource.uri}]"

                    print(f"Tool output: {output}")
                    messages.append(
                        Message(
                            role="tool",
                            content=final_output,
                            tool_name=tool.function.name,
                        )
                    )

            final_response = chat(
                model=model_name,
                messages=messages,
            )
            print(f"LLM: {final_response.message.content}")
            messages.append(final_response.message)

        print("Closing all sessions...")
    print("All sessions closed.")


if __name__ == "__main__":
    asyncio.run(main())
