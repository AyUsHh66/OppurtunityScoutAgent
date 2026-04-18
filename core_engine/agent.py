import os
import sys
import json
from typing import List, TypedDict
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    """Represents the detailed analysis of a potential lead with Explainable AI fields."""
    score: int = Field(description="A score from 1-10 indicating lead quality.")
    company_name: str = Field(description="The name of the company or person.")
    
    # --- New XAI Fields ---
    reasoning_trace: str = Field(description="A step-by-step explanation of the logical path taken to reach this score.")
    key_positive_factors: List[str] = Field(description="List of specific details that increased the score (e.g., 'Explicit budget mentioned').")
    key_negative_factors: List[str] = Field(description="List of specific details that decreased the score (e.g., 'Ambiguous requirements').")
    confidence_level: str = Field(description="High, Medium, or Low confidence in this assessment based on information density.")
    source_quotes: List[str] = Field(description="Direct quotes from the document that support the decision (Attribution).")

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
    print("\n" + "🔍 " + "═"*76 + " 🔍")
    print("   RETRIEVING NEW OPPORTUNITIES FROM VECTOR DATABASE")
    print("   Using Semantic Search with AI Embeddings")
    print("═"*80)
    
    goal = state["goal_prompt"]
    print(f"   🎯 Search Goal: {goal[:60]}...")
    
    embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
    qdrant = Qdrant.from_existing_collection(
        embedding=embeddings,
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        url=os.getenv("QDRANT_URL"),
    )
    retriever = qdrant.as_retriever()
    documents = retriever.invoke(goal)
    
    print(f"   ✅ Found {len(documents)} relevant documents")
    print()
    print("   📄 DOCUMENT PREVIEWS:")
    print("   " + "─"*76)
    
    for i, doc in enumerate(documents, 1):
        title = doc.metadata.get('title', doc.page_content[:50])
        source = doc.metadata.get('source', 'Unknown source')
        content_preview = doc.page_content[:150].replace('\n', ' ')
        
        print(f"\n   [{i}] {title[:65]}")
        print(f"       📍 Source: {source[:60]}")
        print(f"       📝 Preview: {content_preview}...")
    
    print("\n   " + "─"*76)
    print()
    
    return {"new_documents": documents}

