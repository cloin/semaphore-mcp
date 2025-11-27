FROM python:3.12-slim

# OCI image labels
LABEL org.opencontainers.image.title="semaphore-mcp"
LABEL org.opencontainers.image.description="Model Context Protocol (MCP) server for SemaphoreUI automation"
LABEL org.opencontainers.image.source="https://github.com/cloin/semaphore-mcp"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"

WORKDIR /app

# Copy license and files needed for installation
COPY LICENSE .
COPY pyproject.toml .
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir .

# Default environment variables
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

ENTRYPOINT ["semaphore-mcp"]
