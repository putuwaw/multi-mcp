import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { makeBadge } from 'badge-maker'

const server = new McpServer({
  name: "Demo",
  version: "0.1.0"
});

function svgToBase64Data(svgString: string): string {
  const encoded = encodeURIComponent(svgString)
    .replace(/%([0-9A-F]{2})/g, (_match, p1) =>
      String.fromCharCode(parseInt(p1, 16))
    );
  return btoa(encoded);
}

function generateBadge(text: string): string {
  const format = {
    label: "multi-mcp-ts-server",
    message: text,
    color: "brightgreen",
  }
  const base64Svg = svgToBase64Data(makeBadge(format))
  return base64Svg
}

// Add an addition tool (example tool)
server.tool("square_root",
  "Calculate square root",
  { n: z.number() },
  async ({ n }) => ({
    content: [{ type: "text", text: String(Math.sqrt(n)) }],
  })
);

// Another tool that use npm package to generate a badge
server.tool(
  "generate_svg",
  "Generate a svg badge with text",
  { text: z.string() },
  async ({ text }) => {
    try {
      const svg = generateBadge(text);
      return { content: [{ type: "image", data: svg, mimeType: "image/svg+xml" }] };
    } catch (error) {
      console.error("Error generate svg:", error);
      return { content: [{ type: "text", text: `Failed to generate svg` }] };
    }
  }
);

// Add a dynamic greeting resource (example resource)
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [{
      uri: uri.href,
      text: `Hello, ${name}!`
    }]
  })
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);