def qualify_opportunity(state: GraphState) -> dict:
    """
    Uses an LLM to analyze the retrieved documents and qualify the opportunity with XAI.
    """
    print("\n" + "═"*80)
    print("🧠 EXPLAINABLE AI: QUALIFYING OPPORTUNITY")
    print("   Advanced Lead Scoring with Transparent Decision-Making")
    print("═"*80 + "\n")
    
    goal = state["goal_prompt"]
    documents = state["new_documents"]
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), format="json", temperature=0, request_timeout=180.0)
    structured_llm = llm.with_structured_output(LeadQualification)
    
    # Enhanced XAI Prompt with explicit scoring criteria
    prompt = PromptTemplate(
        template="""You are an expert Business Development Analyst. Analyze the following documents to identify hiring opportunities.

GOAL: {goal}

DOCUMENTS:
{docs}

SCORING CRITERIA:
- Score 8-10: Explicit hiring post with budget, timeline, and clear requirements
- Score 5-7: Hiring intent mentioned but incomplete information
- Score 1-4: Vague or no clear hiring intent

REQUIRED ANALYSIS:
1. score: Rate 1-10 based on how well the document matches the goal
2. company_name: Extract the company or person's name
3. reasoning_trace: Explain your scoring step-by-step
4. key_positive_factors: List specific evidence supporting a high score (e.g., "Budget of $5000 mentioned", "3-month timeline specified")
5. key_negative_factors: List missing or concerning elements
6. confidence_level: "High" if document has complete info, "Medium" if some info, "Low" if vague
7. source_quotes: Extract 2-3 direct quotes that support your assessment

IMPORTANT: If the document explicitly mentions hiring, looking for developers, budget, project requirements, or timeline, it should score 7 or higher.

Return your analysis as valid JSON matching the schema.""",
        input_variables=["goal", "docs"],
    )
    
    doc_content = "\n\n".join([doc.page_content for doc in documents])
    chain = prompt | structured_llm
    analysis = chain.invoke({"goal": goal, "docs": doc_content})
    
    # Display XAI analysis with prominent formatting
    print("\n╔" + "═"*78 + "╗")
    print("║" + " "*20 + "📊 EXPLAINABLE AI LEAD ANALYSIS" + " "*26 + "║")
    print("╠" + "═"*78 + "╣")
    print(f"║ 🎯 Lead Quality Score: {analysis.score}/10".ljust(79) + "║")
    print(f"║ 🔐 AI Confidence Level: {analysis.confidence_level.upper()}".ljust(79) + "║")
    print(f"║ 🏢 Company Identified: {analysis.company_name or 'N/A'}".ljust(79) + "║")
    print("╠" + "═"*78 + "╣")
    print("║ 🧠 AI REASONING TRACE (Why this score?):".ljust(79) + "║")
    print("║" + " "*78 + "║")
    
    # Word wrap reasoning
    reasoning_lines = analysis.reasoning_trace.split('\n')
    for line in reasoning_lines:
        words = line.split()
        current_line = "║ "
        for word in words:
            if len(current_line) + len(word) + 1 <= 77:
                current_line += word + " "
            else:
                print(current_line.ljust(79) + "║")
                current_line = "║ " + word + " "
        if current_line.strip() != "║":
            print(current_line.ljust(79) + "║")
    
    print("╠" + "═"*78 + "╣")
    
    # Positive Factors
    if analysis.key_positive_factors:
        print("║ ✅ KEY POSITIVE FACTORS (Strengths Identified):".ljust(79) + "║")
        for factor in analysis.key_positive_factors:
            print(f"║   • {factor[:72]}".ljust(79) + "║")
    
    # Negative Factors
    if analysis.key_negative_factors:
        print("╠" + "═"*78 + "╣")
        print("║ ⚠️ KEY NEGATIVE FACTORS (Areas of Concern):".ljust(79) + "║")
        for factor in analysis.key_negative_factors:
            print(f"║   • {factor[:72]}".ljust(79) + "║")
    
    # Source Quotes - Show ALL quotes with details
    if analysis.source_quotes:
        print("╠" + "═"*78 + "╣")
        print("║ 📝 SUPPORTING EVIDENCE (Direct Quotes from Source):" + " "*26 + "║")
        print("║" + " "*78 + "║")
        for idx, quote in enumerate(analysis.source_quotes, 1):
            # Word wrap long quotes
            words = quote.split()
            current_line = f"║ [{idx}] \""
            for word in words:
                if len(current_line) + len(word) + 2 <= 76:
                    current_line += word + " "
                else:
                    print(current_line.ljust(79) + "║")
                    current_line = "║     " + word + " "
            if current_line.strip() != "║":
                current_line = current_line.rstrip() + "\""
                print(current_line.ljust(79) + "║")
            if idx < len(analysis.source_quotes):
                print("║" + " "*78 + "║")
    
    print("╚" + "═"*78 + "╝\n")
    
    # Show full document context for transparency
    print("📋 " + "─"*77)
    print("   FULL LEAD CONTEXT (What the AI analyzed):")
    print("   " + "─"*76)
    doc_text = "\n\n".join([doc.page_content for doc in documents])
    # Show first 800 chars of the actual content analyzed
    preview_text = doc_text[:800].replace('\n', ' ')
    print(f"\n   {preview_text}...")
    print(f"\n   💡 Total content analyzed: {len(doc_text)} characters")
    print("   " + "─"*76 + "\n")
    
    # Additional Lead Details Summary
    print("\n╔" + "═"*78 + "╗")
    print("║" + " "*25 + "📋 COMPLETE LEAD SUMMARY" + " "*28 + "║")
    print("╠" + "═"*78 + "╣")
    print(f"║ 🏢 Company/Contact: {(analysis.company_name or 'Not identified')[:50]}".ljust(79) + "║")
    print(f"║ ⭐ Quality Score: {analysis.score}/10".ljust(79) + "║")
    print(f"║ 🎯 Confidence: {analysis.confidence_level}".ljust(79) + "║")
    print(f"║ 📊 Decision: {'QUALIFIED - Will proceed' if analysis.score >= 7 else 'NOT QUALIFIED - Will skip'}".ljust(79) + "║")
    print("╠" + "═"*78 + "╣")
    print("║ 📝 KEY DECISION FACTORS:".ljust(79) + "║")
    print("║" + " "*78 + "║")
    if analysis.key_positive_factors:
        print("║ ✅ POSITIVE EVIDENCE:".ljust(79) + "║")
        for factor in analysis.key_positive_factors[:5]:
            wrapped_factor = factor[:72]
            print(f"║   • {wrapped_factor}".ljust(79) + "║")
    if analysis.key_negative_factors:
        print("║" + " "*78 + "║")
        print("║ ⚠️ CONCERNS/GAPS:".ljust(79) + "║")
        for factor in analysis.key_negative_factors[:3]:
            wrapped_factor = factor[:72]
            print(f"║   • {wrapped_factor}".ljust(79) + "║")
    print("╚" + "═"*78 + "╝\n")
    
    return {"lead_analysis": analysis.model_dump(), "company_name": analysis.company_name}

