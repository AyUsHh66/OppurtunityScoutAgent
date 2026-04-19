# QUICK TESTING REFERENCE

## 3 EASIEST WAYS TO TEST

### 1. INTERACTIVE WEB UI (Easiest - No Command Line!)
```
Open in browser: http://localhost:8000/docs
```
✅ See all endpoints
✅ Try each one with a button
✅ See real responses
✅ No curl commands needed

---

### 2. RUN ALL AUTOMATED TESTS
```powershell
python -m pytest tests/ -v
```
✅ 24 tests that verify everything
✅ Shows PASSED/FAILED for each
✅ Takes ~1.5 seconds
✅ Current status: **ALL 24 PASSING** ✅

Test Categories:
- 10 API tests (health, search, notifications, leads, integration)
- 14 security tests (auth, rate limiting, validation, headers)

---

### 3. QUICK CURL TESTS (Simple Command Line)

#### Check if server is alive:
```powershell
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

#### Search for jobs:
```powershell
curl -X POST http://localhost:8000/api/v1/jobs/search `
  -H "X-API-Key: test-key-1234567890123456" `
  -H "Content-Type: application/json" `
  -d '{"query":"Python","source":"startup","limit":3}'
```

#### Get configuration:
```powershell
curl http://localhost:8000/api/v1/config `
  -H "X-API-Key: test-key-1234567890123456"
```

---

## AVAILABLE ENDPOINTS (19 Total)

### Health Checks
- `GET /health` - Health status
- `GET /ready` - Readiness check
- `GET /live` - Liveness check

### Job Search
- `POST /api/v1/jobs/search` - Search opportunities
- `GET /api/v1/jobs/{job_id}` - Get job details

### Notifications  
- `POST /api/v1/notifications/send` - Send now
- `POST /api/v1/notifications/queue` - Queue for later
- `GET /api/v1/notifications/queue/status` - Check status
- `POST /api/v1/notifications/process-queue` - Process queue
- `POST /api/v1/notifications/test` - Test notification

### Leads
- `POST /api/v1/leads/qualify` - Qualify a lead

### Configuration
- `GET /api/v1/config` - Get settings
- `GET /api/v1/config/sources` - List sources

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc
- `GET /openapi.json` - OpenAPI spec
- `GET /` - Homepage
- `GET /metrics` - Metrics

---

## REQUIRED API KEY

All protected endpoints need the `X-API-Key` header:

```
X-API-Key: test-key-1234567890123456
```

Minimum length: 32 characters

---

## RATE LIMITS

Per endpoint limits (requests per minute):
- `/api/v1/jobs/search`: 30 req/min
- `/api/v1/notifications/send`: 10 req/min  
- `/api/v1/leads/qualify`: 20 req/min
- `/api/v1/config`: 100 req/min

---

## TEST DATA IN DATABASE

4 opportunity documents already loaded:
1. Senior Python Developer ($15K-$20K)
2. React Developer ($8K)
3. Full-Stack Developer ($100/hr)
4. DevOps Engineer ($90-120/hr)

---

## SAMPLE PAYLOADS

### Job Search
```json
{
  "query": "Python developer",
  "source": "startup",
  "limit": 5,
  "location": null
}
```

### Send Notification
```json
{
  "type": "job_opportunity",
  "title": "New Job Found",
  "message": "Senior Python role available",
  "priority": "high",
  "target_channels": ["discord"]
}
```

### Qualify Lead
```json
{
  "title": "Looking for Python Developer",
  "description": "5+ years experience required",
  "company": "Tech Corp",
  "source": "startup"
}
```

---

## CURRENT STATUS

✅ Server: RUNNING (http://localhost:8000)
✅ Tests: 24/24 PASSING
✅ Database: FRESH with 4 documents
✅ Security: API keys + rate limiting active
✅ API Docs: Available at /docs

---

## NEXT STEPS

1. **Browse API** → http://localhost:8000/docs
2. **Run Tests** → `python -m pytest tests/ -v`
3. **Test Endpoint** → `curl http://localhost:8000/health`
4. **Explore** → Try different endpoints in the UI

---

**Everything is working and ready to test! 🎯**
