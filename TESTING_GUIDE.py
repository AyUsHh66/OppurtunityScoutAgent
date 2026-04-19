#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPLETE TESTING GUIDE - Business Agent 2.0
Shows all ways to test your project
"""

print("\n" + "="*80)
print("TESTING GUIDE - Business Agent 2.0")
print("="*80 + "\n")

print("METHOD 1: AUTOMATED TEST SUITE (24 Tests)")
print("-" * 80)
print("""
Run all tests with pytest:

    python -m pytest tests/ -v

Expected output:
    tests/test_api.py::TestHealthEndpoints::test_health_endpoint_success PASSED
    tests/test_api.py::TestHealthEndpoints::test_health_response_structure PASSED
    tests/test_api.py::TestJobSearchEndpoints::test_job_search_request_validation PASSED
    tests/test_api.py::TestJobSearchEndpoints::test_job_search_invalid_limit PASSED
    tests/test_api.py::TestJobSearchEndpoints::test_job_search_invalid_source PASSED
    tests/test_api.py::TestNotificationEndpoints::test_notification_request_validation PASSED
    tests/test_api.py::TestNotificationEndpoints::test_notification_invalid_priority PASSED
    tests/test_api.py::TestLeadQualificationEndpoints::test_lead_qualification_request PASSED
    tests/test_api.py::TestLeadQualificationEndpoints::test_lead_qualification_missing_required PASSED
    tests/test_api.py::TestAPIIntegration::test_full_workflow PASSED
    tests/test_security.py::TestAPIKeyValidation::test_api_key_validator_valid_key PASSED
    tests/test_security.py::TestAPIKeyValidation::test_api_key_validator_invalid_short_key PASSED
    tests/test_security.py::TestAPIKeyValidation::test_api_key_validator_admin_key PASSED
    tests/test_security.py::TestAPIKeyValidation::test_api_key_validator_empty_key PASSED
    tests/test_security.py::TestRateLimiting::test_rate_limiter_allows_under_limit PASSED
    tests/test_security.py::TestRateLimiting::test_rate_limiter_blocks_over_limit PASSED
    tests/test_security.py::TestRateLimiting::test_rate_limiter_different_clients PASSED
    tests/test_security.py::TestInputValidation::test_job_search_input_validation PASSED
    tests/test_security.py::TestInputValidation::test_notification_input_validation PASSED
    tests/test_security.py::TestInputValidation::test_notification_channel_validation PASSED
    tests/test_security.py::TestSecurityHeaders::test_request_id_generation PASSED
    tests/test_security.py::TestSecurityHeaders::test_request_id_uniqueness PASSED
    tests/test_security.py::TestEnvironmentSecurity::test_settings_validation PASSED
    tests/test_security.py::TestEnvironmentSecurity::test_sensitive_settings_not_logged PASSED

    ========================= 24 passed in 1.18s =========================

What's tested:
    - 10 API endpoint tests (health, search, notifications, leads, integration)
    - 14 security tests (auth, rate limiting, validation, headers, environment)
""")

print()

print("METHOD 2: WEB UI - API DOCUMENTATION")
print("-" * 80)
print("""
EASIEST METHOD - Use the built-in Swagger UI:

1. Make sure server is running:
   python -m uvicorn app_production:app --reload

2. Open in browser:
   http://localhost:8000/docs

3. You'll see ALL endpoints with:
   - Descriptions
   - Required parameters
   - Test buttons (Try it out!)
   - Response examples

Benefits:
   - Visual, no command line needed
   - Test any endpoint directly
   - See real-time responses
   - Auto-generates curl commands
""")

print()

print("METHOD 3: MANUAL CURL TESTS (PowerShell)")
print("-" * 80)
print("""
A. Health Check:
   curl http://localhost:8000/health

B. Search for Python Developer:
   curl -X POST http://localhost:8000/api/v1/jobs/search `
     -H "X-API-Key: test-key-1234567890123456" `
     -H "Content-Type: application/json" `
     -d '{"query":"Python developer","source":"startup","limit":5}'

C. Get System Configuration:
   curl http://localhost:8000/api/v1/config `
     -H "X-API-Key: test-key-1234567890123456"

D. Send Notification:
   curl -X POST http://localhost:8000/api/v1/notifications/send `
     -H "X-API-Key: test-key-1234567890123456" `
     -H "Content-Type: application/json" `
     -d '{"type":"job_opportunity","title":"New Job","message":"Found matching role","priority":"high"}'

E. Qualify a Lead:
   curl -X POST http://localhost:8000/api/v1/leads/qualify `
     -H "X-API-Key: test-key-1234567890123456" `
     -H "Content-Type: application/json" `
     -d '{"title":"Senior Python Developer","description":"5+ years experience required","company":"Test Corp"}'
""")

print()

print("METHOD 4: QUICK POSTMAN/INSOMNIA TESTS")
print("-" * 80)
print("""
If using Postman or Insomnia:

