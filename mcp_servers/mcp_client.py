"""
MCP Client for Opportunity Scout Agent
This client connects to MCP servers for data ingestion, enrichment, and task management.
"""

import subprocess
import json
from typing import Any
from contextlib import asynccontextmanager

try:
    from mcp import ClientSession
    from mcp.client.stdio import StdioClientTransport
except ImportError:
    print("Warning: mcp package not installed. Install with: pip install mcp")
    ClientSession = None
    StdioClientTransport = None


class MCPClient:
    """Manages connections to MCP servers"""
    
    def __init__(self):
        self.sessions = {}
        self.transports = {}
    
    @asynccontextmanager
    async def connect_to_server(self, server_name: str, server_path: str):
        """Connect to an MCP server via stdio"""
        if ClientSession is None or StdioClientTransport is None:
            raise RuntimeError("MCP package not installed")
        
        # Start the server process
        process = subprocess.Popen(
            ["python", server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Create transport
        transport = StdioClientTransport(process.stdin, process.stdout)
        
        # Create session
        async with ClientSession(transport) as session:
            self.sessions[server_name] = session
            self.transports[server_name] = transport
            try:
                yield session
            finally:
                process.terminate()
                process.wait()
                if server_name in self.sessions:
                    del self.sessions[server_name]
                if server_name in self.transports:
                    del self.transports[server_name]
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Any:
        """Call a tool on a connected server"""
        if server_name not in self.sessions:
            raise RuntimeError(f"Not connected to server: {server_name}")
        
        session = self.sessions[server_name]
        result = await session.call_tool(tool_name, arguments)
        return result
    
    async def list_tools(self, server_name: str) -> list:
        """List available tools on a server"""
        if server_name not in self.sessions:
            raise RuntimeError(f"Not connected to server: {server_name}")
        
        session = self.sessions[server_name]
        tools = await session.list_tools()
        return tools


# For synchronous usage (compatibility with existing code)
class SyncMCPClient:
    """Synchronous wrapper for MCP client"""
    
    def __init__(self, ingestion_server_path: str = None, 
                 enrichment_server_path: str = None,
                 task_management_server_path: str = None):
        """Initialize with server paths"""
        self.ingestion_server_path = ingestion_server_path or "mcp_servers/ingestion_server.py"
        self.enrichment_server_path = enrichment_server_path or "mcp_servers/enrichment_server.py"
        self.task_management_server_path = task_management_server_path or "mcp_servers/task_management_server.py"
        
        # For now, this will work with the langchain tools
        # In a full implementation, you'd use asyncio to bridge sync/async
        self.client = MCPClient()
    
    def ingest_rss_feeds(self, urls: list) -> dict:
        """Ingest RSS feeds via MCP"""
        # Placeholder - would use async client
        return {
            "status": "success",
            "message": "Use async client for this operation",
            "urls": urls
        }
    
    def find_company_info(self, company_name: str) -> dict:
        """Find company info via MCP"""
        # Placeholder - would use async client
        return {
            "status": "success",
            "message": "Use async client for this operation",
            "company_name": company_name
        }
