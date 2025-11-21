"""Crawl4AI API Client"""

import os
import httpx
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class CrawlResult(BaseModel):
    """Result from crawling a URL"""
    url: str
    content: str
    markdown: Optional[str] = None
    metadata: Dict[str, Any] = {}
    links: Dict[str, List[str]] = {}
    media: Dict[str, List[Dict[str, str]]] = {}
    screenshot: Optional[str] = None
    extracted_content: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class Crawl4AIClient:
    """Client for interacting with Crawl4AI instance"""
    
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # Setup basic auth if credentials provided
        auth = None
        if username and password:
            auth = (username, password)
        
        self.client = httpx.AsyncClient(timeout=timeout, auth=auth)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _parse_result(self, result: Dict[str, Any], url: str) -> CrawlResult:
        """Parse API response into CrawlResult model"""
        # Parse markdown (może być dict z raw_markdown)
        markdown_data = result.get("markdown")
        if isinstance(markdown_data, dict):
            markdown = markdown_data.get("raw_markdown", "")
        else:
            markdown = markdown_data or ""
        
        # Parse links (API zwraca listy dict z href)
        links_data = result.get("links", {})
        parsed_links = {}
        for link_type, link_list in links_data.items():
            if isinstance(link_list, list):
                parsed_links[link_type] = [
                    link.get("href") if isinstance(link, dict) else link 
                    for link in link_list
                ]
            else:
                parsed_links[link_type] = link_list
        
        # Parse media (API zwraca skomplikowane struktury, uprośćmy)
        media_data = result.get("media", {})
        parsed_media = {}
        for media_type, media_list in media_data.items():
            if isinstance(media_list, list):
                # Zapisz tylko liczbę elementów zamiast szczegółów
                parsed_media[media_type] = []
            else:
                parsed_media[media_type] = media_list
        
        return CrawlResult(
            url=url,
            content=result.get("html", ""),
            markdown=markdown,
            metadata=result.get("metadata") or {},
            links=parsed_links,
            media=parsed_media,
            screenshot=result.get("screenshot"),
            extracted_content=result.get("extracted_content"),
            success=True
        )
    
    async def crawl_url(
        self,
        url: str,
        word_count_threshold: int = 10,
        extract_only_main: bool = True,
        return_markdown: bool = True,
        screenshot: bool = False,
        wait_for: Optional[str] = None
    ) -> CrawlResult:
        """
        Crawl a single URL and extract content
        
        Args:
            url: The URL to crawl
            word_count_threshold: Minimum word count for content blocks
            extract_only_main: Extract only main content
            return_markdown: Return markdown formatted content
            screenshot: Capture screenshot of the page
            wait_for: CSS selector or JS condition to wait for
        """
        try:
            payload = {
                "urls": [url],
                "word_count_threshold": word_count_threshold,
                "extract_only_main": extract_only_main,
                "return_markdown": return_markdown,
                "screenshot": screenshot
            }
            
            if wait_for:
                payload["wait_for"] = wait_for
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            result = data.get("results", [{}])[0]
            return self._parse_result(result, url)
        except Exception as e:
            return CrawlResult(
                url=url,
                content="",
                success=False,
                error=str(e)
            )
    
    async def crawl_with_js(
        self,
        url: str,
        js_code: Optional[str] = None,
        wait_for: Optional[str] = None,
        return_markdown: bool = True,
        screenshot: bool = False,
        session_id: Optional[str] = None
    ) -> CrawlResult:
        """
        Crawl a URL with JavaScript rendering
        
        Args:
            url: The URL to crawl
            js_code: Optional JavaScript code to execute
            wait_for: CSS selector or JS condition to wait for before extracting content
            return_markdown: Return markdown formatted content
            screenshot: Capture screenshot of the page
            session_id: Session ID to maintain cookies/state across requests
        """
        try:
            payload = {
                "urls": [url],
                "js_code": js_code,
                "wait_for": wait_for,
                "return_markdown": return_markdown,
                "js_rendering": True,
                "screenshot": screenshot
            }
            
            if session_id:
                payload["session_id"] = session_id
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            result = data.get("results", [{}])[0]
            return self._parse_result(result, url)
        except Exception as e:
            return CrawlResult(
                url=url,
                content="",
                success=False,
                error=str(e)
            )
    
    async def extract_structured(
        self,
        url: str,
        css_selectors: List[str],
        return_markdown: bool = True,
        screenshot: bool = False
    ) -> CrawlResult:
        """
        Extract structured data using CSS selectors
        
        Args:
            url: The URL to crawl
            css_selectors: List of CSS selectors to extract
            return_markdown: Return markdown formatted content
            screenshot: Capture screenshot of the page
        """
        try:
            payload = {
                "urls": [url],
                "css_selectors": css_selectors,
                "return_markdown": return_markdown,
                "screenshot": screenshot
            }
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            result = data.get("results", [{}])[0]
            return self._parse_result(result, url)
        except Exception as e:
            return CrawlResult(
                url=url,
                content="",
                success=False,
                error=str(e)
            )
    
    async def crawl_many(
        self,
        urls: List[str],
        max_concurrent: int = 5,
        screenshot: bool = False,
        return_markdown: bool = True
    ) -> List[CrawlResult]:
        """
        Crawl multiple URLs concurrently
        
        Args:
            urls: List of URLs to crawl
            max_concurrent: Maximum concurrent requests
            screenshot: Capture screenshots
            return_markdown: Return markdown formatted content
        """
        try:
            payload = {
                "urls": urls,
                "max_concurrent": max_concurrent,
                "screenshot": screenshot,
                "return_markdown": return_markdown
            }
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            crawl_results = []
            for result in results:
                crawl_results.append(self._parse_result(result, result.get("url", "")))
            
            return crawl_results
            
        except Exception as e:
            # Return error result for all URLs
            return [
                CrawlResult(
                    url=url,
                    content="",
                    success=False,
                    error=str(e)
                )
                for url in urls
            ]
    
    async def extract_with_llm(
        self,
        url: str,
        instruction: str,
        provider: str = "openai/gpt-4o-mini",
        schema: Optional[Dict[str, Any]] = None
    ) -> CrawlResult:
        """
        Extract data using LLM-based extraction
        
        Args:
            url: The URL to crawl
            instruction: Extraction instruction for the LLM
            provider: LLM provider (e.g., "openai/gpt-4o-mini")
            schema: Optional JSON schema for structured output
        """
        try:
            payload = {
                "urls": [url],
                "extraction_strategy": {
                    "type": "llm",
                    "provider": provider,
                    "instruction": instruction
                }
            }
            
            if schema:
                payload["extraction_strategy"]["schema"] = schema
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            result = data.get("results", [{}])[0]
            return self._parse_result(result, url)
        except Exception as e:
            return CrawlResult(
                url=url,
                content="",
                success=False,
                error=str(e)
            )
