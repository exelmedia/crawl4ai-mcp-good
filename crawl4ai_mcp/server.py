"""MCP Server for Crawl4AI"""

import os
import sys
import asyncio
import json
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .client import Crawl4AIClient

load_dotenv()

CRAWL4AI_URL = os.getenv("CRAWL4AI_URL", "https://crawl4ai-u53948.vm.elestio.app")
CRAWL4AI_USERNAME = os.getenv("CRAWL4AI_USERNAME")
CRAWL4AI_PASSWORD = os.getenv("CRAWL4AI_PASSWORD")

app = Server("crawl4ai-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="crawl_url",
            description="Crawl a web page and extract its content in markdown format. Returns the main content of the page with metadata, links, and optionally screenshots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl"
                    },
                    "word_count_threshold": {
                        "type": "integer",
                        "description": "Minimum word count for content blocks",
                        "default": 10
                    },
                    "extract_only_main": {
                        "type": "boolean",
                        "description": "Extract only main content, excluding navigation and footers",
                        "default": True
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Capture screenshot of the page",
                        "default": False
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "CSS selector or JS condition (e.g. 'css:.content' or 'js:document.ready') to wait for before extracting"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="crawl_with_js",
            description="Crawl a web page with JavaScript rendering enabled. Useful for single-page applications and dynamic content. Supports session management for authenticated content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl"
                    },
                    "js_code": {
                        "type": "string",
                        "description": "Optional JavaScript code to execute on the page"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "CSS selector or JS condition to wait for before extracting content"
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Capture screenshot of the page",
                        "default": False
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to maintain cookies/state across multiple requests (useful for login)"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="extract_structured",
            description="Extract structured data from a web page using CSS selectors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl"
                    },
                    "css_selectors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of CSS selectors to extract data from"
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Capture screenshot of the page",
                        "default": False
                    }
                },
                "required": ["url", "css_selectors"]
            }
        ),
        Tool(
            name="crawl_many",
            description="Crawl multiple URLs concurrently for efficient batch processing. Returns results for all URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to crawl"
                    },
                    "max_concurrent": {
                        "type": "integer",
                        "description": "Maximum number of concurrent requests",
                        "default": 5
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Capture screenshots of the pages",
                        "default": False
                    }
                },
                "required": ["urls"]
            }
        ),
        Tool(
            name="extract_with_llm",
            description="Extract data from a web page using LLM-based extraction. Best for complex or irregular content. Requires LLM API access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Instruction for the LLM on what data to extract"
                    },
                    "provider": {
                        "type": "string",
                        "description": "LLM provider (e.g., 'openai/gpt-4o-mini', 'anthropic/claude-3', 'ollama/llama3')",
                        "default": "openai/gpt-4o-mini"
                    }
                },
                "required": ["url", "instruction"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    async with Crawl4AIClient(CRAWL4AI_URL, CRAWL4AI_USERNAME, CRAWL4AI_PASSWORD) as client:
        if name == "crawl_url":
            url = arguments["url"]
            word_count_threshold = arguments.get("word_count_threshold", 10)
            extract_only_main = arguments.get("extract_only_main", True)
            screenshot = arguments.get("screenshot", False)
            wait_for = arguments.get("wait_for")
            
            result = await client.crawl_url(
                url=url,
                word_count_threshold=word_count_threshold,
                extract_only_main=extract_only_main,
                screenshot=screenshot,
                wait_for=wait_for
            )
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=f"Error crawling {url}: {result.error}"
                )]
            
            response_text = f"# Content from {url}\n\n"
            if result.markdown:
                response_text += result.markdown
            else:
                response_text += result.content
            
            # Add metadata
            if result.metadata:
                response_text += f"\n\n## Metadata\n{json.dumps(result.metadata, indent=2)}"
            
            # Add links info
            if result.links:
                internal = len(result.links.get("internal", []))
                external = len(result.links.get("external", []))
                response_text += f"\n\n## Links\n- Internal: {internal}\n- External: {external}"
            
            # Add media info
            if result.media:
                images = len(result.media.get("images", []))
                videos = len(result.media.get("videos", []))
                response_text += f"\n\n## Media\n- Images: {images}\n- Videos: {videos}"
            
            # Add screenshot info
            if result.screenshot:
                response_text += f"\n\n## Screenshot\nScreenshot captured (base64 encoded, {len(result.screenshot)} chars)"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "crawl_with_js":
            url = arguments["url"]
            js_code = arguments.get("js_code")
            wait_for = arguments.get("wait_for")
            screenshot = arguments.get("screenshot", False)
            session_id = arguments.get("session_id")
            
            result = await client.crawl_with_js(
                url=url,
                js_code=js_code,
                wait_for=wait_for,
                screenshot=screenshot,
                session_id=session_id
            )
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=f"Error crawling {url}: {result.error}"
                )]
            
            response_text = f"# Content from {url} (JS rendered)\n\n"
            if result.markdown:
                response_text += result.markdown
            else:
                response_text += result.content
            
            # Add metadata
            if result.metadata:
                response_text += f"\n\n## Metadata\n{json.dumps(result.metadata, indent=2)}"
            
            # Add links and media info
            if result.links:
                internal = len(result.links.get("internal", []))
                external = len(result.links.get("external", []))
                response_text += f"\n\n## Links\n- Internal: {internal}\n- External: {external}"
            
            if result.media:
                images = len(result.media.get("images", []))
                videos = len(result.media.get("videos", []))
                response_text += f"\n\n## Media\n- Images: {images}\n- Videos: {videos}"
            
            # Add screenshot info
            if result.screenshot:
                response_text += f"\n\n## Screenshot\nScreenshot captured (base64 encoded, {len(result.screenshot)} chars)"
            
            # Add session info
            if session_id:
                response_text += f"\n\n## Session\nSession ID: {session_id}"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "extract_structured":
            url = arguments["url"]
            css_selectors = arguments["css_selectors"]
            screenshot = arguments.get("screenshot", False)
            
            result = await client.extract_structured(
                url=url,
                css_selectors=css_selectors,
                screenshot=screenshot
            )
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=f"Error extracting from {url}: {result.error}"
                )]
            
            response_text = f"# Extracted data from {url}\n\n"
            if result.metadata:
                response_text += f"## Extracted Data\n{json.dumps(result.metadata, indent=2)}\n\n"
            
            if result.extracted_content:
                response_text += f"## Extracted Content\n{result.extracted_content}\n\n"
            
            if result.markdown:
                response_text += f"## Content\n{result.markdown}"
            
            if result.screenshot:
                response_text += f"\n\n## Screenshot\nScreenshot captured (base64 encoded, {len(result.screenshot)} chars)"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "crawl_many":
            urls = arguments["urls"]
            max_concurrent = arguments.get("max_concurrent", 5)
            screenshot = arguments.get("screenshot", False)
            
            results = await client.crawl_many(
                urls=urls,
                max_concurrent=max_concurrent,
                screenshot=screenshot
            )
            
            response_text = f"# Batch Crawl Results ({len(urls)} URLs)\n\n"
            
            success_count = sum(1 for r in results if r.success)
            failed_count = len(results) - success_count
            
            response_text += f"## Summary\n- ✅ Success: {success_count}\n- ❌ Failed: {failed_count}\n\n"
            
            for i, result in enumerate(results, 1):
                if result.success:
                    title = result.metadata.get("title", "Untitled") if result.metadata else "Untitled"
                    content_len = len(result.markdown) if result.markdown else len(result.content)
                    links = len(result.links.get("internal", [])) + len(result.links.get("external", [])) if result.links else 0
                    
                    response_text += f"### {i}. {title}\n"
                    response_text += f"- URL: {result.url}\n"
                    response_text += f"- Content: {content_len} chars\n"
                    response_text += f"- Links: {links}\n\n"
                else:
                    response_text += f"### {i}. ❌ Failed\n"
                    response_text += f"- URL: {result.url}\n"
                    response_text += f"- Error: {result.error}\n\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "extract_with_llm":
            url = arguments["url"]
            instruction = arguments["instruction"]
            provider = arguments.get("provider", "openai/gpt-4o-mini")
            
            result = await client.extract_with_llm(
                url=url,
                instruction=instruction,
                provider=provider
            )
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=f"Error extracting from {url}: {result.error}"
                )]
            
            response_text = f"# LLM Extracted Data from {url}\n\n"
            response_text += f"**Provider:** {provider}\n\n"
            
            if result.extracted_content:
                response_text += f"## Extracted Content\n{result.extracted_content}\n\n"
            
            if result.metadata:
                response_text += f"## Metadata\n{json.dumps(result.metadata, indent=2)}"
            
            return [TextContent(type="text", text=response_text)]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]


async def async_main():
    """Async main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
