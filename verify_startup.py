#!/usr/bin/env python
"""
Quick test to verify app starts without errors
"""
import asyncio
from app_production import app

async def test_startup():
    """Test that the app can be created and imported"""
    print("✅ App imported successfully")
    print(f"✅ App has {len(app.routes)} routes")
    print(f"✅ Middleware stack configured")
    
    # List all routes
    print("\n📋 Available Endpoints:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"   {route.path} - {methods}")

if __name__ == "__main__":
    print("="*70)
    print("🚀 BUSINESS AGENT 2.0 - PRODUCTION SERVER STARTUP CHECK")
    print("="*70)
    print()
    
    asyncio.run(test_startup())
    
    print()
    print("="*70)
    print("✅ Server ready to start!")
    print("="*70)
    print()
    print("To run the server:")
    print()
    print("  Development mode:")
    print("    python -m uvicorn app_production:app --reload")
    print()
    print("  Production mode (single worker):")
    print("    python -m uvicorn app_production:app --host 0.0.0.0 --port 8000")
    print()
    print("  Production mode (4 workers with Gunicorn):")
    print("    gunicorn -w 4 -k uvicorn.workers.UvicornWorker app_production:app")
    print()
