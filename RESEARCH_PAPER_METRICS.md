# Business Agent 2.0 - Research Paper Metrics & Specifications

**System Name:** Opportunity Scout Agent (Business Agent 2.0)  
**Architecture Type:** Model Context Protocol (MCP) Based Multi-Agent System  
**Primary Use Case:** Autonomous Lead Discovery, Qualification, and Enrichment  
**Date Extracted:** January 25, 2026

---

## 1. SYSTEM ARCHITECTURE SPECIFICATIONS

### 1.1 Core Framework
- **Orchestration Framework:** LangGraph (State Machine-based)
- **LLM Framework:** LangChain
- **Protocol Standard:** Model Context Protocol (MCP)
- **Programming Language:** Python 3.10+
- **Architecture Pattern:** Microservices with MCP Communication

### 1.2 MCP Server Configuration
| Component | Count | Communication Protocol |
|-----------|-------|----------------------|
| MCP Servers | 3 | stdio/JSON-RPC |
| Total MCP Tools | 11 | Standardized MCP Interface |
| Client Instances | 1 | Async Python Client |

**MCP Servers Breakdown:**
1. **Ingestion Server:** 3 tools (RSS, Reddit, Web Scraping)
2. **Enrichment Server:** 4 tools (Company Info, Email Finding, Verification, Clearbit)
3. **Task Management Server:** 4 tools (Trello, Notion, Discord, Email)

### 1.3 Workflow Architecture
- **Total Workflow Stages:** 5
- **Decision Points:** 2
- **State Variables:** 8

**Workflow Stages:**
1. `retrieve_new_opportunities` - Data Retrieval
2. `qualify_opportunity` - Lead Qualification
3. `enrich_company_info` - Data Enrichment
4. `draft_outreach_email` - Email Generation
5. `create_task_and_notify` - Task Creation

---

## 2. VECTOR DATABASE SPECIFICATIONS

### 2.1 Qdrant Configuration
```
Database: Qdrant Vector Store
Deployment: Docker Container (localhost:6333)
Collection Name: opportunity_scout_collection
```

### 2.2 Vector Parameters
| Parameter | Value | Purpose |
|-----------|-------|---------|
| Vector Dimensions | 4096 | Embedding size from Ollama Phi model |
| Distance Metric | Cosine | Similarity measurement |
| Shard Number | 1 | Data partitioning |
| Replication Factor | 1 | Data redundancy |
| Write Consistency | 1 | Write confirmation threshold |
| On-Disk Payload | true | Storage optimization |

### 2.3 HNSW Index Configuration
| Parameter | Value | Description |
|-----------|-------|-------------|
| M (connections) | 16 | Number of bi-directional links per element |
| EF Construct | 100 | Size of dynamic candidate list |
| Full Scan Threshold | 10,000 | Vector count before index activation |
| Max Indexing Threads | 0 | Auto (system-determined) |
| On-Disk Index | false | In-memory for performance |

### 2.4 Optimizer Configuration
| Parameter | Value |
|-----------|-------|
| Deleted Threshold | 0.2 (20%) |
| Vacuum Min Vector Number | 1,000 |
| Indexing Threshold | 10,000 |
| Flush Interval | 5 seconds |

### 2.5 WAL (Write-Ahead Log) Configuration
| Parameter | Value |
|-----------|-------|
| WAL Capacity | 32 MB |
| Segments Ahead | 0 |
| Retain Closed Segments | 1 |

---

## 3. TEXT PROCESSING SPECIFICATIONS

### 3.1 Document Chunking Parameters
```python
Splitter: RecursiveCharacterTextSplitter
Chunk Size: 1,000 characters
Chunk Overlap: 200 characters (20% overlap)
Length Function: len (character-based)
Separator Regex: false
```

**Rationale:**
- 1,000 characters provides optimal context window for semantic coherence
- 200-character overlap ensures context preservation across chunks
- Prevents information loss at chunk boundaries

### 3.2 Embedding Model
```
Model: Ollama (Phi Model)
Base URL: http://localhost:11434
Output Dimensions: 4,096
Embedding Type: Dense Vector Representation
```

