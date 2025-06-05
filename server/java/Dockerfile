FROM eclipse-temurin:23-jdk

WORKDIR /app

RUN apt-get update && \
    apt-get install -y maven make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . . 

RUN mvn clean package

CMD ["make", "run"]
