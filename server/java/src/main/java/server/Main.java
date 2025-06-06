package server;

import io.modelcontextprotocol.server.McpAsyncServer;
import io.modelcontextprotocol.server.McpServer;
import io.modelcontextprotocol.server.McpServerFeatures;
import io.modelcontextprotocol.server.transport.StdioServerTransportProvider;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.modelcontextprotocol.spec.McpSchema;
import io.modelcontextprotocol.spec.McpSchema.Tool;
import io.modelcontextprotocol.spec.McpSchema.CallToolResult;

import org.jetbrains.annotations.NotNull;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import reactor.core.publisher.Mono;

public class Main {
    private static final Logger logger = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        ObjectMapper objectMapper = new ObjectMapper();
        StdioServerTransportProvider transportProvider = new StdioServerTransportProvider(objectMapper);

        var capabilities = McpSchema.ServerCapabilities.builder()
                .tools(true)
                .logging()
                .build();
        McpAsyncServer asyncServer = McpServer.async(transportProvider)
                .serverInfo("Demo", "0.1.0")
                .capabilities(capabilities)
                .build();

        var csvToolSpec = getAsyncToolSpecification();
        asyncServer.addTool(csvToolSpec)
                .doOnSuccess(v -> logger.info("Tool csv registered"))
                .doOnError(v -> logger.info("Failed to register csv tool"))
                .subscribe();
    }

    private static McpServerFeatures.@NotNull AsyncToolSpecification getAsyncToolSpecification() {
        String csv_schema = ToolSchema.csvHead();
        return new McpServerFeatures.AsyncToolSpecification(
                new Tool("iris_csv", "Get top data for iris csv", csv_schema),
                (exchange, arguments) -> {
                    SparkCSV sparkCSV = new SparkCSV();
                    String result;
                    try {
                        Integer n_row = (Integer) arguments.get("n");
                        result = sparkCSV.getRow(n_row);
                    } catch (ClassCastException e) {
                        return Mono.just(new CallToolResult("Failed to cast int: " + e.getMessage(), true));
                    } catch (Exception e) {
                        return Mono.just(new CallToolResult("Failed to get iris data: " + e.getMessage(), true));
                    }
                    return Mono.just(new CallToolResult(result, false));
                }
        );
    }
}