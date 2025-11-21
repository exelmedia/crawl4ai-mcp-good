# Dockerfile for Crawl4AI MCP Server
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY setup.py .
COPY src/ src/
COPY README.md .

# Install the package
RUN pip install -e .

# Environment variables (can be overridden at runtime)
ENV CRAWL4AI_URL=https://crawl4ai-u53948.vm.elestio.app
ENV CRAWL4AI_USERNAME=root
# CRAWL4AI_PASSWORD should be set at runtime via -e or docker-compose

# Expose port (optional, MCP uses stdio by default)
ENV PORT=8000
ENV HOST=0.0.0.0

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from crawl4ai_mcp.server import app; print('OK')" || exit 1

# Default command - run MCP server
CMD ["python", "-m", "crawl4ai_mcp.server"]
