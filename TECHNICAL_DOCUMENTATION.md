# Opportunity Scout Agent - Technical Documentation

## Project Overview
An autonomous AI agent that discovers business opportunities by ingesting data from multiple sources (RSS, Reddit, websites), qualifying leads using LLM analysis, enriching contact information, and automating outreach through task management integrations.

## Technology Stack

### Core Framework
- **LangChain**: Framework for building LLM applications
- **LangGraph**: State machine orchestration for multi-step AI workflows
- **Pydantic**: Data validation and settings management

### AI/ML Components
- **Ollama**: Local LLM inference (currently using `phi` model)
- **LangChain-Ollama**: Integration layer for Ollama embeddings and chat models
- **Vector Embeddings**: 2560-dimensional vectors from Phi model

### Data Storage
- **Qdrant**: Vector database for semantic search
  - Collection: `opportunity_scout_collection`
  - Running on: `http://localhost:6333`
  - Stores chunked documents with embeddings
  - Deployed via Docker Compose

### Data Sources
- **RSS Feeds**: Via `feedparser`
- **Reddit**: Via `praw` (Reddit API wrapper)
- **Web Scraping**: Via `newspaper3k` and `RecursiveUrlLoader` with BeautifulSoup4
- **Twitter**: Via `tweepy` (configured but not actively used)

### External APIs & Integrations
- **Hunter.io**: Email finding and company enrichment
- **Clearbit**: Company data enrichment (optional)
- **Trello**: Task management and card creation
- **Notion**: Alternative task management
- **Discord**: Notification system via bot

### Model Context Protocol (MCP)
New standardized interface for AI tool interaction:
- **3 MCP Servers**:
  1. Ingestion Server - Data collection tools
  2. Enrichment Server - Lead research tools  
  3. Task Management Server - Action/notification tools
- **MCP Client**: Connects to servers via stdio transport
- Compatible with Claude Desktop and other MCP clients

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│              LangGraph Workflow                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Retrieve │→ │ Qualify  │→ │ Enrich   │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│       ↓              ↓              ↓           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Draft   │→ │ Create   │→ │   END    │     │
│  │  Email   │  │  Task    │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
           ↓                    ↓
    ┌──────────────┐    ┌──────────────┐
    │   Qdrant     │    │  External    │
    │   Vector DB  │    │  APIs        │
    └──────────────┘    └──────────────┘
```

### File Structure
```
Business-Agent-2.0/
├── core_engine/
│   ├── agent.py                    # Main LangGraph workflow
│   └── agent_mcp_example.py        # MCP integration example
├── perception/
│   ├── ingest.py                   # Data ingestion module
│   └── test_newspaper.py           # Web scraping tests
├── tools/
│   ├── enrichment.py               # Hunter.io integration
│   └── task_management.py          # Trello/Notion/Discord tools
├── mcp_servers/                    # NEW: MCP implementation
│   ├── ingestion_server.py         # MCP data ingestion server
│   ├── enrichment_server.py        # MCP enrichment server
│   ├── task_management_server.py   # MCP task server
│   └── mcp_client.py               # MCP client library
├── config/                         # Empty config directory
├── qdrant_storage/                 # Qdrant persistent data
├── .env                            # Environment configuration
├── requirements.txt                # Python dependencies
└── docker-compose.yml              # Qdrant deployment
```

## Data Flow

### 1. Ingestion Pipeline
```python
# Sources → Documents → Chunks → Embeddings → Qdrant

RSS/Reddit/Web → RSSFeedLoader/RedditPostsLoader/RecursiveUrlLoader
                → Document objects with metadata
                → RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
                → OllamaEmbeddings (phi model, 2560 dims)
                → Qdrant.from_documents()
                → Vector storage with metadata
```

**Key Parameters:**
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Embedding dimensions: 2560
- Max recursion depth for web scraping: 2

### 2. Agent Workflow (LangGraph State Machine)

**State Schema:**
```python
class GraphState(TypedDict):
    goal_prompt: str                    # Search query
    new_documents: List[Document]       # Retrieved docs
    lead_analysis: dict                 # LLM analysis result
    is_qualified: bool                  # Qualification flag
    company_name: str                   # Extracted company
    enriched_contact_info: dict         # Hunter.io data
    draft_email: str                    # Generated email
    task_url: str                       # Trello/Notion URL
