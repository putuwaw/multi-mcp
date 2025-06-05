package server;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class SparkCSV {
    // Dataset source: https://data.mendeley.com/datasets/7xwsksdpy3/1
    private static final String CSV_FILENAME = "iris-write-from-docker.csv";
    private final SparkSession spark;
    private final Dataset<Row> df;

    public SparkCSV() {
        this.spark = createSparkSession();
        this.df = loadCsvAsDataFrame();
    }

    private SparkSession createSparkSession() {
        return SparkSession.builder()
                .appName("CSV Reader Example")
                .master("local[*]")
                .getOrCreate();
    }

    private Dataset<Row> loadCsvAsDataFrame() {
        try {
            Path csvPath = resolveCsvPath();
            return spark.read()
                    .option("header", "true")
                    .option("inferSchema", "true")
                    .csv(csvPath.toString());
        } catch (IOException | URISyntaxException e) {
            throw new RuntimeException("Failed to load CSV file: " + SparkCSV.CSV_FILENAME, e);
        }
    }

    private Path resolveCsvPath() throws IOException, URISyntaxException {
        URL resource = getClass().getClassLoader().getResource(SparkCSV.CSV_FILENAME);

        if (resource == null) {
            throw new IllegalArgumentException(SparkCSV.CSV_FILENAME + " not found!");
        }

        if ("file".equals(resource.getProtocol())) {
            // Development environment
            return Paths.get(resource.toURI());
        } else {
            // Running from JAR
            try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream(SparkCSV.CSV_FILENAME)) {
                if (inputStream == null) {
                    throw new IllegalArgumentException(SparkCSV.CSV_FILENAME + " not found in JAR!");
                }

                Path tempFile = Files.createTempFile("iris-temp-", ".csv");
                tempFile.toFile().deleteOnExit();
                Files.copy(inputStream, tempFile, StandardCopyOption.REPLACE_EXISTING);
                return tempFile;
            }
        }
    }

    public String getRow(Integer n) {
        List<Row> rows = df.takeAsList(n);
        StructType schema = df.schema();
        List<Map<String, Object>> result = new ArrayList<>();

        for (Row row : rows) {
            Map<String, Object> rowMap = new LinkedHashMap<>();
            for (StructField field : schema.fields()) {
                rowMap.put(field.name(), row.getAs(field.name()));
            }
            result.add(rowMap);
        }

        return result.toString();
    }
}
