"""
MCP Server for Task Management and Notifications
Provides tools for creating tasks (Trello, Notion) and sending notifications (Discord).
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


class TaskManagementServer:
    def __init__(self):
        self.server = mcp.server.stdio.StdioServer()
        self.setup_routes()

    def setup_routes(self):
        """Setup MCP tools and handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                types.Tool(
                    name="create_trello_card",
                    description="Create a card in a Trello list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "list_id": {
                                "type": "string",
                                "description": "The Trello list ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "Card title/name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Card description"
                            }
                        },
                        "required": ["list_id", "name"]
                    }
                ),
                types.Tool(
                    name="create_notion_task",
                    description="Create a task page in Notion database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "content": {
                                "type": "string",
                                "description": "Task content/description"
                            }
                        },
                        "required": ["title", "content"]
                    }
                ),
                types.Tool(
                    name="send_discord_message",
                    description="Send a message to a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "The Discord channel ID"
                            },
                            "message": {
                                "type": "string",
                                "description": "Message content"
                            }
                        },
                        "required": ["channel_id", "message"]
                    }
                ),
                types.Tool(
                    name="send_email_notification",
                    description="Send an email notification",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body"
                            }
                        },
                        "required": ["recipient", "subject", "body"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Any:
            if name == "create_trello_card":
                return await self._create_trello_card(
                    arguments["list_id"],
                    arguments["name"],
                    arguments.get("description", "")
                )
            elif name == "create_notion_task":
                return await self._create_notion_task(
                    arguments["title"],
                    arguments["content"]
                )
            elif name == "send_discord_message":
                return await self._send_discord_message(
                    arguments["channel_id"],
                    arguments["message"]
                )
            elif name == "send_email_notification":
                return await self._send_email_notification(
                    arguments["recipient"],
                    arguments["subject"],
                    arguments["body"]
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _create_trello_card(self, list_id: str, name: str, description: str = "") -> dict:
        """Create a Trello card"""
        try:
            api_key = os.getenv("TRELLO_API_KEY")
            token = os.getenv("TRELLO_TOKEN")
            
            if not api_key or not token:
                return {"status": "error", "message": "Trello credentials not configured"}
            
            url = "https://api.trello.com/1/cards"
            query = {
                'key': api_key,
                'token': token,
                'idList': list_id,
                'name': name,
                'desc': description
            }
            
            response = requests.post(url, params=query)
            response.raise_for_status()
            
            card_data = response.json()
            return {
                "status": "success",
                "message": f"Trello card created",
                "card_url": card_data.get('shortUrl'),
                "card_id": card_data.get('id')
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _create_notion_task(self, title: str, content: str) -> dict:
        """Create a Notion task"""
        try:
            token = os.getenv("NOTION_API_KEY")
            database_id = os.getenv("NOTION_DATABASE_ID")
            
            if not token or not database_id:
                return {"status": "error", "message": "Notion credentials not configured"}
            
            url = "https://api.notion.com/v1/pages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }
            payload = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Details": {"rich_text": [{"text": {"content": content}}]}
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            task_data = response.json()
            return {
                "status": "success",
                "message": "Notion task created",
                "task_url": task_data.get('url'),
                "task_id": task_data.get('id')
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _send_discord_message(self, channel_id: str, message: str) -> dict:
        """Send a Discord message"""
        try:
            token = os.getenv("DISCORD_BOT_TOKEN")
            
            if not token:
                return {"status": "error", "message": "Discord bot token not configured"}
            
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            headers = {"Authorization": f"Bot {token}"}
            data = {"content": message}
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Discord message sent successfully"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _send_email_notification(self, recipient: str, subject: str, body: str) -> dict:
        """Send an email notification (placeholder for SMTP integration)"""
        try:
            # This is a placeholder. You'd need to integrate with your email service
            # For example, using smtplib or a service like SendGrid
            return {
                "status": "success",
                "message": f"Email notification would be sent to {recipient}",
                "note": "Email integration not yet implemented"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def run(self):
        """Run the MCP server"""
        async with self.server:
            pass


if __name__ == "__main__":
    import asyncio
    server = TaskManagementServer()
    asyncio.run(server.run())
