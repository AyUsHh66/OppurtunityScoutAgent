"""
MCP Server for Lead Enrichment
Provides tools for enriching lead data from various sources.
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
import requests

load_dotenv()

import mcp.server.stdio
from mcp.types import Tool
import mcp.types as types


class EnrichmentServer:
    def __init__(self):
        self.server = mcp.server.stdio.StdioServer()
        self.setup_routes()

    def setup_routes(self):
        """Setup MCP tools and handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                types.Tool(
                    name="find_company_info",
                    description="Find company information and contact details using Hunter.io API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "The company name to research"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Optional: Company domain (e.g., example.com)"
                            }
                        },
                        "required": ["company_name"]
                    }
                ),
                types.Tool(
                    name="find_email",
                    description="Find email addresses for a company or person using Hunter.io",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Company domain"
                            },
                            "first_name": {
                                "type": "string",
                                "description": "Optional: First name of person"
                            },
                            "last_name": {
                                "type": "string",
                                "description": "Optional: Last name of person"
                            }
                        },
                        "required": ["domain"]
                    }
                ),
                types.Tool(
                    name="verify_email",
                    description="Verify if an email address is valid using Hunter.io",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Email address to verify"
                            }
                        },
                        "required": ["email"]
                    }
                ),
                types.Tool(
                    name="get_company_info_clearbit",
                    description="Get detailed company information using Clearbit API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Company domain"
                            }
                        },
                        "required": ["domain"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Any:
            if name == "find_company_info":
                return await self._find_company_info(
                    arguments["company_name"],
                    arguments.get("domain")
                )
            elif name == "find_email":
                return await self._find_email(
                    arguments["domain"],
                    arguments.get("first_name"),
                    arguments.get("last_name")
                )
            elif name == "verify_email":
                return await self._verify_email(arguments["email"])
            elif name == "get_company_info_clearbit":
                return await self._get_company_info_clearbit(arguments["domain"])
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _find_company_info(self, company_name: str, domain: str = None) -> dict:
        """Find company information"""
        try:
            api_key = os.getenv("HUNTER_API_KEY")
            if not api_key:
                return {"status": "error", "message": "Hunter API key not configured"}
            
            # Use provided domain or construct one
            if not domain:
                domain = f"{company_name.lower().replace(' ', '')}.com"
            
            url = f"https://api.hunter.io/v2/company-enrichment?domain={domain}&api_key={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json().get("data", {})
            return {
                "status": "success",
                "data": data,
                "company_name": data.get("name"),
                "industry": data.get("industry"),
                "employees": data.get("employees"),
                "website": data.get("website")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _find_email(self, domain: str, first_name: str = None, last_name: str = None) -> dict:
        """Find email addresses"""
        try:
            api_key = os.getenv("HUNTER_API_KEY")
            if not api_key:
                return {"status": "error", "message": "Hunter API key not configured"}
            
            url = f"https://api.hunter.io/v2/email-finder?domain={domain}&api_key={api_key}"
            if first_name:
                url += f"&first_name={first_name}"
            if last_name:
                url += f"&last_name={last_name}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json().get("data", {})
            return {
                "status": "success",
                "email": data.get("email"),
                "confidence": data.get("confidence"),
                "sources": data.get("sources")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _verify_email(self, email: str) -> dict:
        """Verify email address"""
        try:
            api_key = os.getenv("HUNTER_API_KEY")
            if not api_key:
                return {"status": "error", "message": "Hunter API key not configured"}
            
            url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json().get("data", {})
            return {
                "status": "success",
                "email": data.get("email"),
                "result": data.get("result"),
                "score": data.get("score")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_company_info_clearbit(self, domain: str) -> dict:
        """Get company info from Clearbit"""
        try:
            api_key = os.getenv("CLEARBIT_API_KEY")
            if not api_key:
                return {"status": "error", "message": "Clearbit API key not configured"}
            
            url = f"https://company-stream.clearbit.com/v1/companies/find?domain={domain}"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return {
                "status": "success",
                "data": data
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def run(self):
        """Run the MCP server"""
        async with self.server:
            pass


if __name__ == "__main__":
    import asyncio
    server = EnrichmentServer()
    asyncio.run(server.run())
