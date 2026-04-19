#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Database Reset Guide
Shows all the steps needed to clear vector DB and restart ingestions
"""

import os
from pathlib import Path

print("\n" + "="*80)
print("[GUIDE] COMPLETE DATABASE RESET & RESTART GUIDE")
print("="*80 + "\n")

print("[STEP 1] Check System Requirements")
print("-" * 80)
print("""
The Business Agent requires the following services to be running:

1. QDRANT Vector Database (Required)
   - Running at: http://localhost:6333
   - Start with: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   - Or: qdrant standalone

2. OLLAMA Local LLM (Required for embeddings)
   - Running at: http://localhost:11434
   - Download: https://ollama.com/download
   - After install, run: ollama serve
   - Pull model: ollama pull phi (or mistral, neural-chat)

3. FastAPI Server (Your application)
   - This will run at: http://localhost:8000
   - Docs available at: http://localhost:8000/docs

Current status:
""")

import subprocess

# Check Qdrant
try:
    import requests
    response = requests.get("http://localhost:6333/health", timeout=2)
    print("[OK] Qdrant is running at http://localhost:6333")
except:
    print("[WARN] Qdrant NOT running - Please start it with:")
    print("       docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")

# Check Ollama
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    print("[OK] Ollama is running at http://localhost:11434")
except:
    print("[WARN] Ollama NOT running - Please start it with:")
    print("       ollama serve")

print()
print()

print("[STEP 2] Reset Vector Database")
print("-" * 80)
print("""
To clear the existing collection and start fresh:

Option A: Full Reset (Recommended)
---------------------------------
Run this command to backup old data and reingest test data:

    python reset_vector_db_clean.py

This will:
1. Backup current database to: qdrant_backups/
2. Delete the opportunity_scout_collection
3. Create 4 fresh test documents
4. Verify the data can be queried

Option B: Manual Reset
----------------------
If you prefer to clear only the collection:

    python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://localhost:6333')
try:
    client.delete_collection('opportunity_scout_collection')
    print('[OK] Collection deleted')
except Exception as e:
    print(f'[INFO] {e}')
"

Option C: Complete Wipe (Nuclear Option)
-----------------------------------------
Delete the entire qdrant_storage directory:

    rmdir /s /q qdrant_storage
    mkdir qdrant_storage

Then reingest data when starting the server.

""")
print()

print("[STEP 3] Reingest Data")
print("-" * 80)
print("""
After resetting the database, reingest data using:

Option A: Ingest Test Data (Recommended - No Reddit credentials needed)
-----------------------------------------------------------------------
The reset script already creates 4 hiring opportunities.

Option B: Ingest Real Data from Reddit
---------------------------------------
Requires Reddit API credentials. Set these in your .env file:

    REDDIT_CLIENT_ID=your_client_id
    REDDIT_CLIENT_SECRET=your_client_secret
    REDDIT_USER_AGENT=your_user_agent

Then run:

    python ingest_reddit_simple.py

This will:
1. Fetch posts from: r/forhire, r/freelance, r/hiring
2. Create embeddings using Ollama
3. Store in Qdrant

Option C: Ingest from Multiple Sources
--------------------------------------
The perception/ingest.py supports multiple data sources:
- Reddit (subreddits)
- HackerNews Jobs
- RSS Feeds
- Custom data

""")
print()

print("[STEP 4] Start the Application Server")
print("-" * 80)
print("""
Once the database is reset and data is ingested:

Development Mode (with auto-reload):
------------------------------------
    python -m uvicorn app_production:app --reload

Production Mode (single worker):
---------------------------------
    python -m uvicorn app_production:app --host 0.0.0.0 --port 8000

Production Mode (multiple workers):
------------------------------------
    pip install gunicorn
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app_production:app

Then access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

""")
print()

print("[STEP 5] Verify Everything Works")
print("-" * 80)
print("""
Test the API with these commands:

1. Health Check:
   curl http://localhost:8000/health

2. Search for opportunities:
   curl -X POST http://localhost:8000/api/v1/jobs/search \\
     -H "X-API-Key: test-key-1234567890123456" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "Python developer", "source": "test_data", "limit": 5}'

3. View all data:
   python show_all_leads.py

4. Access API Documentation:
   Open http://localhost:8000/docs in your browser

""")
print()

print("="*80)
print("[COMPLETE] Reset & Restart Guide")
print("="*80)
print()
print("For detailed help on any step, see:")
print("  - PRODUCTION_DEPLOYMENT.md")
print("  - DEPLOYMENT_GUIDE.md")
print("  - README.md")
print()
