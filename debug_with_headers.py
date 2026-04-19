#!/usr/bin/env python
"""Debug endpoint with detailed error"""

import requests
import json

headers = {'X-API-Key': 'test-key-1234567890123456'}
payload = {'query': 'Python', 'source': 'startup', 'limit': 3}

response = requests.post(
    'http://localhost:8000/api/v1/jobs/search',
    json=payload,
    headers=headers,
    timeout=10
)

print(f'Status: {response.status_code}')
print(f'Headers: {dict(response.headers)}')
print(f'Content: {response.text}')

try:
    data = response.json()
    print(f'\nJSON:\n{json.dumps(data, indent=2)}')
except:
    print('(Not JSON)')
