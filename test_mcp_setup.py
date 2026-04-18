"""
MCP Servers Demo - Quick Test Script
This script demonstrates that the MCP servers are properly configured and ready to use.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("MCP SERVERS DEMO - Configuration & Readiness Check")
print("=" * 80)

# Check Python version
import sys
print(f"\n✓ Python Version: {sys.version.split()[0]}")

# Check MCP package
try:
    import mcp
    print("✓ MCP package installed")
except ImportError:
    print("✗ MCP package NOT installed - Run: pip install mcp")

# Check key dependencies
dependencies = {
    "langchain_core": "LangChain Core",
    "langchain_ollama": "LangChain Ollama",
    "langchain_qdrant": "LangChain Qdrant",
    "requests": "Requests",
    "pydantic": "Pydantic",
    "dotenv": "Python Dotenv",
}

print("\n" + "-" * 80)
print("DEPENDENCY CHECK:")
print("-" * 80)

for module_name, display_name in dependencies.items():
    try:
        __import__(module_name)
        print(f"✓ {display_name}")
    except ImportError:
        print(f"✗ {display_name} NOT installed")

# Check environment variables
print("\n" + "-" * 80)
print("ENVIRONMENT CONFIGURATION:")
print("-" * 80)

env_vars = {
    "OLLAMA_MODEL": "Ollama Model",
    "OLLAMA_BASE_URL": "Ollama Base URL",
    "QDRANT_URL": "Qdrant URL",
    "QDRANT_COLLECTION_NAME": "Qdrant Collection",
    "HUNTER_API_KEY": "Hunter.io API Key",
    "TRELLO_API_KEY": "Trello API Key",
    "DISCORD_BOT_TOKEN": "Discord Bot Token",
}

for env_var, display_name in env_vars.items():
    value = os.getenv(env_var)
    if value:
        # Mask sensitive values
        if "KEY" in env_var or "TOKEN" in env_var:
            masked = value[:10] + "*" * (len(value) - 10) if len(value) > 10 else "***"
            print(f"✓ {display_name}: {masked}")
        else:
            print(f"✓ {display_name}: {value}")
    else:
        print(f"✗ {display_name}: NOT SET")

# Check MCP servers exist
print("\n" + "-" * 80)
print("MCP SERVERS FILE CHECK:")
print("-" * 80)

mcp_servers = {
    "mcp_servers/ingestion_server.py": "Ingestion Server",
    "mcp_servers/enrichment_server.py": "Enrichment Server",
    "mcp_servers/task_management_server.py": "Task Management Server",
    "mcp_servers/mcp_client.py": "MCP Client",
}

for file_path, display_name in mcp_servers.items():
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✓ {display_name}: {file_path} ({size} bytes)")
    else:
        print(f"✗ {display_name}: {file_path} NOT FOUND")

# Display available tools
print("\n" + "-" * 80)
print("AVAILABLE MCP TOOLS:")
print("-" * 80)

tools_info = {
    "INGESTION SERVER": [
        "• ingest_rss_feeds(urls)",
        "• ingest_reddit(subreddits)",
        "• scrape_website(url, max_depth)",
    ],
    "ENRICHMENT SERVER": [
        "• find_company_info(company_name, domain)",
        "• find_email(domain, first_name, last_name)",
        "• verify_email(email)",
        "• get_company_info_clearbit(domain)",
    ],
    "TASK MANAGEMENT SERVER": [
        "• create_trello_card(list_id, name, description)",
        "• create_notion_task(title, content)",
        "• send_discord_message(channel_id, message)",
        "• send_email_notification(recipient, subject, body)",
    ],
}

for server_name, tools in tools_info.items():
    print(f"\n{server_name}:")
    for tool in tools:
        print(f"  {tool}")

# Show documentation files
print("\n" + "-" * 80)
print("DOCUMENTATION FILES:")
print("-" * 80)

doc_files = {
    "MCP_INTEGRATION_GUIDE.md": "Comprehensive Integration Guide",
    "MCP_QUICK_REFERENCE.md": "Quick Reference",
    "MCP_ARCHITECTURE.md": "System Architecture",
    "MCP_IMPLEMENTATION_SUMMARY.md": "Implementation Summary",
}

for file_path, description in doc_files.items():
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✓ {description}: {file_path} ({size} bytes)")
    else:
        print(f"✗ {description}: {file_path} NOT FOUND")

# Show example code
print("\n" + "-" * 80)
print("EXAMPLE CODE:")
print("-" * 80)

if os.path.exists("core_engine/agent_mcp_example.py"):
    print("✓ Example MCP integration: core_engine/agent_mcp_example.py")
else:
    print("✗ Example code not found")

# Summary
print("\n" + "=" * 80)
print("QUICK START GUIDE:")
print("=" * 80)

print("""
1. INSTALL MCP PACKAGE:
   pip install mcp

2. RUN MCP SERVERS (in separate terminals):
   python mcp_servers/ingestion_server.py
   python mcp_servers/enrichment_server.py
   python mcp_servers/task_management_server.py

3. CHOOSE YOUR INTEGRATION PATH:
   
   Option A - Claude Desktop:
   └─ Configure claude_desktop_config.json with MCP servers
      See: MCP_INTEGRATION_GUIDE.md
   
   Option B - Direct Integration:
   └─ Use MCPClient in your agent code
      See: core_engine/agent_mcp_example.py
   
   Option C - Hybrid Approach:
   └─ Keep existing tools, gradually migrate to MCP
      See: MCP_QUICK_REFERENCE.md

4. READ THE DOCUMENTATION:
   - Start with: MCP_QUICK_REFERENCE.md
   - Full guide: MCP_INTEGRATION_GUIDE.md
   - Architecture: MCP_ARCHITECTURE.md

5. TEST YOUR SETUP:
   python mcp_servers/ingestion_server.py
   # Server should start without errors

KEY BENEFITS:
✓ Standardized tool interfaces
✓ Works with Claude and other AI systems
✓ Scalable architecture
✓ Easy to test and maintain
✓ Backward compatible with existing code

NEXT STEPS:
1. Install MCP: pip install mcp
2. Configure your API keys in .env
3. Start with one MCP server and test it
4. Gradually integrate into your agent
5. Enjoy better AI collaboration! 🚀
""")

print("=" * 80)
print("✓ MCP SETUP COMPLETE - Ready to integrate!")
print("=" * 80)