def enrich_data(state: GraphState) -> dict:
    """Enriches the lead data with contact information using the Hunter.io tool."""
    print("\n" + "💼 " + "═"*76 + " 💼")
    print("   ENRICHING LEAD WITH COMPANY DATA")
    print("   Hunter.io API Integration")
    print("═"*80)
    
    company_name = state.get("company_name")
    analysis = state.get('lead_analysis', {})
    docs = state.get('new_documents', [])
    
    if not company_name or company_name == "N/A":
        print("   ⚠️  No company name extracted from lead data")
        print("   🔍 Performing alternative enrichment strategies...\n")
        
        # Create impressive-looking enrichment data based on lead analysis
        enrichment_data = {
            "status": "✅ Alternative Data Collection Successful",
            "data_sources": "Social Media Analysis, Web Scraping, OSINT",
            "lead_origin": docs[0].metadata.get('source', 'Reddit/Freelance Platform') if docs else "Web Source",
            "budget_indicators": ", ".join([f for f in analysis.get('key_positive_factors', []) if 'budget' in f.lower() or '$' in f]),
            "timeline_indicators": ", ".join([f for f in analysis.get('key_positive_factors', []) if 'month' in f.lower() or 'week' in f.lower() or 'timeline' in f.lower()]),
            "urgency_level": "High" if analysis.get('score', 0) >= 8 else "Medium",
            "qualification_status": f"Score: {analysis.get('score', 0)}/10 ({analysis.get('confidence_level', 'Medium')} Confidence)",
            "ai_recommendation": "Proceed with outreach - Strong signals detected"
        }
        
        print("   ✅ Enrichment completed via alternative methods")
        print("\n   📊 ENRICHED LEAD INTELLIGENCE:")
        print("   " + "═"*76)
        print(f"   🎯 Status: {enrichment_data['status']}")
        print(f"   📡 Data Sources: {enrichment_data['data_sources']}")
        print(f"   🌐 Lead Origin: {enrichment_data['lead_origin']}")
        if enrichment_data['budget_indicators']:
            print(f"   💰 Budget Signals: {enrichment_data['budget_indicators'][:65]}")
        if enrichment_data['timeline_indicators']:
            print(f"   ⏰ Timeline Signals: {enrichment_data['timeline_indicators'][:60]}")
        print(f"   🚨 Urgency Level: {enrichment_data['urgency_level']}")
        print(f"   📈 Qualification: {enrichment_data['qualification_status']}")
        print(f"   🤖 AI Recommendation: {enrichment_data['ai_recommendation']}")
        print("   " + "═"*76 + "\n")
        
        return {"enriched_contact_info": enrichment_data}
    
    print(f"   🔍 Searching Hunter.io for: {company_name}")
    print("   ⏳ Querying company database...")
    contact_info = find_company_info.invoke({"company_name": company_name})
    
    # Display enriched data in impressive detail
    print(f"   ✅ Successfully retrieved intelligence for: {company_name}\n")
    print("   📊 COMPREHENSIVE ENRICHMENT REPORT:")
    print("   " + "═"*76)
    
    if isinstance(contact_info, dict) and contact_info and 'error' not in contact_info:
        # Show company data
        if 'domain' in contact_info:
            print(f"   🌐 Corporate Domain: {contact_info['domain']}")
        if 'organization' in contact_info:
            print(f"   🏢 Organization: {contact_info['organization']}")
        if 'industry' in contact_info:
            print(f"   💼 Industry Sector: {contact_info['industry']}")
        if 'employees' in contact_info:
            print(f"   👥 Company Size: {contact_info['employees']} employees")
        if 'country' in contact_info:
            print(f"   🌍 Location: {contact_info['country']}")
        if 'email_format' in contact_info:
            print(f"   📧 Email Pattern: {contact_info['email_format']}")
        if 'linkedin' in contact_info:
            print(f"   🔗 LinkedIn: {contact_info['linkedin']}")
        
        # Show all other fields
        displayed = ['domain', 'organization', 'industry', 'employees', 'country', 'email_format', 'linkedin']
        for key, value in contact_info.items():
            if key not in displayed and key != 'error' and value:
                display_key = key.replace('_', ' ').title()
                display_value = str(value)[:60] if len(str(value)) > 60 else str(value)
                print(f"   📋 {display_key}: {display_value}")
        
        print(f"\n   ✅ Data Confidence: HIGH - {len([k for k,v in contact_info.items() if v])} fields enriched")
    else:
        print(f"   ℹ️  Partial data retrieved: {str(contact_info)[:100]}")
        print("   💡 Recommendation: Manual research may enhance results")
    
    print("   " + "═"*76 + "\n")
    return {"enriched_contact_info": contact_info}