---

## 4. LLM CONFIGURATION

### 4.1 Language Model Parameters

**For Lead Qualification (Deterministic):**
```python
Model: Ollama Phi
Temperature: 0.0
Output Format: Structured JSON
Mode: with_structured_output
```

**For Email Generation (Creative):**
```python
Model: Ollama Phi
Temperature: 0.3
Output Format: Natural Language
Context Window: Full lead context
```

### 4.2 Structured Output Schema
The system uses Pydantic models for type-safe LLM outputs:

**LeadQualification Schema:**
- `score`: Integer (1-10 scale)
- `company_name`: String
- `reasoning_trace`: String (step-by-step explanation)
- `key_positive_factors`: List[String]
- `key_negative_factors`: List[String]
- `confidence_level`: String (High/Medium/Low)
- `source_quotes`: List[String] (direct evidence)

---

## 5. DATA SOURCE INTEGRATIONS

### 5.1 Ingestion Sources
| Source Type | Loader | Metadata Tracking |
|-------------|--------|-------------------|
| RSS Feeds | RSSFeedLoader | Yes (timestamp) |
| Reddit | RedditPostsLoader | Yes (subreddit, timestamp) |
| Web Pages | RecursiveUrlLoader | Yes (URL, crawl depth) |
| Twitter/X | Tweepy | Configured (not active) |

### 5.2 Web Scraping Configuration
```python
Parser: BeautifulSoup4 (lxml parser)
Max Depth: 2 (configurable)
Extractor: Custom HTML → Plain Text
Target: <body> content extraction
```

---

## 6. EXTERNAL API INTEGRATIONS

### 6.1 Enrichment APIs
| API Service | Purpose | Tools |
|-------------|---------|-------|
| Hunter.io | Email discovery & verification | 3 tools |
| Clearbit | Company data enrichment | 1 tool |

### 6.2 Task Management APIs
| Platform | Purpose | Integration Type |
|----------|---------|-----------------|
| Trello | Task card creation | REST API |
| Notion | Task page creation | REST API |
| Discord | Notifications | Webhook |
| Email | Notifications | SMTP |

---

## 7. EXPLAINABLE AI (XAI) FEATURES

### 7.1 Transparency Components
The system implements explainable AI through:

1. **Reasoning Trace:** Step-by-step logical explanation
2. **Factor Attribution:** Positive/negative influence identification
3. **Confidence Assessment:** High/Medium/Low confidence levels
4. **Source Quotes:** Direct evidence from documents
5. **Score Justification:** Explicit 1-10 scoring rationale

### 7.2 Lead Qualification Threshold
```
Qualification Score: > 7 out of 10
Decision Point: Binary (Qualified/Not Qualified)
Factors Considered: Budget, hiring intent, tech stack match
```

---

## 8. SYSTEM PERFORMANCE CHARACTERISTICS

### 8.1 Processing Pipeline Stages (Estimated)
| Stage | Typical Duration |
|-------|-----------------|
| Document Retrieval | 1-3 seconds |
| Lead Qualification | 2-5 seconds |
| Company Enrichment | 3-6 seconds |
| Email Drafting | 2-4 seconds |
| Task Creation | 1-3 seconds |
| **Total Pipeline** | **9-21 seconds** |

*Note: These are estimated ranges based on typical LLM and API response times*

### 8.2 Scalability Metrics
```
Concurrent MCP Servers: 3
Async Capable: Yes
Vector Search: O(log N) with HNSW
Database Persistence: Docker volume-mounted
```

---

## 9. DATA STORAGE & PERSISTENCE

### 9.1 Storage Architecture
```
Primary Storage: Qdrant Vector Database
Persistence: Docker Volume (./qdrant_storage)
Collections: 1 (opportunity_scout_collection)
Index Type: HNSW (Hierarchical Navigable Small World)
```

### 9.2 Metadata Storage
Each document chunk includes:
- `source`: Origin URL/feed
- `ingest_timestamp`: Unix timestamp
- `content`: Chunked text
- `vector`: 4,096-dimensional embedding

---

