import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
# UPDATED: Import directly from pydantic
from pydantic import BaseModel, Field

from langchain_core.prompts import PromptTemplate
from langchain_ollama.chat_models import ChatOllama
from langchain_qdrant import Qdrant
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# --- Import our new tools ---
from tools.enrichment import find_company_info
from tools.task_management import create_trello_card, send_discord_message

# Load environment variables from.env file
load_dotenv()

class LeadQualification(BaseModel):
    """Represents the analysis of a potential lead."""
    score: int = Field(description="A score from 1-10 indicating lead quality, where 10 is the highest.")
    justification: str = Field(description="A brief analysis explaining the score and why this is or isn't a good lead.")
    company_name: str = Field(description="The name of the company or person, if identifiable. Otherwise, 'N/A'.")

class GraphState(TypedDict):
    """
    Represents the state of our Opportunity Scout agent.
    """
    goal_prompt: str
    new_documents: List
    lead_analysis: dict
    is_qualified: bool
    company_name: str
    enriched_contact_info: dict
    draft_email: str
    task_url: str

# --- Graph Nodes ---

def retrieve_new_opportunities(state: GraphState) -> dict:
    """
    Retrieves new documents from the Qdrant vector store based on the goal prompt.
    """
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
    """
    Uses an LLM to analyze the retrieved documents and qualify the opportunity.
    """
    print("---QUALIFYING OPPORTUNITY---")
    goal = state["goal_prompt"]
    documents = state["new_documents"]
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), format="json", temperature=0)
    structured_llm = llm.with_structured_output(LeadQualification)
    
    prompt = PromptTemplate(
        template="""You are a business analyst. Your goal is to identify high-quality leads based on the provided documents.
        Analyze the following documents in the context of this goal: '{goal}'
        
        Documents:
        {docs}
        
        Based on the documents, does this represent a high-quality lead?
        Provide a score from 1-10 and a brief justification.
        """,
        input_variables=["goal", "docs"],
    )
    
    doc_content = "\n\n".join([doc.page_content for doc in documents])
    chain = prompt | structured_llm
    analysis = chain.invoke({"goal": goal, "docs": doc_content})
    print(f"Lead Analysis: {analysis}")
    
    # UPDATED: Using model_dump() instead of the deprecated dict()
    return {"lead_analysis": analysis.model_dump(), "company_name": analysis.company_name}

def enrich_data(state: GraphState) -> dict:
    """Enriches the lead data with contact information using the Hunter.io tool."""
    print("---ENRICHING DATA---")
    company_name = state.get("company_name")
    if not company_name or company_name == "N/A":
        print("No company name to enrich.")
        return {"enriched_contact_info": {"error": "No company name provided."}}
        
    contact_info = find_company_info.invoke({"company_name": company_name})
    print(f"Enrichment Info: {contact_info}")
    return {"enriched_contact_info": contact_info}

def draft_outreach(state: GraphState) -> dict:
    """Drafts a personalized outreach email based on all available information."""
    print("---DRAFTING OUTREACH EMAIL---")
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), temperature=0.3)
    
    prompt = PromptTemplate(
        template="""You are a friendly business development representative.
        Based on the following information, draft a concise, personalized, and non-aggressive outreach email.
        Reference their specific problem or recent news. Do not invent information.

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
    }).content # Use.content to get the string from the AIMessage
    print(f"Drafted Email: {draft}")
    return {"draft_email": draft}

def create_task_and_notify(state: GraphState) -> dict:
    """Creates a task in Trello and sends a notification to Discord."""
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
    
    # Create Trello card (Make sure to add TRELLO_LIST_ID to your.env file)
    trello_list_id = os.getenv("TRELLO_LIST_ID")
    if not trello_list_id:
        print("TRELLO_LIST_ID not set in.env file. Skipping Trello card creation.")
        trello_result = "Skipped"
    else:
        trello_result = create_trello_card.invoke({
            "list_id": trello_list_id,
            "name": f"New Lead: {company_name}",
            "description": task_description
        })
    print(trello_result)
    
    # Send Discord notification
    discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if discord_channel_id:
        notification_message = f"🚀 New Opportunity Found: **{company_name}**\n- **Score:** {state.get('lead_analysis', {}).get('score')}\n- **Justification:** {state.get('lead_analysis', {}).get('justification')}\n- **Action:** Task created in Trello."
        send_discord_message.invoke({"channel_id": discord_channel_id, "message": notification_message})
    
    return {"task_url": trello_result}

# --- Conditional Edge ---

def should_act_on_opportunity(state: GraphState) -> str:
    """
    Determines whether to proceed with action or end the workflow based on the lead score.
    """
    print("---CHECKING IF LEAD IS QUALIFIED---")
    score = state.get("lead_analysis", {}).get("score", 0)
    
    if score > 7:
        print("---LEAD IS QUALIFIED, PROCEEDING TO ACTION---")
        return "enrich_data"
    else:
        print("---LEAD NOT QUALIFIED, ENDING WORKFLOW---")
        return END

# --- Build the Graph ---

workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("retrieve", retrieve_new_opportunities)
workflow.add_node("qualify", qualify_opportunity)
workflow.add_node("enrich_data", enrich_data)
workflow.add_node("draft_outreach", draft_outreach)
workflow.add_node("create_task_and_notify", create_task_and_notify)

# Set the entry point
workflow.set_entry_point("retrieve")

# Add edges
workflow.add_edge("retrieve", "qualify")
workflow.add_conditional_edges(
    "qualify",
    should_act_on_opportunity,
)
workflow.add_edge("enrich_data", "draft_outreach")
workflow.add_edge("draft_outreach", "create_task_and_notify")
workflow.add_edge("create_task_and_notify", END)

# Compile the graph
app = workflow.compile()

# --- Run the Agent ---
if __name__ == "__main__":
    print("🚀 Starting Autonomous Opportunity Scout...")
    
    initial_state = {
        "goal_prompt": "Find posts where someone is looking to hire a web developer or needs help with a web project."
    }

    # Run the graph
    final_state = app.invoke(initial_state)

    print("\n---AGENT RUN COMPLETE---")
    print("Final State:")
    print(final_state)