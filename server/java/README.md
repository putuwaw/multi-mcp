# Multi MCP Java Server

MCP Server in Java.

## Try the MCP
Pull the Docker image:
```
docker pull putuwaw/multi-mcp-java-server
```

Try the MCP using Postman (forward port 4040 to see the Spark UI):
```
docker run -i --rm -p 4040:4040 putuwaw/multi-mcp-java-server
```