1. Create new request
2. Set method: POST
3. Set URL: http://localhost:8000/api/v1/jobs/search
4. Headers tab, add:
   - Key: X-API-Key
   - Value: test-key-1234567890123456
5. Body tab, select JSON, paste:
   {
     "query": "Python developer",
     "source": "startup",
     "limit": 5
   }
6. Click Send
7. See response!
""")

print()

print("METHOD 5: PYTHON TEST SCRIPT")
print("-" * 80)
print("""
Create file: test_manual.py

    import requests
    import json

    BASE_URL = "http://localhost:8000"
    API_KEY = "test-key-1234567890123456"

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # Test 1: Health check
    response = requests.get(f"{BASE_URL}/health")
    print("Health:", response.json())

    # Test 2: Search jobs
    payload = {
        "query": "Python developer",
        "source": "startup",
        "limit": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/jobs/search",
        json=payload,
        headers=headers
    )
    print("Search:", response.json())

    # Test 3: Get config
    response = requests.get(
        f"{BASE_URL}/api/v1/config",
        headers=headers
    )
    print("Config:", response.json())

Run it:
    python test_manual.py
""")

print()

print("WHAT TO TEST")
print("-" * 80)
print("""
1. Health Endpoints:
   [x] GET /health - Should return {"status": "healthy"}
   [x] GET /ready - Should show readiness status
   [x] GET /live - Should show liveness status

2. Job Search:
   [x] POST /api/v1/jobs/search - Search with valid queries
   [x] Test with different sources (startup, reddit, rss, etc.)
   [x] Test limit parameter (1-100)
   [x] Test invalid inputs (limit > 100)

3. Notifications:
   [x] POST /api/v1/notifications/send - Send notification
   [x] POST /api/v1/notifications/queue - Queue for later
   [x] GET /api/v1/notifications/queue/status - Check queue
   [x] POST /api/v1/notifications/process-queue - Process queue

4. Lead Qualification:
   [x] POST /api/v1/leads/qualify - Qualify a lead
   [x] Test with various inputs

5. Configuration:
   [x] GET /api/v1/config - Get current settings
   [x] GET /api/v1/config/sources - List available sources

6. Security:
   [x] Test with valid API key
   [x] Test with invalid API key (should 401)
   [x] Test with missing API key (should 401)
   [x] Test rate limiting (make 6 requests quickly to /api/v1/jobs/search)

7. Documentation:
   [x] GET /docs - Swagger UI
   [x] GET /redoc - ReDoc UI
""")

print()

print("EXPECTED RESPONSES")
print("-" * 80)
print("""
Health Check:
    Status: 200
    Response: {"status":"healthy"}

Job Search (valid):
    Status: 200
    Response: {
        "query": "Python developer",
        "source": "startup",
        "results": [...],
        "count": 4,
        "timestamp": "2026-04-19T..."
    }

Job Search (invalid source):
    Status: 422
    Response: Validation error

Missing API Key:
    Status: 401
    Response: {"detail":"Missing API key"}

Rate Limit Exceeded:
    Status: 429
    Response: {"detail":"Rate limit exceeded"}

Configuration:
    Status: 200
    Response: {
        "environment": "development",
        "debug": false,
        "llm_model": "phi",
        "job_sources": ["startup", "reddit", "rss"],
        "notification_channels": ["discord", "email"],
        "version": "2.0"
    }
""")

print()

print("TESTING WORKFLOW")
print("-" * 80)
print("""
Step 1: Start the server
    python -m uvicorn app_production:app --reload

Step 2: Run automated tests
    python -m pytest tests/ -v

Step 3: Manual testing via UI
    Open: http://localhost:8000/docs
    Try each endpoint in the UI

Step 4: Test edge cases
    - Invalid API key
    - Missing required fields
    - Out-of-range values
    - Rate limit (5 req/min for search endpoint)

Step 5: Check logs
    Look in logs/ folder for detailed execution traces

Step 6: Verify database
    Check if data is being stored in qdrant_storage/
""")

print()

print("TROUBLESHOOTING")
print("-" * 80)
print("""
Q: Getting 500 error on requests
A: Check logs for details, restart server

Q: API key not working
A: API key must be at least 32 characters
   Use: X-API-Key header
   Example: test-key-1234567890123456 (32 chars)

Q: Rate limit error
A: Endpoint has limit of 5-30 req/min
   Wait a minute and try again

Q: Tests failing
A: 1. Stop server if it's running
   2. Run: python full_reset.py
   3. Run: python -m pytest tests/ -v

Q: Database errors
A: Run: python full_reset.py
   This resets database with fresh data
""")

print()

print("="*80)
print("QUICK START")
print("="*80)
print()
print("Right now, do this:")
print()
print("1. Open browser: http://localhost:8000/docs")
print("   (This is the interactive API documentation)")
print()
print("2. Or run tests: python -m pytest tests/ -v")
print("   (This runs all 24 automated tests)")
print()
print("3. Or use curl: curl http://localhost:8000/health")
print("   (This checks if server is responding)")
print()
print("="*80)
print()