## 10. SECURITY & CONFIGURATION

### 10.1 Environment Variables
All sensitive data managed via `.env` file:
- API keys (Hunter.io, Clearbit, Trello, Notion, Discord)
- Database URLs
- Model endpoints
- Authentication tokens

### 10.2 Configuration Management
```
Format: Environment Variables
Storage: .env file (excluded from version control)
Loader: python-dotenv
Validation: Pydantic models
```

---

## 11. TECHNOLOGY STACK SUMMARY

### 11.1 Core Dependencies
| Category | Technologies |
|----------|-------------|
| **AI/ML** | LangChain, LangGraph, Ollama |
| **Vector DB** | Qdrant (Docker) |
| **Protocol** | Model Context Protocol (MCP) |
| **Data Processing** | RecursiveCharacterTextSplitter |
| **Web** | BeautifulSoup4, newspaper3k, feedparser |
| **APIs** | requests, praw (Reddit), tweepy |
| **Schema** | Pydantic (type validation) |
| **Environment** | python-dotenv |

### 11.2 Development Tools
```
Container Runtime: Docker Compose
Package Manager: pip
Configuration: requirements.txt
Documentation: Markdown
```

---

## 12. WORKFLOW STATE MANAGEMENT

### 12.1 GraphState Schema
The system maintains state across workflow stages:

```python
GraphState (TypedDict):
  - goal_prompt: str
  - new_documents: List[Document]
  - lead_analysis: dict
  - is_qualified: bool
  - company_name: str
  - enriched_contact_info: dict
  - draft_email: str
  - task_url: str
```

**State Transitions:** 8 variables tracked across 5 workflow nodes

---

## 13. QUALITY ASSURANCE

### 13.1 Lead Quality Scoring
```
Scale: 1-10 (integer)
Threshold: 7 (qualification cutoff)
Method: LLM-based structured output
Validation: Pydantic schema enforcement
```

### 13.2 Data Quality Controls
- Temperature 0.0 for deterministic qualification
- Structured JSON output format
- Schema validation with Pydantic
- Source quote attribution for transparency

---

## 14. DEPLOYMENT ARCHITECTURE

### 14.1 Container Configuration
```yaml
Service: qdrant
Image: qdrant/qdrant:latest
Ports: 6333 (REST), 6334 (gRPC)
Volumes: ./qdrant_storage:/qdrant/storage
Restart Policy: unless-stopped
```

### 14.2 Process Architecture
```
Main Process: Python Agent (agent.py)
Background Services: 3 MCP Servers (stdio)
Database: Qdrant Container
LLM Service: Ollama (localhost:11434)
```

---

## 15. RESEARCH METRICS SUMMARY

### 15.1 System Complexity Metrics
| Metric | Value |
|--------|-------|
| Total Python Files | 16 |
| MCP Servers | 3 |
| Total Tools | 11 |
| Workflow Stages | 5 |
| State Variables | 8 |
| External APIs | 7 |
| Vector Dimensions | 4,096 |
| Chunk Size | 1,000 chars |
| Qualification Threshold | 7/10 |

### 15.2 Integration Complexity
```
Data Sources: 4 (RSS, Reddit, Web, Twitter)
Enrichment Services: 2 (Hunter.io, Clearbit)
Task Platforms: 4 (Trello, Notion, Discord, Email)
Total External Integrations: 10
```

---

## 16. INNOVATION HIGHLIGHTS

### 16.1 Novel Contributions
1. **MCP-Based Architecture:** Standardized tool interface for AI agents
2. **Explainable AI Integration:** Built-in transparency and reasoning traces
3. **Multi-Source Ingestion:** Unified processing of diverse data sources
4. **Structured LLM Output:** Type-safe lead qualification with Pydantic
5. **Autonomous Pipeline:** End-to-end lead discovery to task creation

### 16.2 Technical Advantages
- **Modularity:** Independent MCP servers enable parallel development
- **Reusability:** MCP tools work with Claude Desktop and other clients
- **Scalability:** Async-capable architecture with HNSW indexing
- **Transparency:** XAI features provide audit trails
- **Standardization:** Protocol-based communication reduces coupling

