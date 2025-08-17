FROM ubuntu:22.04

# install python and docker
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    gnupg \
    lsb-release && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# run ollama
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3.2:3b

# copy all files
COPY . .

# install dependencies using uv
RUN uv sync --frozen

# run the example
CMD ["bash", "-c", "nohup ollama serve > ollama.log 2>&1 & uv run python example.py"]