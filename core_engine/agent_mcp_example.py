"""
Example: Updated Opportunity Scout Agent using MCP
This shows how to integrate MCP servers into your existing agent workflow.

You can gradually migrate your agent to use these patterns.
"""

import os
import json
import asyncio
from typing import List, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from langchain_core.prompts import PromptTemplate
from langchain_ollama.chat_models import ChatOllama
from langchain_qdrant import Qdrant
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# Import MCP client (when ready to integrate)
# from mcp_servers.mcp_client import MCPClient

load_dotenv()

class LeadQualification(BaseModel):
    """Represents the analysis of a potential lead."""
    score: int = Field(description="A score from 1-10 indicating lead quality, where 10 is the highest.")
    justification: str = Field(description="A brief analysis explaining the score.")
    company_name: str = Field(description="The name of the company or person.")

class GraphState(TypedDict):
    """Represents the state of our Opportunity Scout agent."""
    goal_prompt: str
    new_documents: List
    lead_analysis: dict
    is_qualified: bool
    company_name: str
    enriched_contact_info: dict
    draft_email: str
    task_url: str

# ============================================================
# EXAMPLE: How to use MCP for data ingestion
# ============================================================

async def retrieve_new_opportunities_with_mcp(state: GraphState) -> dict:
    """
    EXAMPLE: Retrieve documents using MCP Ingestion Server
    
    This shows how you could migrate from langchain loaders to MCP.
    """
    # Option 1: Using MCP (when integrated)
    """
    from mcp_servers.mcp_client import MCPClient
    
    client = MCPClient()
    async with client.connect_to_server("ingestion", "mcp_servers/ingestion_server.py") as session:
        # Ingest from RSS
        result = await client.call_tool("ingestion", "ingest_rss_feeds", {
            "urls": [
                "https://news.ycombinator.com/rss",
                "https://techcrunch.com/feed/"
            ]
        })
        print(f"Ingestion result: {result}")
    """
    
    # Option 2: Current approach (still works)
    print("---RETRIEVING NEW OPPORTUNITIES---")
    goal = state["goal_prompt"]
    embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
    qdrant = Qdrant.from_existing_collection(
        embedding=embeddings,
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        url=os.getenv("QDRANT_URL"),
    )
    retriever = qdrant.as_retriever()
    documents = retriever.invoke(goal)
    print(f"Found {len(documents)} new documents.")
    return {"new_documents": documents}

def qualify_opportunity(state: GraphState) -> dict:
    """Qualify opportunities (unchanged from original)"""
    print("---QUALIFYING OPPORTUNITY---")
    goal = state["goal_prompt"]
    documents = state["new_documents"]
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), format="json", temperature=0)
    structured_llm = llm.with_structured_output(LeadQualification)
    
    prompt = PromptTemplate(
        template="""You are a business analyst. Your goal is to identify high-quality leads.
        Analyze the following documents in the context of this goal: '{goal}'
        
        Documents:
        {docs}
        
        Based on the documents, does this represent a high-quality lead?
        """,
        input_variables=["goal", "docs"],
    )
    
    doc_content = "\n\n".join([doc.page_content for doc in documents])
    chain = prompt | structured_llm
    analysis = chain.invoke({"goal": goal, "docs": doc_content})
    print(f"Lead Analysis: {analysis}")
    
    return {"lead_analysis": analysis.model_dump(), "company_name": analysis.company_name}

# ============================================================
# EXAMPLE: How to use MCP for enrichment
# ============================================================

async def enrich_data_with_mcp(state: GraphState) -> dict:
    """
    EXAMPLE: Enrich lead data using MCP Enrichment Server
    
    This demonstrates how to migrate enrichment logic to MCP.
    """
    print("---ENRICHING DATA---")
    company_name = state.get("company_name")
    
    if not company_name or company_name == "N/A":
        print("No company name to enrich.")
        return {"enriched_contact_info": {"error": "No company name provided."}}
    
    # Option 1: Using MCP (when integrated)
    """
    from mcp_servers.mcp_client import MCPClient
    
    client = MCPClient()
    async with client.connect_to_server("enrichment", "mcp_servers/enrichment_server.py") as session:
        result = await client.call_tool("enrichment", "find_company_info", {
            "company_name": company_name
        })
        
        if result.get("status") == "success":
            enriched_info = result.get("data", {})
        else:
            enriched_info = {"error": result.get("message")}
    """
    
    # Option 2: Current approach
    from tools.enrichment import find_company_info
    contact_info = find_company_info.invoke({"company_name": company_name})
    
    print(f"Enrichment Info: {contact_info}")
    return {"enriched_contact_info": contact_info}

