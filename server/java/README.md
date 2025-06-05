# Multi MCP Java Server

MCP Server in Java.

## Build:
```
docker build -t mcp-java-server .
```

## Test
Try the MCP using Postman (forward port 4040 to see the Spark UI):
```
docker run -i --rm -p 4040:4040 mcp-java-server
```