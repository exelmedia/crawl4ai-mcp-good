from setuptools import setup, find_packages

setup(
    name="crawl4ai-mcp",
    version="0.1.0",
    description="MCP server for Crawl4AI integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "crawl4ai-mcp=crawl4ai_mcp.server:main",
        ],
    },
)
