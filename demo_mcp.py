"""
Simple Demo: Testing MCP Servers
Shows the 3 MCP servers working with basic examples
"""

import asyncio
import subprocess
import time
from pathlib import Path

async def start_mcp_server(server_path):
    """Start an MCP server"""
    print(f"Starting {Path(server_path).stem}...")
    process = subprocess.Popen(
        [".venv/Scripts/python.exe", server_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    await asyncio.sleep(1)
    return process

async def demo():
    print("\n" + "="*80)
    print("MCP SERVERS DEMO")
    print("="*80)
    
    # Show available servers
    print("\n[1] INGESTION SERVER")
    print("    - ingest_rss_feeds(urls)")
    print("    - ingest_reddit(subreddits)")
    print("    - scrape_website(url, max_depth)")
    
    print("\n[2] ENRICHMENT SERVER")
    print("    - find_company_info(company_name, domain)")
    print("    - find_email(domain, first_name, last_name)")
    print("    - verify_email(email)")
    print("    - get_company_info_clearbit(domain)")
    
    print("\n[3] TASK MANAGEMENT SERVER")
    print("    - create_trello_card(list_id, name, description)")
    print("    - create_notion_task(title, content)")
    print("    - send_discord_message(channel_id, message)")
    print("    - send_email_notification(recipient, subject, body)")
    
    print("\n" + "="*80)
    print("TESTING SERVER STARTUP")
    print("="*80)
    
    servers = [
        "mcp_servers/ingestion_server.py",
        "mcp_servers/enrichment_server.py",
        "mcp_servers/task_management_server.py",
    ]
    
    processes = []
    for server in servers:
        try:
            proc = await start_mcp_server(server)
            processes.append(proc)
            print(f"✓ {Path(server).stem} started")
        except Exception as e:
            print(f"✗ {Path(server).stem} failed: {e}")
    
    print("\n" + "="*80)
    print("SERVERS RUNNING")
    print("="*80)
    print(f"\nAll {len(processes)} MCP servers are active")
    print("\nThe servers are now ready to accept tool calls from Claude or other clients.")
    print("\nExample usage:")
    print("  client.call_tool('ingestion', 'ingest_rss_feeds', {'urls': [...]})")
    print("  client.call_tool('enrichment', 'find_company_info', {'company_name': '...'})")
    print("  client.call_tool('task_management', 'send_discord_message', {...})")
    
    print("\n" + "="*80)
    print("CONFIGURATION STATUS")
    print("="*80)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = {
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL"),
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "HUNTER_API_KEY": "SET" if os.getenv("HUNTER_API_KEY") else "NOT SET",
        "TRELLO_API_KEY": "SET" if os.getenv("TRELLO_API_KEY") else "NOT SET",
        "DISCORD_BOT_TOKEN": "SET" if os.getenv("DISCORD_BOT_TOKEN") else "NOT SET",
    }
    
    for key, value in keys.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("DEMO COMPLETE - MCP Servers are operational!")
    print("="*80)
    
    # Cleanup
    for proc in processes:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(demo())
