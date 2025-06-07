import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from schema import MCPClient, MCPServerConfig, MultiMCPTool


def prompt_for_args(input_schema: dict) -> dict | None:
    args = {}
    for key in input_schema["required"]:
        key_dtype = input_schema["properties"][key]["type"]
        value = input(f"Enter value for {key}: ")

        if key_dtype == "number":
            try:
                value = int(value)
            except ValueError:
                print(f"Invalid input for {key}. Expected a number.")
                return None

        args[key] = value
    return args


async def main():
    client = MCPClient()
    list_tools: list[MultiMCPTool] = []

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
            client.stdio_transport[server] = transport

            read_stream, write_stream = transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            client.session[server] = session
            await session.initialize()
            print(f"Successfully connected to server: {server}")

            response = await session.list_tools()
            tools = response.tools

            for tool in tools:
                new_tool = MultiMCPTool(server=server, **tool.model_dump())
                list_tools.append(new_tool)

        print("Available Tools:\n")
        for i, tool in enumerate(list_tools):
            print(f"{i + 1}. [{tool.server}] {tool.name} - {tool.description}")
        while True:
            choice = input("\nSelect a tool by number (or 'quit' to quit): ")
            print("result:", choice)
            if "quit" in choice.lower():
                print("Exiting...")
                break
            try:
                selected_tool = list_tools[int(choice) - 1]
            except (IndexError, ValueError):
                print("Please enter a valid number.")
                continue

            args = prompt_for_args(selected_tool.inputSchema)
            if args is None:
                print("Invalid input. Please try again.")
                continue

            print(f"Calling tool {selected_tool.name} with args: {args}")
            if selected_tool.server == "java":
                print("[INFO] You can open localhost:4040 to see the Spark UI.")
            try:
                result = await client.session[selected_tool.server].call_tool(
                    name=selected_tool.name,
                    arguments=args,
                )
                print(f"Tool call result: {result}")
            except Exception as e:
                print(f"Error calling tool {selected_tool.name}: {e}")
        print("Closing all sessions...")
    print("All sessions closed.")


if __name__ == "__main__":
    asyncio.run(main())
