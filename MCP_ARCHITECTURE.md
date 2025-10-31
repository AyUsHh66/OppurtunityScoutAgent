# MCP Architecture for Opportunity Scout Agent

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OPPORTUNITY SCOUT AGENT                       │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      LangGraph Workflow                         │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │ │
│  │  │   Retrieve   │───▶│   Qualify    │───▶│   Enrich     │    │ │
│  │  └──────────────┘    └──────────────┘    └──────────────┘    │ │
│  │         │                    │                    │            │ │
│  │         ▼                    ▼                    ▼            │ │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │ │
│  │   │   MCP Client │    │   MCP Client │    │   MCP Client │    │ │
│  │   │ (Ingestion)  │    │   (N/A yet)  │    │(Enrichment)  │    │ │
│  │   └──────────────┘    └──────────────┘    └──────────────┘    │ │
│  │         │                                         │             │ │
│  │         ▼                                         ▼             │ │
│  │   ┌──────────────────────────────────────────────────────┐    │ │
│  │   │         MCP Servers (Background Processes)          │    │ │
│  │   │                                                      │    │ │
│  │   │  ┌───────────────────┐  ┌───────────────────┐      │    │ │
│  │   │  │  Ingestion Server │  │Enrichment Server  │      │    │ │
│  │   │  │  • ingest_rss     │  │ • find_company   │      │    │ │
│  │   │  │  • ingest_reddit  │  │ • find_email     │      │    │ │
│  │   │  │  • scrape_website │  │ • verify_email   │      │    │ │
│  │   │  │                   │  │ • clearbit_info  │      │    │ │
│  │   │  └───────────────────┘  └───────────────────┘      │    │ │
│  │   │           │                      │                 │    │ │
│  │   │           ▼                      ▼                 │    │ │
│  │   │      [Qdrant]              [Hunter.io]             │    │ │
│  │   │                            [Clearbit]              │    │ │
│  │   │                                                      │    │ │
│  │   │  ┌───────────────────────────────────────────┐      │    │ │
│  │   │  │  Task Management Server                  │      │    │ │
│  │   │  │  • create_trello_card                   │      │    │ │
│  │   │  │  • create_notion_task                   │      │    │ │
│  │   │  │  • send_discord_message                 │      │    │ │
│  │   │  │  • send_email_notification              │      │    │ │
│  │   │  └───────────────────────────────────────────┘      │    │ │
│  │   │           │                                        │    │ │
│  │   │           ▼                                        │    │ │
│  │   │      [Trello] [Notion] [Discord] [Email]          │    │ │
│  │   │                                                      │    │ │
│  │   └──────────────────────────────────────────────────────┘    │ │
│  │              │                        │                       │ │
│  └──────────────┼────────────────────────┼───────────────────────┘ │
│                 │                        │                         │
│                 ▼                        ▼                         │
│          [Draft Email]          [Create Task]                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow
```
User Goal
    │
    ▼
Retrieve Node
    │
    ├─▶ MCP Client calls Ingestion Server
    │
    ▼
Ingestion Server
    │
    ├─ ingest_rss_feeds() ──▶ [RSS Sources] ──▶ [Qdrant]
    ├─ ingest_reddit()     ──▶ [Reddit API] ──▶ [Qdrant]
    └─ scrape_website()    ──▶ [Web Pages]  ──▶ [Qdrant]
    │
    ▼
Vector Embeddings + Storage
    │
    ▼
Retrieval Pipeline
```

### 2. Lead Qualification Flow
```
Retrieved Documents
    │
    ▼
Qualify Node
    │
    ├─ Parse with LLM
    │
    ▼
LeadQualification (Score, Company, Justification)
    │
    ├─ Score > 7?
    │
    ├─ YES ──▶ Continue to Enrichment
    │
    └─ NO ──▶ End workflow
```

### 3. Lead Enrichment Flow
```
Company Name (from qualification)
    │
    ▼
Enrich Node
    │
    ├─▶ MCP Client calls Enrichment Server
    │
    ▼
Enrichment Server
    │
    ├─ find_company_info()    ──▶ [Hunter.io] ──▶ Company Details
    ├─ find_email()           ──▶ [Hunter.io] ──▶ Email Addresses
    ├─ verify_email()         ──▶ [Hunter.io] ──▶ Email Validation
    └─ get_company_clearbit() ──▶ [Clearbit]  ──▶ Detailed Profile
    │
    ▼
Enriched Lead Profile
```

### 4. Task & Notification Flow
```
Lead Analysis + Enriched Info
    │
    ▼
Create Task Node
    │
    ├─▶ MCP Client calls Task Management Server
    │
    ▼
Task Management Server
    │
    ├─ create_trello_card()      ──▶ [Trello API]   ──▶ Trello Board
    ├─ create_notion_task()      ──▶ [Notion API]   ──▶ Notion DB
    ├─ send_discord_message()    ──▶ [Discord API]  ──▶ Discord Channel
    └─ send_email_notification() ──▶ [Email SMTP]   ──▶ Email Inbox
    │
    ▼
Actions Completed
```

