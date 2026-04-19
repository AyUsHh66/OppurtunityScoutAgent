#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Vector Database Reset (No Ollama Required)
- Clears the Qdrant collection
- Creates a fresh database with placeholder data
- Ready for the server to use
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("[RESET] VECTOR DATABASE RESET (Simple - No Ollama Required)")
print("="*80 + "\n")

# Step 1: Connect and clear collection
print("[CLEAR] Clearing Qdrant collection...")
print("-" * 80)

try:
    from qdrant_client import QdrantClient
    
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    client = QdrantClient(url=qdrant_url)
    
    collection_name = "opportunity_scout_collection"
    
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"[OK] Deleted collection: {collection_name}")
    except Exception as e:
        print(f"[INFO] Collection status: {e}")
    
    print("[OK] Database cleared\n")
    
except Exception as e:
    print(f"[ERROR] Failed to connect to Qdrant at {qdrant_url}")
    print(f"[WARN] Please check:")
    print(f"  1. Is Qdrant running?")
    print(f"  2. Is it accessible at: {qdrant_url}")
    print(f"  3. Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
    sys.exit(1)

print()

# Step 2: Recreate collection
print("[CREATE] Recreating collection from scratch...")
print("-" * 80)

try:
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
    )
    
    # Create collection with placeholder settings
    # We'll use this until we can get embeddings
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,  # Placeholder dimension for sparse vectors
            distance=Distance.COSINE
        ),
    )
    
    print(f"[OK] Created collection: {collection_name}")
    print(f"[OK] Vector dimension: 384 (ready for embeddings)")
    print()
    
    # Create placeholder data points with random vectors
    import random
    import time
    
    print("[DATA] Adding placeholder documents...")
    
    placeholder_data = [
        {
            "title": "Senior Python Developer Needed",
            "company": "FinTech Startup",
            "budget": "$15,000-$20,000",
            "content": "We are looking for a Senior Python Developer with 5+ years experience"
        },
        {
            "title": "React Developer - E-commerce Project",
            "company": "Digital Agency",
            "budget": "$8,000",
            "content": "Need experienced React developer for e-commerce platform rebuild"
        },
        {
            "title": "Full-Stack Developer - SaaS",
            "company": "SaaS Startup",
            "budget": "$100/hour",
            "content": "Growing SaaS company needs full-stack developer with Next.js expertise"
        },
        {
            "title": "DevOps Engineer Available",
            "company": "Freelancer",
            "budget": "$90-120/hour",
            "content": "DevOps engineer available for Kubernetes and AWS infrastructure work"
        },
    ]
    
    points = []
    for idx, item in enumerate(placeholder_data):
        # Create simple random vector
        random_vector = [random.random() for _ in range(384)]
        
        point = PointStruct(
            id=idx + 1,
            vector=random_vector,
            payload={
                "title": item["title"],
                "company": item["company"],
                "budget": item["budget"],
                "content": item["content"],
                "source": "placeholder",
                "timestamp": time.time()
            }
        )
        points.append(point)
        print(f"  [{idx+1}] {item['title']}")
    
    # Upload points
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"\n[OK] Added {len(points)} placeholder documents")
    
except Exception as e:
    print(f"[ERROR] Failed to create collection: {e}")
    sys.exit(1)

print()

# Step 3: Verify
print("[VERIFY] Verifying database...")
print("-" * 80)

try:
    collection_info = client.get_collection(collection_name=collection_name)
    point_count = collection_info.points_count
    
    print(f"[OK] Collection verified!")
    print(f"[OK] Total documents: {point_count}")
    print()
    
    # List documents
    print("[DATA] Current documents in collection:")
    points = client.scroll(collection_name=collection_name, limit=100)[0]
    for point in points:
        if point.payload:
            print(f"  - {point.payload.get('title', 'N/A')}")
            print(f"    Company: {point.payload.get('company', 'N/A')}")
            print(f"    Budget: {point.payload.get('budget', 'N/A')}")
    
except Exception as e:
    print(f"[WARN] Verification failed: {e}")

print()
print("="*80)
print("[SUCCESS] DATABASE RESET COMPLETE!")
print("="*80)
print()
print("[INFO] Status:")
print(f"  * Collection: {collection_name}")
print(f"  * Status: Ready for ingestion")
print(f"  * Documents: {len(placeholder_data)} placeholder items added")
print()
print("[NEXT] Next steps:")
print()
print("OPTION 1: Start Server with Current Data")
print("  1. Start Ollama: ollama serve (in another terminal)")
print("  2. Start Server: python -m uvicorn app_production:app --reload")
print("  3. Access API: http://localhost:8000/docs")
print()
print("OPTION 2: Ingest Real Data from Reddit")
print("  1. Set Reddit credentials in .env file:")
print("     REDDIT_CLIENT_ID=...")
print("     REDDIT_CLIENT_SECRET=...")
print("     REDDIT_USER_AGENT=...")
print("  2. Run: python ingest_reddit_simple.py")
print()
print("OPTION 3: Continue with Placeholder Data")
print("  * Server will work with placeholder vectors")
print("  * Search results will be based on random similarity")
print("  * Replace vectors later when Ollama is available")
print()
print("[TIP] To see all configuration options:")
print("  * See .env file for settings")
print("  * See config/settings.py for defaults")
print()