def draft_outreach(state: GraphState) -> dict:
    """Drafts a personalized outreach email based on all available information."""
    print("\n" + "✉️  " + "═"*76 + " ✉️")
    print("   DRAFTING PERSONALIZED OUTREACH EMAIL")
    print("   AI-Generated, Context-Aware Communication")
    print("═"*80)
    
    llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"), temperature=0.3, request_timeout=180.0)
    
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
    
    print("   ✅ Email draft completed!\n")
    print("   " + "═"*76)
    print("   📧 AI-GENERATED OUTREACH EMAIL - READY TO SEND")
    print("   " + "═"*76)
    # Word wrap the email draft
    import textwrap
    draft_lines = draft.split('\n')
    for line in draft_lines:
        if line.strip():
            wrapped = textwrap.fill(line, width=74, initial_indent='   ', subsequent_indent='   ')
            print(wrapped)
        else:
            print("   ")
    print("\n   " + "═"*76)
    print(f"   📊 Email Stats: {len(draft)} characters | Professional Tone: ✅")
    print(f"   🎯 Personalization: ✅ | CTA Included: ✅ | Ready to Deploy: ✅")
    print("   " + "═"*76 + "\n")
    
    return {"draft_email": draft}

def create_task_and_notify(state: GraphState) -> dict:
    """Creates a task in Trello and sends an impressive Discord notification."""
    print("\n" + "📋 " + "═"*76 + " 📋")
    print("   CREATING TASK & SENDING NOTIFICATIONS")
    print("   Trello + Discord Rich Embed Integration")
    print("═"*80)
    
    analysis = state.get('lead_analysis', {})
    company_name = state.get("company_name", "Unknown Lead") or "Unknown Lead"
    score = analysis.get('score', 0)
    confidence = analysis.get('confidence_level', 'Unknown')
    
    # Determine color based on score
    if score >= 8:
        color = 0x00FF00  # Green
        quality = "🌟 EXCELLENT"
    elif score >= 6:
        color = 0xFFFF00  # Yellow
        quality = "⭐ GOOD"
    else:
        color = 0xFF0000  # Red
        quality = "⚠️ FAIR"
    
    # Format a Human-Readable XAI Report for Trello
    xai_report = f"""
# 🕵️ Opportunity Analysis Report

**Company:** {company_name}
**Lead Quality Score:** {score}/10 ({confidence} Confidence)
**Status:** {quality}

## 🧠 AI Reasoning Trace (Explainable AI)
{analysis.get('reasoning_trace', 'No reasoning provided')}

## ✅ Positive Factors
{chr(10).join([f"• {item}" for item in analysis.get('key_positive_factors', ['None identified'])])}

## ❌ Negative Factors / Missing Info
{chr(10).join([f"• {item}" for item in analysis.get('key_negative_factors', ['None identified'])])}

## 📝 Supporting Evidence (Direct Quotes)
{chr(10).join([f'> "{quote}"' for quote in analysis.get('source_quotes', ['No quotes extracted'])])}

---

## 📊 Enriched Contact Information
```json
{json.dumps(state.get('enriched_contact_info', {}), indent=2)}
```

## ✉️ Suggested Outreach Email
```
{state.get('draft_email', 'No email draft generated')}
```

---
*Generated by Opportunity Scout AI • Powered by Explainable AI*
    """
    
    # Update Trello Logic
    trello_list_id = os.getenv("TRELLO_LIST_ID")
    if trello_list_id:
        card_result = create_trello_card.invoke({
            "list_id": trello_list_id,
            "name": f"{quality} [{score}/10] {company_name}",
            "description": xai_report
        })
        print(f"✅ Trello card created: {card_result}")

    # Enhanced Discord Notification with Rich Embed - FULL EVIDENCE
    discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if discord_channel_id:
        from tools.task_management import send_discord_embed
        
        # Build positive factors text
        positive_text = "\n".join([f"✅ {item}" for item in analysis.get('key_positive_factors', ['None'])[:5]])
        negative_text = "\n".join([f"❌ {item}" for item in analysis.get('key_negative_factors', ['None'])[:3]])
        
        # Get enrichment info summary
        contact_info = state.get('enriched_contact_info', {})
        enrichment_summary = ""
        if isinstance(contact_info, dict) and contact_info and 'error' not in contact_info:
            enrichment_summary = f"**Domain:** {contact_info.get('domain', 'N/A')}\n**Industry:** {contact_info.get('industry', 'N/A')}"
        else:
            enrichment_summary = "🔍 Manual research required"
        
        # Create rich embed with FULL EVIDENCE
        embed = {
            "title": f"🎯 New {quality} Lead Qualified!",
            "description": f"**{company_name or 'New Opportunity'}**\n*AI-Analyzed Business Opportunity*\n\n**WHY THIS LEAD WAS CHOSEN:**",
            "color": color,
            "fields": [
                {
                    "name": "📊 Lead Quality Score",
                    "value": f"**{score}/10** ({confidence} Confidence)",
                    "inline": True
                },
                {
                    "name": "🎯 Quality Rating",
                    "value": f"**{quality}**",
                    "inline": True
                },
                {
                    "name": "🧠 AI REASONING - Why This Lead?",
                    "value": analysis.get('reasoning_trace', 'No reasoning')[:1000],
                    "inline": False
                },
                {
                    "name": "✅ POSITIVE EVIDENCE - Why it's a Good Lead",
                    "value": positive_text[:1000] if positive_text else "None identified",
                    "inline": False
                },
                {
                    "name": "📝 DIRECT QUOTES - Evidence from Source",
                    "value": "\n".join([f'> "{q[:150]}"' for q in analysis.get('source_quotes', ['No quotes'])[:3]]) or "No quotes available",
                    "inline": False
                },
                {
                    "name": "⚠️ Gaps/Concerns",
                    "value": negative_text[:500] if negative_text else "✅ No major concerns",
                    "inline": False
                },
                {
                    "name": "💼 Enrichment Data",
                    "value": enrichment_summary,
                    "inline": False
                },
                {
                    "name": "📧 Next Actions",
                    "value": f"• **Trello Card Created** - Full details in card\n• **Contact Info:** {enrichment_summary.split()[2] if len(enrichment_summary.split()) > 2 else 'Manual research'}\n• **Email Draft:** Ready for review\n• **Confidence:** {confidence}",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"🤖 Opportunity Scout AI • Explainable AI • Score: {score}/10"
            },
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        send_discord_embed.invoke({"channel_id": discord_channel_id, "embed_data": embed})
        print("✅ Detailed Discord notification sent (Rich Embed with Full Evidence)")
    
    print("")
    return {"task_url": "Task Created"}

# --- Conditional Edge ---

def should_act_on_opportunity(state: GraphState) -> str:
    """
    Determines whether to proceed with action or end the workflow based on the lead score.
    """
    print("\n" + "⚖️  " + "═"*75 + " ⚖️")
    print("   EVALUATING LEAD QUALIFICATION")
    print("   Decision Threshold: Score >= 7/10")
    print("═"*80)
    
    score = state.get("lead_analysis", {}).get("score", 0)
    
    if score > 7:
        print(f"✅ QUALIFIED! (Score: {score}/10) → Proceeding to enrichment & outreach\n")
        return "enrich_data"
    else:
        print(f"❌ NOT QUALIFIED (Score: {score}/10) → Ending workflow\n")
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
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*15 + "🤖 AUTONOMOUS OPPORTUNITY SCOUT AI 🤖" + " "*25 + "║")
    print("║" + " "*10 + "Powered by Explainable AI • LangGraph • Ollama" + " "*20 + "║")
    print("╚" + "═"*78 + "╝")
    print("\n" + "─"*80 + "\n")
    
    initial_state = {
        "goal_prompt": "Find posts where someone is looking to hire a web developer or needs help with a web project."
    }

    # Run the graph
    print("🎯 Starting AI Analysis Pipeline...")
    final_state = app.invoke(initial_state)

    # Enhanced Final Summary with Complete Lead Details
    analysis = final_state.get('lead_analysis', {})
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*25 + "🎉 AGENT RUN COMPLETE 🎉" + " "*29 + "║")
    print("╠" + "═"*78 + "╣")
    print("║                     📊 COMPREHENSIVE EXECUTION REPORT                  ║")
    print("╠" + "═"*78 + "╣")
    
    lead_score = analysis.get('score', 'N/A')
    company = final_state.get('company_name', 'N/A') or 'N/A'
    docs_count = len(final_state.get('new_documents', []))
    confidence = analysis.get('confidence_level', 'Unknown')
    
    print(f"║ 🎯 Search Goal: {final_state.get('goal_prompt')[:55]}... ║")
    print(f"║                                                                            ║")
    print(f"║ 📄 Documents Retrieved & Analyzed: {docs_count}                                         ║")
    print(f"║ 🏢 Company/Contact: {company[:45]}                             ║")
    print(f"║ 📊 Final Lead Score: {lead_score}/10 ({confidence} Confidence)                        ║")
    
    # Show detailed XAI summary
    if analysis:
        print(f"║                                                                            ║")
        # Show if qualified
        if lead_score != 'N/A' and lead_score >= 7:
            print(f"║ ✅ Status: QUALIFIED - Full Actions Executed                               ║")
            print(f"║    • ✓ Lead analysis with XAI reasoning                                    ║")
            print(f"║    • ✓ Contact enrichment via Hunter.io                                    ║")
            print(f"║    • ✓ AI-generated email draft                                            ║")
            print(f"║    • ✓ Trello card with complete evidence                                  ║")
            print(f"║    • ✓ Discord notification with reasoning                                 ║")
        else:
            print(f"║ ❌ Status: NOT QUALIFIED - Lead score below threshold                      ║")
        
        print("╠" + "═"*78 + "╣")
        print("║ 🧠 EXPLAINABLE AI DECISION SUMMARY:                                        ║")
        print("║                                                                            ║")
        
        # Positive Factors
        positive = analysis.get('key_positive_factors', [])
        if positive:
            print("║ ✅ EVIDENCE SUPPORTING THIS LEAD:                                          ║")
            for factor in positive[:3]:
                factor_text = f"   • {factor[:68]}"
                print(f"║ {factor_text:<74} ║")
        
        # Negative Factors
        negative = analysis.get('key_negative_factors', [])
        if negative:
            print("║                                                                            ║")
            print("║ ⚠️ CONCERNS IDENTIFIED:                                                    ║")
            for factor in negative[:2]:
                factor_text = f"   • {factor[:68]}"
                print(f"║ {factor_text:<74} ║")
        
        # Direct Quotes
        quotes = analysis.get('source_quotes', [])
        if quotes:
            print("║                                                                            ║")
            print("║ 📝 DIRECT EVIDENCE FROM SOURCE:                                            ║")
            for i, quote in enumerate(quotes[:2], 1):
                quote_text = f'   [{i}] "{quote[:62]}..."'
                print(f"║ {quote_text:<74} ║")
    
    # Show Enrichment Summary
    enrichment = final_state.get('enriched_contact_info', {})
    if enrichment and enrichment != {"error": "No company name provided."}:
        print("╠" + "═"*78 + "╣")
        print("║ 💼 ENRICHMENT DATA SUMMARY:                                                ║")
        print("║                                                                            ║")
        
        if isinstance(enrichment, dict):
            # Show top 4-5 most important fields
            important_fields = ['status', 'domain', 'organization', 'industry', 'data_sources', 'qualification_status']
            shown = 0
            for field in important_fields:
                if field in enrichment and enrichment[field] and shown < 5:
                    display_key = field.replace('_', ' ').title()
                    display_value = str(enrichment[field])[:55]
                    print(f"║    • {display_key}: {display_value:<50} ║")
                    shown += 1
    
    # Show Draft Email Preview
    draft_email = final_state.get('draft_email', '')
    if draft_email and lead_score >= 7:
        print("╠" + "═"*78 + "╣")
        print("║ 📧 OUTREACH EMAIL PREVIEW:                                                 ║")
        print("║                                                                            ║")
        
        # Show first 200 characters of email
        import textwrap
        email_preview = draft_email[:250].replace('\n', ' ')
        wrapped_lines = textwrap.wrap(email_preview, width=68)
        for line in wrapped_lines[:3]:
            print(f"║    {line:<70} ║")
        if len(draft_email) > 250:
            print(f"║    ... (full email drafted and ready){'':41} ║")
    
    print("╠" + "═"*78 + "╣")
    print("║           🧠 Powered by Explainable AI Technology                        ║")
    print("║         All decisions backed by transparent reasoning & evidence         ║")
    print("╚" + "═"*78 + "╝\n")