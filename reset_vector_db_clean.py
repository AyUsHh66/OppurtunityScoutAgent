#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reset Vector Database and Reingest Data
- Backup current Qdrant collection
- Clear/reset the collection
- Reingest fresh test data
"""

import os
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("[RESET] BUSINESS AGENT 2.0 - VECTOR DATABASE RESET & REINGEST")
print("="*80 + "\n")

# Step 1: Backup current database
print("[BACKUP] STEP 1: BACKING UP CURRENT DATABASE")
print("-" * 80)

backup_dir = Path("qdrant_backups")
backup_dir.mkdir(exist_ok=True)

if Path("qdrant_storage").exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"qdrant_backup_{timestamp}"
    
    try:
        shutil.copytree("qdrant_storage", backup_path)
        print(f"[OK] Backed up to: {backup_path}")
    except Exception as e:
        print(f"[WARN] Backup failed: {e}")
else:
    print("[INFO] No existing database to backup")

print()

# Step 2: Clear the collection
print("[CLEAR] STEP 2: CLEARING VECTOR DATABASE")
print("-" * 80)

try:
    from qdrant_client import QdrantClient
    
    # Connect to Qdrant
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    client = QdrantClient(url=qdrant_url)
    
    # Delete old collection if it exists
    collection_name = "opportunity_scout_collection"
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"[OK] Deleted collection: {collection_name}")
    except Exception as e:
        print(f"[INFO] Collection didn't exist or already deleted: {e}")
    
    print("[OK] Vector database cleared")
    
except Exception as e:
    print(f"[ERROR] Error clearing database: {e}")
    print(f"[WARN] Make sure Qdrant is running at {qdrant_url}")
    sys.exit(1)

print()

# Step 3: Create fresh test data
print("[CREATE] STEP 3: CREATING FRESH TEST DATA")
print("-" * 80)

try:
    from langchain_ollama import OllamaEmbeddings
    from langchain_qdrant import Qdrant
    from langchain_core.documents import Document
    
    # Sample hiring posts for initial data
    hiring_posts = [
        Document(
            page_content="""
            Title: Looking for a Senior Python Developer - Budget $15,000
            
            We're a fintech startup looking for an experienced Python developer
            to build our core data pipeline and API services.
            
            Requirements:
            - 5+ years Python experience
            - Knowledge of FastAPI/Django
            - Experience with PostgreSQL and Redis
            - DevOps knowledge (Docker, Kubernetes) is a plus
            
            Budget: $15,000-$20,000 for 3-month project
            Timeline: Start immediately
            Location: Remote
            
            Please send your portfolio and availability!
            """,
            metadata={
                "source": "test_data",
                "title": "Senior Python Developer Needed",
                "company": "FinTech Startup",
                "budget": "$15,000-$20,000",
                "ingest_timestamp": time.time()
            }
        ),
        Document(
            page_content="""
            [HIRING] React Developer - $8,000 Project
            
            Digital agency seeking React expert for e-commerce platform rebuild.
            
            Project Details:
            - Rebuild React frontend with TypeScript
            - Integrate with existing REST API
            - Implement real-time features with WebSockets
            - Must have experience with Redux/Zustand
            
            Budget: $8,000, approximately 4 weeks
            Start: ASAP
            
            Send GitHub profile and previous React projects!
            """,
            metadata={
                "source": "test_data",
                "title": "React Developer - E-commerce Project",
                "company": "Digital Agency",
                "budget": "$8,000",
                "ingest_timestamp": time.time()
            }
        ),
        Document(
            page_content="""
            Hiring: Full-Stack Developer - $100/hour
            
            Growing SaaS company looking for full-stack expertise.
            
            Stack: Next.js, Node.js, PostgreSQL, AWS
            - Build new features for our platform
            - Architect scalable solutions
            - Mentor junior developers (optional)
            
            Rate: $100/hour, 20-30 hours/week
            Duration: Ongoing (could be permanent)
            Location: Remote
            
            Contact: careers@startupname.com
            """,
            metadata={
                "source": "test_data",
                "title": "Full-Stack Developer - SaaS",
                "company": "SaaS Startup",
                "budget": "$100/hour",
                "ingest_timestamp": time.time()
            }
        ),
        Document(
            page_content="""
            [FOR HIRE] DevOps Engineer Available
            
            Looking for DevOps/Infrastructure opportunities.
            
            Skills:
            - Kubernetes, Docker, Terraform
            - AWS and GCP expertise
            - CI/CD pipeline design
            - Prometheus, ELK stack monitoring
            
            Available: Full-time contract or project-based
            Rate: $90-120/hour depending on scope
            Notice: 2 weeks
            
            Portfolio: github.com/devops-engineer
            """,
            metadata={
                "source": "test_data",
                "title": "DevOps Engineer Available",
                "company": "Freelancer",
                "budget": "$90-120/hour",
                "ingest_timestamp": time.time()
            }
        ),
    ]
    
    print(f"[DOCS] Creating embeddings for {len(hiring_posts)} documents...")
    
    # Initialize embeddings
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    embeddings = OllamaEmbeddings(
        model=os.getenv("LLM_MODEL", "phi"),
        base_url=ollama_url
    )
    
    # Create Qdrant vector store with fresh data
    vector_store = Qdrant.from_documents(
        documents=hiring_posts,
        embedding=embeddings,
        url=qdrant_url,
        collection_name=collection_name,
        prefer_grpc=False
    )
    
    print(f"[OK] Created {len(hiring_posts)} test documents in Qdrant")
    print(f"[OK] Collection: {collection_name}")
    
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("   Make sure the following are installed:")
    print("   - langchain-ollama")
    print("   - langchain-qdrant")
    print("   Run: pip install langchain-ollama langchain-qdrant")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error creating test data: {e}")
    print(f"\n[WARN] Troubleshooting:")
    print(f"   1. Is Qdrant running? (Expected at {qdrant_url})")
    print(f"   2. Is Ollama running? (Expected at {ollama_url})")
    print(f"   3. Check environment variables in .env file")
    sys.exit(1)

print()

# Step 4: Verify the data
print("[VERIFY] STEP 4: VERIFYING DATA")
print("-" * 80)

try:
    # Query to verify
    from langchain_ollama import OllamaEmbeddings
    from langchain_qdrant import Qdrant
    
    embeddings = OllamaEmbeddings(
        model=os.getenv("LLM_MODEL", "phi"),
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
    )
    
    vector_store = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    
    # Test search
    results = vector_store.similarity_search("Python developer", k=3)
    print(f"[OK] Database query test successful: Found {len(results)} results")
    
    if results:
        print(f"\n   Sample result:")
        print(f"   - Title: {results[0].metadata.get('title', 'N/A')}")
        print(f"   - Company: {results[0].metadata.get('company', 'N/A')}")
        print(f"   - Budget: {results[0].metadata.get('budget', 'N/A')}")
    
except Exception as e:
    print(f"[WARN] Verification failed: {e}")

print()

# Final status
print("="*80)
print("[SUCCESS] DATABASE RESET COMPLETE!")
print("="*80)
print()
print("[SUMMARY] Status:")
if Path("qdrant_storage").exists():
    print(f"  * Backup created: {backup_dir}/qdrant_backup_{timestamp}")
print(f"  * Database cleared and recreated")
print(f"  * Test data ingested: {len(hiring_posts)} documents")
print(f"  * Collection: {collection_name}")
print()
print("[READY] Next steps:")
print("  1. Start the server: python -m uvicorn app_production:app --reload")
print("  2. To ingest Reddit data: python ingest_reddit_simple.py")
print("  3. To search the data: python show_all_leads.py")
print()