---

## 17. USE CASE METRICS

### 17.1 Operational Workflow
```
Input: User goal/search query
Process: 5-stage autonomous pipeline
Output: Qualified leads with tasks created
Automation Level: Fully autonomous (human oversight optional)
```

### 17.2 Lead Processing
```
Documents Retrieved: Configurable (default: top-k from Qdrant)
Qualification Rate: Variable (depends on source quality)
Enrichment Success: Depends on API availability
Task Creation: Automated (Trello/Notion/Discord)
```

---

## 18. COMPARATIVE ADVANTAGES

### 18.1 vs Traditional Systems
| Aspect | Traditional | This System |
|--------|-------------|-------------|
| Tool Integration | Hardcoded | MCP Protocol |
| LLM Explainability | Black box | XAI features |
| Data Sources | Single | Multi-source (4) |
| Orchestration | Custom code | LangGraph FSM |
| Scalability | Monolithic | Microservices |

### 18.2 Protocol Benefits
- **Interoperability:** Works with Claude Desktop and other MCP clients
- **Maintainability:** Tools updated independently
- **Testability:** Each server tested in isolation
- **Extensibility:** New tools added without agent modifications

---

## 19. FUTURE RESEARCH DIRECTIONS

### 19.1 Potential Enhancements
1. Multi-model ensemble for qualification
2. Real-time streaming ingestion
3. Distributed Qdrant deployment
4. Advanced RAG with reranking
5. Multi-agent collaboration frameworks

### 19.2 Research Questions
- Optimal chunk size for different document types
- Temperature impact on lead qualification accuracy
- HNSW parameter tuning for domain-specific data
- MCP overhead vs direct integration performance
- XAI feature impact on user trust

---

## 20. CITATION INFORMATION

### 20.1 System Components to Cite

**Core Frameworks:**
- LangChain: Framework for LLM applications
- LangGraph: State machine orchestration
- Model Context Protocol: Anthropic's standardized tool interface

**Vector Database:**
- Qdrant: Vector similarity search engine
- HNSW: Approximate nearest neighbor algorithm

**LLM:**
- Ollama: Local LLM inference platform
- Phi Model: Microsoft's efficient language model

### 20.2 Key Papers & References
- HNSW: Malkov & Yashunin (2018) - Efficient and robust approximate nearest neighbor search
- Vector Embeddings: Dense passage retrieval research
- MCP: Anthropic Model Context Protocol specification
- LangGraph: ReACT pattern and state machines for AI agents

---

## USAGE IN RESEARCH PAPERS

### Recommended Citation Format:

**For Architecture Description:**
"The system implements a Model Context Protocol (MCP) based architecture with 3 independent servers providing 11 standardized tools, orchestrated via LangGraph state machine with 5 workflow stages."

**For Vector Database:**
"Document embeddings (4,096 dimensions) are stored in Qdrant vector database using HNSW indexing (M=16, EF=100) with cosine similarity metric."

**For Text Processing:**
"Documents are split into 1,000-character chunks with 200-character overlap using RecursiveCharacterTextSplitter for optimal semantic coherence."

**For AI Explainability:**
"The system implements explainable AI through structured outputs including reasoning traces, factor attribution, confidence levels, and source quotes for transparency."

**For Performance:**
"The autonomous pipeline processes leads through 5 stages (retrieval, qualification, enrichment, email drafting, task creation) in an estimated 9-21 seconds per lead."

---

## VERIFICATION NOTE

✅ **All metrics in this document are extracted from actual source code, configuration files, and system architecture.**

**Sources:**
- `qdrant_storage/collections/opportunity_scout_collection/config.json` - Vector DB configuration
- `core_engine/agent.py` - Workflow and LLM parameters
- `perception/ingest.py` - Text processing configuration
- `mcp_servers/*.py` - MCP server specifications
- `requirements.txt` - Technology stack
- `docker-compose.yml` - Deployment configuration

**Not Included:** Sample data generation values (these are synthetic for demonstration only)

---

**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**System Version:** Business Agent 2.0 with MCP Integration
