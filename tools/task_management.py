# In tools/task_management.py
import os
import requests
from langchain_core.tools import tool

@tool
def create_trello_card(list_id: str, name: str, description: str) -> str:
    """Creates a new card on a Trello list with a name and description."""
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    if not api_key or not token:
        return "Trello API key or token not set."

    url = "https://api.trello.com/1/cards"
    query = {
        'key': api_key,
        'token': token,
        'idList': list_id,
        'name': name,
        'desc': description
    }
    try:
        response = requests.post(url, params=query)
        response.raise_for_status()
        return f"Trello card created successfully: {response.json()['shortUrl']}"
    except requests.exceptions.RequestException as e:
        return f"Failed to create Trello card: {e}"

@tool
def create_notion_task(title: str, content: str) -> str:
    """Creates a new task page in a Notion database with a title and content."""
    token = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not token or not database_id:
        return "Notion API key or Database ID not set."

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
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Notion task created successfully: {response.json()['url']}"
    except requests.exceptions.RequestException as e:
        return f"Failed to create Notion task: {e}"

@tool
def send_discord_message(channel_id: str, message: str) -> str:
    """Sends a message to a specified Discord channel using a bot token."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        return "Discord bot token not set."

    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}
    data = {"content": message}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return "Discord message sent successfully."
    except requests.exceptions.RequestException as e:
        return f"Failed to send Discord message: {e}"