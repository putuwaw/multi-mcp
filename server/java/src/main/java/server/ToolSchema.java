package server;

/**
 * References: <a href="https://modelcontextprotocol.io/docs/concepts/tools#tool-definition-structure">MCP Tool definition structure</a>
 */
public final class ToolSchema {

    private static final String CSV_HEAD_SCHEMA = """
        {
          "type": "object",
          "id": "urn:jsonschema:Operation",
          "properties": {
            "n": {
              "type": "number"
            }
          }
        }
        """;

    private ToolSchema() {
        // Prevent instantiation
    }

    public static String csvHead() {
        return CSV_HEAD_SCHEMA;
    }
}