## Component Interactions

### How MCP Servers Communicate

```
Agent Process                    MCP Server Process
       │                                │
       ├─ Create Subprocess             │
       │  (Start Server)                │
       │                                ▼
       │                         Server Initialized
       │                                │
       ├─ Open Stdio Connection         │
       │ ◀────────────────────────────▶ │
       │   (StdioTransport)             │
       │                                │
       ├─ Call Tool                     │
       │ {"jsonrpc": "2.0",             │
       │  "method": "tools/call",       │
       │  "params": {...}}              │
       │ ──────────────────────────────▶│
       │                                │
       │                         Execute Tool
       │                         (call API, etc)
       │                                │
       │ ◀────────────────────────────── │
       │ Return Result                  │
       │ {"jsonrpc": "2.0",             │
       │  "result": {...}}              │
       │                                │
       ├─ Process Result                │
       │                                │
       └─ Cleanup Connection            │
         (Close Stdio)                  │
```

## Server Architecture

### Each Server Follows MCP Protocol

```
┌─────────────────────────────────────┐
│      MCP Server Instance            │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  StdioServer                   │ │
│  │  • Initialize                  │ │
│  │  • Handle connections          │ │
│  │  • Manage lifecycle            │ │
│  └────────────────────────────────┘ │
│         │                            │
│         ▼                            │
│  ┌────────────────────────────────┐ │
│  │  Tool Registry                 │ │
│  │  • list_tools()                │ │
│  │  • Define tool schemas         │ │
│  └────────────────────────────────┘ │
│         │                            │
│         ▼                            │
│  ┌────────────────────────────────┐ │
│  │  Tool Handlers                 │ │
│  │  • call_tool()                 │ │
│  │  • Execute requested tool      │ │
│  │  • Return result               │ │
│  └────────────────────────────────┘ │
│                                      │
└─────────────────────────────────────┘
```

## Integration Patterns

### Pattern 1: Direct Integration
```python
# In agent.py or other module
async def get_company_info():
    client = MCPClient()
    async with client.connect_to_server("enrichment", path) as session:
        result = await client.call_tool("enrichment", "find_company_info", args)
    return result
```

### Pattern 2: Claude Desktop Integration
```json
{
  "mcpServers": {
    "enrichment": {
      "command": "python",
      "args": ["path/to/enrichment_server.py"]
    }
  }
}
```

### Pattern 3: Hybrid Approach
```python
# Use MCP for new features
# Keep existing langchain tools for compatibility
# Gradually migrate over time

if use_mcp:
    result = await mcp_client.call_tool(...)
else:
    result = legacy_tool.invoke(...)
```

## Scaling Considerations

### Adding New MCP Servers

```
Current:                    Future:
┌─────────────────┐        ┌─────────────────┐
│ Ingestion       │        │ Ingestion       │
│ Enrichment      │   ───▶ │ Enrichment      │
│ Task Management │        │ Task Management │
└─────────────────┘        │ Analysis        │
                            │ Notifications   │
                            │ Custom Tools    │
                            └─────────────────┘
```

### Performance Optimization

```
Before:           After (with MCP):
agent ─────────▶  agent ──┐
  │                       ├─▶ Ingestion Server (parallel)
  ├─ Sequential           ├─▶ Enrichment Server (parallel)
  │  tool calls          └─▶ Task Server (parallel)
  │
  └─ Blocked on each tool
```

## Monitoring & Logging

```
┌──────────────────────────────────────┐
│      Agent Process                   │
│  ┌────────────────────────────────┐  │
│  │ Logging                        │  │
│  │ • Tool calls                   │  │
│  │ • Parameters                   │  │
│  │ • Results                      │  │
│  │ • Errors                       │  │
│  └────────────────────────────────┘  │
│         │                            │
│         ▼                            │
│   logs/ directory                    │
│   • agent.log                        │
│   • server_calls.log                 │
│   • errors.log                       │
│                                      │
└──────────────────────────────────────┘
```

## Deployment Architecture

```
Production Setup:

┌─────────────────────────────────────────────┐
│           Container Orchestration           │
│        (Docker Compose or Kubernetes)       │
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │   Agent      │  │   Qdrant     │       │
│  │  Container   │  │  Container   │       │
│  └──────────────┘  └──────────────┘       │
│         │                                  │
│         ├─▶ ┌──────────────┐              │
│         │   │ Ingestion    │              │
│         │   │ Server       │              │
│         │   └──────────────┘              │
│         │                                  │
│         ├─▶ ┌──────────────┐              │
│         │   │ Enrichment   │              │
│         │   │ Server       │              │
│         │   └──────────────┘              │
│         │                                  │
│         └─▶ ┌──────────────┐              │
│             │ Task Manager │              │
│             │ Server       │              │
│             └──────────────┘              │
│                                             │
└─────────────────────────────────────────────┘
```

---

This architecture provides:
- ✅ **Modularity**: Each service is independent
- ✅ **Scalability**: Services can scale independently
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Testability**: Each component can be tested in isolation
- ✅ **Extensibility**: New services can be added easily