def draft_outreach(state: GraphState) -> dict:
    """Draft outreach email (unchanged from original)"""
    print("---DRAFTING OUTREACH EMAIL---")
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), temperature=0.3)
    
    prompt = PromptTemplate(
        template="""You are a friendly business development representative.
        Based on the following information, draft a concise, personalized outreach email.

        Goal: {goal}
        Original Documents: {docs}
        Lead Analysis: {analysis}
        Contact Info: {contact}
        
        Draft the email below:
        """,
        input_variables=["goal", "docs", "analysis", "contact"],
    )
    
    doc_content = "\n\n".join([doc.page_content for doc in state["new_documents"]])
    
    chain = prompt | llm
    draft = chain.invoke({
        "goal": state["goal_prompt"],
        "docs": doc_content,
        "analysis": json.dumps(state["lead_analysis"]),
        "contact": json.dumps(state["enriched_contact_info"])
    }).content
    
    print(f"Drafted Email: {draft}")
    return {"draft_email": draft}

# ============================================================
# EXAMPLE: How to use MCP for task management
# ============================================================

async def create_task_and_notify_with_mcp(state: GraphState) -> dict:
    """
    EXAMPLE: Create tasks and send notifications using MCP
    
    This shows how to use the Task Management MCP Server.
    """
    print("---CREATING TASK AND NOTIFYING---")
    
    company_name = state.get("company_name", "Unknown Lead")
    task_description = f"""
    **Lead Analysis:**
    {json.dumps(state.get('lead_analysis'), indent=2)}

    **Enriched Info:**
    {json.dumps(state.get('enriched_contact_info'), indent=2)}

    **Draft Email:**
    {state.get('draft_email')}
    """
    
    # Option 1: Using MCP (when integrated)
    """
    from mcp_servers.mcp_client import MCPClient
    
    client = MCPClient()
    async with client.connect_to_server("task_management", "mcp_servers/task_management_server.py") as session:
        # Create Trello card
        trello_result = await client.call_tool("task_management", "create_trello_card", {
            "list_id": os.getenv("TRELLO_LIST_ID"),
            "name": f"New Lead: {company_name}",
            "description": task_description
        })
        print(f"Trello Result: {trello_result}")
        
        # Send Discord notification
        discord_result = await client.call_tool("task_management", "send_discord_message", {
            "channel_id": os.getenv("DISCORD_CHANNEL_ID"),
            "message": f"🚀 New Opportunity: **{company_name}**"
        })
        print(f"Discord Result: {discord_result}")
    """
    
    # Option 2: Current approach
    from tools.task_management import create_trello_card, send_discord_message
    
    trello_list_id = os.getenv("TRELLO_LIST_ID")
    if trello_list_id:
        trello_result = create_trello_card.invoke({
            "list_id": trello_list_id,
            "name": f"New Lead: {company_name}",
            "description": task_description
        })
        print(trello_result)
    
    discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if discord_channel_id:
        notification_message = f"🚀 New Opportunity Found: **{company_name}**"
        send_discord_message.invoke({"channel_id": discord_channel_id, "message": notification_message})
    
    return {"task_url": "Trello card created"}

def should_act_on_opportunity(state: GraphState) -> str:
    """Determine if lead is qualified (unchanged)"""
    print("---CHECKING IF LEAD IS QUALIFIED---")
    score = state.get("lead_analysis", {}).get("score", 0)
    
    if score > 7:
        print("---LEAD IS QUALIFIED, PROCEEDING TO ACTION---")
        return "enrich_data"
    else:
        print("---LEAD NOT QUALIFIED, ENDING WORKFLOW---")
        return END

# ============================================================
# Build the Graph (unchanged pattern)
# ============================================================

workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("retrieve", retrieve_new_opportunities_with_mcp)
workflow.add_node("qualify", qualify_opportunity)
workflow.add_node("enrich_data", enrich_data_with_mcp)
workflow.add_node("draft_outreach", draft_outreach)
workflow.add_node("create_task_and_notify", create_task_and_notify_with_mcp)

# Set entry point
workflow.set_entry_point("retrieve")

# Add edges
workflow.add_edge("retrieve", "qualify")
workflow.add_conditional_edges("qualify", should_act_on_opportunity)
workflow.add_edge("enrich_data", "draft_outreach")
workflow.add_edge("draft_outreach", "create_task_and_notify")
workflow.add_edge("create_task_and_notify", END)

# Compile the graph
app = workflow.compile()

# ============================================================
# Run the Agent
# ============================================================

if __name__ == "__main__":
    print("🚀 Starting Autonomous Opportunity Scout (MCP-Ready)...")
    
    initial_state = {
        "goal_prompt": "Find posts where someone is looking to hire a web developer.",
    }

    # Run the graph (synchronously)
    final_state = app.invoke(initial_state)

    print("\n---AGENT RUN COMPLETE---")
    print("Final State:")
    print(final_state)
