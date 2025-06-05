run:
	@java -Djava.security.manager=allow \
		--add-exports java.base/sun.nio.ch=ALL-UNNAMED \
		--add-exports java.base/sun.util.calendar=ALL-UNNAMED \
		--add-opens java.base/java.lang=ALL-UNNAMED \
		--add-opens java.base/java.util=ALL-UNNAMED \
		-jar target/multi-mcp-java-server-1.0-SNAPSHOT.jar

package:
	@mvn clean package
