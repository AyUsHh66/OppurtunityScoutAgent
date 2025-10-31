# Model Context Protocol (MCP) Integration Guide

## Overview

Your Opportunity Scout Agent has been upgraded to use the **Model Context Protocol (MCP)**. MCP allows you to:

- **Standardize tool interactions** across different AI systems
- **Create reusable, composable tools** that work with Claude and other AI models
- **Scale your agent** with better separation of concerns
- **Enable multi-agent collaboration** with standardized interfaces

## MCP Architecture

Your project now includes three MCP servers:

### 1. **Ingestion Server** (`mcp_servers/ingestion_server.py`)
Handles all data ingestion from various sources:
- **ingest_rss_feeds** - Ingest RSS feeds
- **ingest_reddit** - Ingest Reddit posts
- **scrape_website** - Recursively scrape websites

### 2. **Enrichment Server** (`mcp_servers/enrichment_server.py`)
Enriches lead data from external services:
- **find_company_info** - Find company details via Hunter.io
- **find_email** - Find email addresses via Hunter.io
- **verify_email** - Verify email addresses via Hunter.io
- **get_company_info_clearbit** - Get company data via Clearbit

### 3. **Task Management Server** (`mcp_servers/task_management_server.py`)
Manages tasks and notifications:
- **create_trello_card** - Create Trello cards
- **create_notion_task** - Create Notion tasks
- **send_discord_message** - Send Discord notifications
- **send_email_notification** - Send email notifications

## How to Use MCP Servers

### Option 1: With Claude Desktop (Recommended)

1. **Install MCP package:**
   ```bash
   pip install mcp
   ```

2. **Configure Claude Desktop** to use your MCP servers by adding to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "ingestion": {
         "command": "python",
         "args": ["path/to/mcp_servers/ingestion_server.py"]
       },
       "enrichment": {
         "command": "python",
         "args": ["path/to/mcp_servers/enrichment_server.py"]
       },
       "task_management": {
         "command": "python",
         "args": ["path/to/mcp_servers/task_management_server.py"]
       }
     }
   }
   ```

3. **Claude will now have access to all your tools** and can use them in conversations.

### Option 2: Direct Integration in Your Agent

You can also integrate MCP servers directly into your `core_engine/agent.py`:

```python
import asyncio
from mcp_servers.mcp_client import MCPClient

async def use_mcp_tools():
    client = MCPClient()
    
    # Connect to ingestion server
    async with client.connect_to_server("ingestion", "mcp_servers/ingestion_server.py") as session:
        # Call tools
        result = await client.call_tool("ingestion", "ingest_rss_feeds", {
            "urls": ["https://example.com/feed.rss"]
        })
        print(result)
```

## Integration with Existing Agent

### Current Workflow

Your agent currently:
1. Retrieves opportunities from Qdrant
2. Qualifies leads
3. Enriches data
4. Drafts emails
5. Creates tasks and sends notifications

### With MCP

Each step can now leverage MCP servers:

```python
# Before (current)
from tools.enrichment import find_company_info
contact_info = find_company_info.invoke({"company_name": company_name})

# After (MCP)
async def enrich_data_with_mcp(state):
    async with client.connect_to_server("enrichment", ...) as session:
        result = await client.call_tool("enrichment", "find_company_info", {
            "company_name": state["company_name"]
        })
        return result
```

## Benefits of MCP Integration

### 1. **Better Tool Discovery**
Claude and other MCP-compatible clients automatically discover available tools.

### 2. **Standardized Interfaces**
All tools follow the same protocol, making them:
- Easy to understand
- Easy to extend
- Easy to debug

### 3. **Server Separation**
- Each server can be updated independently
- Easier to test individual components
- Better error handling and logging

### 4. **Multi-Client Support**
Your tools can now be used by:
- Claude Desktop
- Web frontends using Claude API
- Other AI agents
- Custom applications

### 5. **Resource Management**
MCP servers handle their own lifecycle:
- Automatic startup/shutdown
- Built-in error recovery
- Resource cleanup

## Example: Using MCP with Claude

Once configured in Claude Desktop, you can ask Claude:

> "Using the ingestion tool, fetch the latest posts from r/startups and store them in our vector database."

Claude will:
1. Detect available MCP servers
2. Select the appropriate tools
3. Call the ingestion server's `ingest_reddit` tool
4. Return the results

## Configuration & Environment Variables

Ensure these are in your `.env` file:

```env
# Ingestion
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=opportunity_scout_collection

# Enrichment
HUNTER_API_KEY=your_hunter_key
CLEARBIT_API_KEY=your_clearbit_key

# Task Management
TRELLO_API_KEY=your_trello_key
TRELLO_TOKEN=your_trello_token
TRELLO_LIST_ID=your_list_id

NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_db_id

DISCORD_BOT_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=your_channel_id

# Reddit (for ingestion)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

## Next Steps

### Phase 1: Implement (Recommended First)
1. Update your agent to use MCP client for data ingestion
2. Test each MCP server independently
3. Add error handling and logging

### Phase 2: Enhance
1. Add more enrichment data sources
2. Create an MCP server for lead qualification analysis
3. Add persistence for historical analyses

### Phase 3: Advanced
1. Create MCP servers for each data source (Twitter, LinkedIn, etc.)
2. Build a web UI that connects to your MCP servers
3. Integrate with additional AI models

## Starting MCP Servers Manually

To test individual servers:

```bash
# Terminal 1: Start ingestion server
python mcp_servers/ingestion_server.py

# Terminal 2: Start enrichment server
python mcp_servers/enrichment_server.py

# Terminal 3: Start task management server
python mcp_servers/task_management_server.py
```

## Troubleshooting

### MCP Package Not Installed
```bash
pip install mcp
```

### Server Not Responding
- Check if the server process is running
- Verify environment variables are set
- Check logs for errors

### Tool Not Found
- Run `list_tools()` on the connected session
- Verify the tool name matches exactly
- Check server implementation

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/anthropics/model-context-protocol)
- [Claude Desktop Setup](https://modelcontextprotocol.io/quickstart/user)

## Summary

Your Opportunity Scout Agent now has:
- ✅ Three specialized MCP servers
- ✅ Standardized tool interfaces
- ✅ Better separation of concerns
- ✅ Easy integration with Claude and other AI systems
- ✅ Scalable architecture for future expansion

The MCP integration maintains backward compatibility with your existing code while providing a path to more advanced integrations and AI collaboration.
