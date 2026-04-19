#!/usr/bin/env python
"""Test the fixed job search endpoint"""

import requests
import json
import sys

headers = {'X-API-Key': 'test-key-1234567890123456'}
payload = {'query': 'Python', 'source': 'startup', 'limit': 3}

try:
    response = requests.post(
        'http://localhost:8000/api/v1/jobs/search',
        json=payload,
        headers=headers,
        timeout=10
    )
    print(f'✅ Status: {response.status_code}')
    data = response.json()
    
    print(f"📊 Results: {data.get('count', 0)} opportunities found")
    print(f"🔍 Source: {data.get('source', 'unknown')}")
    print()
    
    if data.get('jobs'):
        print("=" * 60)
        for i, job in enumerate(data['jobs'], 1):
            print(f"\n({i}) {job.get('title', 'N/A')}")
            print(f"    💼 {job.get('company', 'N/A')}")
            print(f"    📍 {job.get('location', 'N/A')}")
            print(f"    💰 {job.get('budget', 'N/A')}")
            if job.get('type'):
                print(f"    🏷️  Type: {job.get('type').upper()}")
            if job.get('score'):
                print(f"    ⭐ Relevance: {job.get('score'):.2%}")
    else:
        print("⚠️  No jobs found in response")
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
