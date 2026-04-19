#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPLETE SYSTEM RESET
- Delete all database files
- Clear all cached data
- Start fresh with new ingestion
"""

import os
import sys
import shutil
from pathlib import Path

print("\n" + "="*80)
print("[FULL RESET] Business Agent - Complete System Cleanup")
print("="*80 + "\n")

# Step 1: Remove all Qdrant data
print("[CLEANUP] Step 1: Removing all Qdrant data files...")
print("-" * 80)

paths_to_remove = [
    "qdrant_storage",
    "qdrant_backups",
]

for path in paths_to_remove:
    if Path(path).exists():
        try:
            shutil.rmtree(path)
            print(f"[OK] Deleted: {path}")
        except Exception as e:
            print(f"[WARN] Failed to delete {path}: {e}")
    else:
        print(f"[INFO] Not found: {path}")

print()

# Step 2: Remove cached Python files
print("[CLEANUP] Step 2: Removing Python cache files...")
print("-" * 80)

cache_paths = [
    "__pycache__",
    ".pytest_cache",
    "logs",
]

for path in cache_paths:
    if Path(path).exists():
        try:
            shutil.rmtree(path)
            print(f"[OK] Deleted: {path}")
        except Exception as e:
            print(f"[WARN] Failed to delete {path}: {e}")

print()

# Step 3: Verify cleanup
print("[VERIFY] Step 3: Verifying cleanup...")
print("-" * 80)

for path in paths_to_remove:
    if not Path(path).exists():
        print(f"[OK] {path} - Removed")
    else:
        print(f"[WARN] {path} - Still exists")

print()

# Step 4: Recreate necessary directories
print("[CREATE] Step 4: Recreating necessary directories...")
print("-" * 80)

dirs_to_create = [
    "logs",
    "qdrant_storage",
]

for dir_path in dirs_to_create:
    Path(dir_path).mkdir(exist_ok=True)
    print(f"[OK] Created: {dir_path}")

print()

# Step 5: Initialize fresh Qdrant collection
print("[INIT] Step 5: Initializing fresh Qdrant collection...")
print("-" * 80)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import random
    import time
    
    # Connect to Qdrant (create local connection if needed)
    client = QdrantClient(path="./qdrant_storage")
    
    collection_name = "opportunity_scout_collection"
    
    # Create collection
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        ),
    )
    
    print(f"[OK] Created collection: {collection_name}")
    
    # Add sample documents
    sample_docs = [
        {
            "title": "Senior Python Developer Needed",
            "company": "FinTech Startup",
            "budget": "$15,000-$20,000",
            "content": "Python developer with 5+ years experience for fintech data pipeline"
        },
        {
            "title": "React Developer - $8,000 Project",
            "company": "Digital Agency",
            "budget": "$8,000",
            "content": "React expert needed for e-commerce platform frontend rebuild"
        },
        {
            "title": "Full-Stack Developer - $100/hour",
            "company": "SaaS Startup",
            "budget": "$100/hour",
            "content": "Next.js full-stack developer for ongoing SaaS platform development"
        },
        {
            "title": "DevOps Engineer Available",
            "company": "Freelancer",
            "budget": "$90-120/hour",
            "content": "DevOps engineer with Kubernetes and AWS expertise available for contract work"
        },
    ]
    
    points = []
    for idx, doc in enumerate(sample_docs):
        vector = [random.random() for _ in range(384)]
        point = PointStruct(
            id=idx + 1,
            vector=vector,
            payload={
                "title": doc["title"],
                "company": doc["company"],
                "budget": doc["budget"],
                "content": doc["content"],
                "source": "startup",
                "timestamp": time.time()
            }
        )
        points.append(point)
        print(f"  [{idx+1}] {doc['title']}")
    
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"[OK] Added {len(sample_docs)} sample documents")
    
except Exception as e:
    print(f"[ERROR] Failed to initialize collection: {e}")
    print("[INFO] This is okay - will be created on first server startup")

print()
print("="*80)
print("[SUCCESS] FULL RESET COMPLETE!")
print("="*80)
print()
print("[READY] System is clean and ready to start!")
print()
print("Next steps:")
print()
print("1. Start the server:")
print("   python -m uvicorn app_production:app --reload")
print()
print("2. The server will start fresh with:")
print("   - Clean database")
print("   - 4 sample job opportunities")
print("   - All systems reset")
print()
print("API will be available at: http://localhost:8000")
print("Docs available at: http://localhost:8000/docs")
print()
