"""
Simple HTTP server for Elast.io deployment.
This allows the service to be accessible via HTTPS while MCP remains stdio-based.
"""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="Crawl4AI MCP Server")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page showing service status"""
    crawl4ai_url = os.getenv("CRAWL4AI_URL", "Not configured")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crawl4AI MCP Server</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .status {{
                background: #2ecc71;
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
                font-size: 18px;
            }}
            .info {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .info strong {{
                color: #34495e;
            }}
            code {{
                background: #34495e;
                color: #ecf0f1;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #7f8c8d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Crawl4AI MCP Server</h1>
            
            <div class="status">
                ✅ Server is Running
            </div>
            
            <div class="info">
                <strong>Service Type:</strong> Model Context Protocol (MCP) Server
            </div>
            
            <div class="info">
                <strong>Protocol:</strong> stdio (Standard Input/Output)
            </div>
            
            <div class="info">
                <strong>Crawl4AI Backend:</strong> <code>{crawl4ai_url}</code>
            </div>
            
            <div class="info">
                <strong>Server Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
            
            <h2>📝 Usage</h2>
            <p>This is an MCP server that communicates via stdio protocol. It cannot be used directly via HTTP.</p>
            <p>To use this server:</p>
            <ol>
                <li>Configure it in your MCP client (Claude Desktop, Cursor, etc.)</li>
                <li>Use the command: <code>python -m crawl4ai_mcp.server</code></li>
                <li>Set environment variables for Crawl4AI API credentials</li>
            </ol>
            
            <h2>🔗 Available Endpoints</h2>
            <ul>
                <li><code>/</code> - This status page</li>
                <li><code>/health</code> - Health check endpoint</li>
            </ul>
            
            <div class="footer">
                Crawl4AI MCP Server • Deployed on Elast.io
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "crawl4ai-mcp",
        "protocol": "stdio",
        "timestamp": datetime.utcnow().isoformat(),
        "crawl4ai_url": os.getenv("CRAWL4AI_URL", "Not configured")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
