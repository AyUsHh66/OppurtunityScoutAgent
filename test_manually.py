#!/usr/bin/env python
"""Test manually to see the exact error"""

from fastapi.testclient import TestClient
from app_production import app
import json

client = TestClient(app)

# Test 1: Health endpoint
print("Test 1: Health endpoint")
r = client.get("/health")
print(f"Status: {r.status_code}, Response: {r.json()}\n")

# Test 2: Job search with correct source
print("Test 2: Job search with 'database' source")
r = client.post(
    "/api/v1/jobs/search",
    json={"query": "Python", "source": "database", "limit": 3},
    headers={"X-API-Key": "test-key-1234567890123456"}
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Count: {data.get('count')}")
    if data.get('jobs'):
        print(f"First job: {data['jobs'][0].get('title')}")
else:
    print(f"Error: {r.json()}")
print()

# Test 3: Job search with 'startup' source (should work now)
print("Test 3: Job search with 'startup' source")
r = client.post(
    "/api/v1/jobs/search",
    json={"query": "Python", "source": "startup", "limit": 3},
    headers={"X-API-Key": "test-key-1234567890123456"}
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Count: {data.get('count')}")
    if data.get('jobs'):
        print(f"First job: {data['jobs'][0].get('title')}")
else:
    print(f"Error: {r.json()}")
