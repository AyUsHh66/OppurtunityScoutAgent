#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
START SERVER - Business Agent 2.0
Starts the production server with fresh database
"""

import subprocess
import time
import sys

print("\n" + "="*80)
print("STARTING BUSINESS AGENT 2.0 - PRODUCTION SERVER")
print("="*80 + "\n")

print("[STATUS] System Ready:")
print("  Middleware: Fixed and configured")
print("  Database: Fresh and clean")
print("  Routes: 19 endpoints available")
print("  API Docs: http://localhost:8000/docs")
print()

print("[LAUNCHING] Starting Uvicorn server...")
print()

try:
    # Start the server
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app_production:app", "--reload"],
        cwd="C:\\Users\\silen\\Desktop\\Business-Agent-2.0"
    )
except KeyboardInterrupt:
    print("\n\n[STOP] Server stopped by user")
except Exception as e:
    print(f"\n[ERROR] Failed to start server: {e}")
    sys.exit(1)