```

**Node Execution:**

1. **retrieve_new_opportunities**
   - Input: `goal_prompt`
   - Process: Semantic search in Qdrant
   - Output: `new_documents`
   - Retriever: similarity search with embeddings

2. **qualify_opportunity**
   - Input: `goal_prompt`, `new_documents`
   - LLM: ChatOllama with structured output
   - Schema: LeadQualification (score: int, justification: str, company_name: str)
   - Output: `lead_analysis`, `company_name`
   - Temperature: 0 (deterministic)

3. **Conditional Edge: should_act_on_opportunity**
   - Logic: score > 7 → proceed, else END
   - Routes to: enrich_data OR END

4. **enrich_data**
   - Input: `company_name`
   - API: Hunter.io company enrichment
   - Process: Construct domain from company name
   - Output: `enriched_contact_info`

5. **draft_outreach**
   - Input: All previous state
   - LLM: ChatOllama (temperature: 0.3)
   - Process: Generate personalized email
   - Output: `draft_email`

6. **create_task_and_notify**
   - Actions:
     - Create Trello card with lead details
     - Send Discord notification
   - Output: `task_url`

### 3. MCP Server Architecture

**Protocol:** JSON-RPC 2.0 over stdio
**Transport:** StdioServerTransport

**Server Structure:**
```python
class MCPServer:
    def __init__(self):
        self.server = StdioServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        # Returns tool schemas
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        # Executes tool with arguments
```

**Available Tools:**

**Ingestion Server:**
- `ingest_rss_feeds(urls: list[str])` → processes RSS feeds
- `ingest_reddit(subreddits: list[str])` → fetches Reddit posts (25 per subreddit)
- `scrape_website(url: str, max_depth: int)` → recursive web crawling

**Enrichment Server:**
- `find_company_info(company_name: str, domain: str)` → Hunter.io API
- `find_email(domain: str, first_name: str, last_name: str)` → Email finder
- `verify_email(email: str)` → Email validation
- `get_company_info_clearbit(domain: str)` → Clearbit API

**Task Management Server:**
- `create_trello_card(list_id: str, name: str, description: str)`
- `create_notion_task(title: str, content: str)`
- `send_discord_message(channel_id: str, message: str)`
- `send_email_notification(recipient: str, subject: str, body: str)`

## Configuration

### Environment Variables (.env)
```env
# LLM & Vector DB
OLLAMA_MODEL="phi"                              # Changed from llama3 for memory
OLLAMA_BASE_URL="http://localhost:11434"
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION_NAME="opportunity_scout_collection"

# Reddit API
REDDIT_CLIENT_ID="xiOLRL4YMbn6j1kQIvnWkA"
REDDIT_CLIENT_SECRET="[SECRET]"
REDDIT_USER_AGENT="OpportunityScout/1.0 by Swimming_Apricot_401"

# Enrichment APIs
HUNTER_API_KEY="[CONFIGURED]"
CLEARBIT_API_KEY="[OPTIONAL]"

# Task Management
TRELLO_API_KEY="[CONFIGURED]"
TRELLO_TOKEN="[CONFIGURED]"
TRELLO_LIST_ID="[CONFIGURED]"
NOTION_API_KEY="[OPTIONAL]"
NOTION_DATABASE_ID="[OPTIONAL]"

# Notifications
DISCORD_BOT_TOKEN="[CONFIGURED]"
DISCORD_CHANNEL_ID="[CONFIGURED]"
```

### Docker Compose (Qdrant)
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: opportunity_scout_qdrant
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC
    volumes:
      - ./qdrant_storage:/qdrant/storage
    restart: always
```

## Dependencies (requirements.txt)

### Core
- langchain
- langgraph
- langchain-core
- langchain-community
- langchain-text-splitters
- langchain-ollama
- langchain-qdrant
- qdrant-client

### Data Sources
- feedparser (RSS)
- listparser (OPML)
- newspaper3k==0.2.8 (web scraping)
- praw (Reddit)
- tweepy (Twitter)
- beautifulsoup4
- lxml

### Utilities
- python-dotenv
- requests
- pydantic
- APScheduler

### MCP
- mcp (Model Context Protocol SDK)

## Execution Flow

### Running the Agent
```bash
# Set environment
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONPATH='.'

# Run agent
.venv/Scripts/python.exe core_engine/agent.py
```

### Prerequisites
1. **Ollama running** with phi model loaded
2. **Qdrant running** via Docker Compose
3. **Environment variables** configured in .env
4. **Python virtual environment** activated (.venv)

