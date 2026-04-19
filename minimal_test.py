#!/usr/bin/env python
"""Minimal test to trace errors"""

import traceback
import asyncio

print("Testing imports and function directly...")

try:
    from app_production import search_opportunities_in_qdrant
    from app_production import app
    
    print("✓ Imports successful")
    
    # Test the search function
    print("\nTesting search_opportunities_in_qdrant...")
    results = search_opportunities_in_qdrant("Python", limit=3)
    print(f"✓ Got {len(results)} results")
    
    # Now test the actual endpoint by creating a test client
    print("\nTesting via FastAPI test client...")
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/jobs/search",
        json={"query": "Python", "source": "startup", "limit": 3},
        headers={"X-API-Key": "test-key-1234567890123456"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
