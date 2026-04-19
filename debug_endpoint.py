#!/usr/bin/env python
"""Test the endpoint and show full error"""

import requests
import json

headers = {'X-API-Key': 'test-key-1234567890123456'}
payload = {'query': 'Python', 'source': 'startup', 'limit': 3}

try:
    response = requests.post(
        'http://localhost:8000/api/v1/jobs/search',
        json=payload,
        headers=headers,
        timeout=10
    )
    print(f'Status: {response.status_code}')
    print(f'Response text: {response.text}')
    print()
    
    try:
        data = response.json()
        print(f'JSON: {json.dumps(data, indent=2)}')
    except:
        print('Could not parse JSON response')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
