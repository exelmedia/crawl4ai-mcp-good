# Crawl4AI MCP Server

MCP (Model Context Protocol) server that integrates with Crawl4AI for web scraping and content extraction.

## Features

- Web page crawling and content extraction
- Markdown conversion
- LLM-ready content formatting
- JavaScript rendering support
- CSS selector-based extraction

## Installation

### Option 1: Local Installation

```bash
pip install --no-cache-dir -r requirements.txt
pip install -e .
```

### Option 2: Docker (Recommended)

```bash
# Quick start with Docker Compose
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d

# Or manual Docker
docker build -t crawl4ai-mcp .
docker run -d --name crawl4ai-mcp \
  -e CRAWL4AI_URL=your_url \
  -e CRAWL4AI_USERNAME=root \
  -e CRAWL4AI_PASSWORD=your_password \
  crawl4ai-mcp
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for complete Docker documentation.

## Configuration

Create a `.env` file based on `.env.example`:

```bash
CRAWL4AI_URL=https://crawl4ai-u53948.vm.elestio.app
CRAWL4AI_API_KEY=your_api_key_here
```

## Usage

### Running the MCP Server

```bash
python -m crawl4ai_mcp.server
```

### Available Tools

- `crawl_url`: Crawl a web page and extract content with metadata, links, and media
  - Supports screenshots and wait conditions
- `crawl_with_js`: Crawl a page with JavaScript rendering
  - Session management for authenticated content
  - Custom JavaScript execution
- `extract_structured`: Extract structured data using CSS selectors
- `crawl_many`: Batch crawl multiple URLs concurrently
  - Configurable concurrency limit
  - Efficient for bulk processing
- `extract_with_llm`: AI-powered data extraction
  - Supports OpenAI, Anthropic, Ollama providers
  - Best for complex or irregular content

## Deployment

### Docker Deployment

Quick start:
```bash
docker-compose up -d
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for complete Docker documentation.

### Elast.io Deployment

Quick start guide: [ELAST_QUICK_START.md](ELAST_QUICK_START.md)
Full documentation: [ELAST_DEPLOYMENT.md](ELAST_DEPLOYMENT.md)

**Quick Commands for Elast.io:**
```bash
Build:  docker-compose build
Run:    docker-compose up -d
```

**Environment Variables:**
```
CRAWL4AI_URL=https://crawl4ai-u53948.vm.elestio.app
CRAWL4AI_USERNAME=root
CRAWL4AI_PASSWORD=your_password
PORT=8000
HOST=0.0.0.0
```

## License

MIT
