# Quick Reference: MCP Integration for Opportunity Scout

## What Changed?

Your project now has **three MCP servers** that standardize how your agent interacts with tools.

## File Structure

```
Business-Agent-2.0/
├── mcp_servers/                    # NEW: MCP servers
│   ├── __init__.py
│   ├── ingestion_server.py        # Data ingestion tools
│   ├── enrichment_server.py       # Lead enrichment tools
│   ├── task_management_server.py  # Task & notification tools
│   └── mcp_client.py              # Client for connecting to servers
├── core_engine/
│   ├── agent.py                   # Original agent (unchanged)
│   └── agent_mcp_example.py       # NEW: Example of MCP integration
├── MCP_INTEGRATION_GUIDE.md       # NEW: Detailed guide
└── requirements.txt               # Updated with `mcp`
```

## Quick Start

### 1. Install MCP
```bash
pip install mcp
```

### 2. Choose Your Integration Path

**Option A: Use with Claude Desktop (Easiest)**
- Add MCP servers to Claude Desktop config
- Claude automatically discovers and uses your tools
- No code changes needed to your agent

**Option B: Integrate into Your Agent**
- Use the `MCPClient` in your agent code
- Full control over tool usage
- See `core_engine/agent_mcp_example.py` for examples

### 3. Test Individual Servers
```bash
# Terminal 1
python mcp_servers/ingestion_server.py

# Terminal 2
python mcp_servers/enrichment_server.py

# Terminal 3
python mcp_servers/task_management_server.py
```

## MCP Servers Overview

### Ingestion Server
**Tools for data collection:**
- `ingest_rss_feeds(urls)` - Get RSS content
- `ingest_reddit(subreddits)` - Get Reddit posts
- `scrape_website(url, max_depth)` - Crawl websites

### Enrichment Server
**Tools for lead research:**
- `find_company_info(company_name, domain)` - Company details
- `find_email(domain, first_name, last_name)` - Email discovery
- `verify_email(email)` - Email validation
- `get_company_info_clearbit(domain)` - Clearbit data

### Task Management Server
**Tools for action:**
- `create_trello_card(list_id, name, description)`
- `create_notion_task(title, content)`
- `send_discord_message(channel_id, message)`
- `send_email_notification(recipient, subject, body)`

## Migration Examples

### Before (Current)
```python
from tools.enrichment import find_company_info

contact_info = find_company_info.invoke({"company_name": "Acme Corp"})
```

### After (With MCP)
```python
from mcp_servers.mcp_client import MCPClient

async def get_company_info():
    client = MCPClient()
    async with client.connect_to_server("enrichment", ...) as session:
        result = await client.call_tool("enrichment", "find_company_info", {
            "company_name": "Acme Corp"
        })
        return result
```

## Key Benefits

| Benefit | Description |
|---------|-------------|
| **Standardized** | All tools follow MCP protocol |
| **Composable** | Tools work together seamlessly |
| **Discoverable** | Claude automatically finds all tools |
| **Scalable** | Add new servers without changing agent code |
| **Testable** | Each server can be tested independently |
| **Reusable** | Tools work across different agents/clients |

## Configuration

Add to `.env`:
```env
# Ingestion
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=opportunity_scout_collection

# Enrichment
HUNTER_API_KEY=your_key
CLEARBIT_API_KEY=your_key

# Task Management
TRELLO_API_KEY=your_key
TRELLO_TOKEN=your_token
TRELLO_LIST_ID=your_id

NOTION_API_KEY=your_key
NOTION_DATABASE_ID=your_id

DISCORD_BOT_TOKEN=your_token
DISCORD_CHANNEL_ID=your_id
```

## Next Steps

1. **Install MCP**: `pip install mcp`
2. **Test servers**: Run them individually to verify they work
3. **Choose integration path**: Claude Desktop or direct agent integration
4. **Migrate tools gradually**: Update one tool at a time
5. **Monitor performance**: Check logs and adjust as needed

## Troubleshooting

**Issue: Import errors when running servers**
- Solution: `pip install -r requirements.txt` first

**Issue: Server won't start**
- Check: Python version (3.8+), all dependencies installed
- Verify: `.env` file has required API keys

**Issue: Tools not discoverable in Claude**
- Check: MCP servers are running
- Verify: Claude Desktop config points to correct server paths

## References

- 📖 [MCP Official Docs](https://modelcontextprotocol.io/)
- 📋 [Implementation Guide](MCP_INTEGRATION_GUIDE.md)
- 💻 [Example Code](core_engine/agent_mcp_example.py)
- 🔧 [Server Code](mcp_servers/)

## Support

For issues:
1. Check the detailed guide: `MCP_INTEGRATION_GUIDE.md`
2. Review example implementation: `core_engine/agent_mcp_example.py`
3. Test servers individually: `python mcp_servers/<server>.py`
4. Check MCP documentation: https://modelcontextprotocol.io/

---

**Your project is now MCP-ready! 🚀**
