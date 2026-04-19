#!/usr/bin/env python
"""Debug the search function"""

from app_production import search_opportunities_in_qdrant
import traceback

try:
    results = search_opportunities_in_qdrant('Python', limit=3)
    print(f'Found {len(results)} opportunities')
    for r in results:
        print(f'  - {r.get("title", "N/A")} ({r.get("company", "N/A")})')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