### Data Ingestion
```bash
# Ingest data first
.venv/Scripts/python.exe perception/ingest.py

# This:
# 1. Scrapes test website (Lilian Weng's blog)
# 2. Chunks content (390 chunks from 16 documents)
# 3. Generates embeddings via Ollama
# 4. Stores in Qdrant (force_recreate=True)
```

## Performance Characteristics

### Current Setup
- **LLM Model**: Phi (1.6GB, fits in 2.6GB memory requirement)
- **Vector Dimensions**: 2560
- **Document Chunks**: ~390 from test dataset
- **Retrieval**: Top 4 documents by default
- **Lead Qualification**: Threshold score > 7

### Memory Requirements
- Ollama Phi: ~2.6GB system memory
- Qdrant: Minimal (lightweight vector store)
- Python runtime: ~500MB

### API Rate Limits
- Hunter.io: Free tier limits apply
- Trello: Standard API limits
- Discord: Bot rate limits
- Reddit: OAuth rate limits

## Error Handling

### Common Issues
1. **Vector dimension mismatch**: Recreate collection with force_recreate=True
2. **Ollama memory**: Switch to smaller model (phi instead of llama3)
3. **Docker not running**: Start Docker Desktop before docker-compose
4. **PYTHONPATH not set**: Required for module imports
5. **Unicode encoding**: Set PYTHONIOENCODING='utf-8' on Windows

### Graceful Degradation
- Enrichment API failure: Continues with error in enriched_contact_info
- Trello creation failure: Logged but doesn't stop workflow
- Discord notification failure: Continues silently

## Extension Points

### Adding New Data Sources
1. Create loader in `perception/ingest.py`
2. Add MCP tool in `mcp_servers/ingestion_server.py`
3. Follow pattern: load → add metadata → process_and_store_documents()

### Adding New Enrichment APIs
1. Add API client in `tools/enrichment.py` or MCP server
2. Add tool decorator: `@tool`
3. Update agent node to call new tool

### Adding New Task Integrations
1. Add integration in `tools/task_management.py`
2. Add MCP tool in `mcp_servers/task_management_server.py`
3. Update create_task_and_notify node

## Testing

### Test Files
- `test_mcp_setup.py`: Verifies MCP configuration
- `demo_mcp.py`: Demonstrates MCP servers running
- `perception/test_newspaper.py`: Tests web scraping

### Manual Testing
```bash
# Test MCP setup
python test_mcp_setup.py

# Test MCP servers
python demo_mcp.py

# Test ingestion
python perception/ingest.py
```

## Deployment Considerations

### Production Recommendations
1. Use managed Qdrant instance (Qdrant Cloud)
2. Implement proper API key rotation
3. Add monitoring and logging
4. Use production-grade LLM (GPT-4, Claude)
5. Implement retry logic with exponential backoff
6. Add rate limiting for external APIs
7. Use message queue for async processing
8. Implement proper error tracking (Sentry)

### Scalability
- Each MCP server can scale independently
- Qdrant can be clustered
- LangGraph workflows can be parallelized
- Add Redis for caching API responses

## Key Technical Decisions

1. **Why LangGraph?** State machine pattern for complex multi-step workflows
2. **Why Qdrant?** Lightweight, fast, Docker-friendly vector database
3. **Why Ollama?** Local inference, no API costs, privacy
4. **Why MCP?** Standardization, Claude Desktop integration, reusable tools
5. **Why Phi model?** Smaller footprint, faster inference, lower memory requirements
6. **Why force_recreate?** Model changes require dimension consistency

## API Endpoints

### Qdrant
- REST: http://localhost:6333
- Dashboard: http://localhost:6333/dashboard
- Collections API: http://localhost:6333/collections

### Ollama
- API: http://localhost:11434
- Generate: POST /api/generate
- Embeddings: POST /api/embeddings
- Models: GET /api/tags

## Current Status

### Working Features ✅
- Data ingestion from web sources
- Vector embeddings with Phi model
- Semantic search in Qdrant
- Lead qualification with LLM
- Email drafting
- Trello integration
- Discord notifications
- MCP servers implementation

### Limitations ⚠️
- Hunter.io enrichment has domain mapping issues
- Limited to test dataset (Lilian Weng's blog)
- No scheduling/automation (APScheduler configured but not active)
- No Reddit/RSS ingestion in main workflow
- Email sending not implemented (placeholder)

### Next Steps 🚀
- Integrate RSS/Reddit feeds into main workflow
- Add scheduling for periodic ingestion
- Improve company domain detection
- Add more enrichment sources
- Implement email sending
- Add monitoring and analytics
- Create web dashboard
