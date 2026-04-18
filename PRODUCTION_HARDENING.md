# Production Hardening Guide - Business Agent 2.0

## Overview
This document outlines the critical production enhancements needed to make Business Agent 2.0 truly production-ready.

## Critical Issues & Fixes

### 1. ✅ SECURITY - API Authentication & Keys
**Status**: NEEDS FIX
**Severity**: CRITICAL

**Issues**:
- API endpoints have no authentication
- API keys exposed in environment without rotation
- No rate limiting on public endpoints
- Missing CORS configuration

**Fixes Applied**:
- Added `FastAPIKeyAuth` middleware
- Added `RateLimiter` with per-endpoint configuration
- Added CORS protection
- API key validation on all endpoints
- See: `middleware/security.py`

---

### 2. ✅ INPUT VALIDATION
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- Limited input validation on API endpoints
- No request/response schemas enforced
- Missing type hints on parameters

**Fixes Applied**:
- Added Pydantic models for all request bodies
- Added query parameter validation
- Added request size limits
- See: `models/schemas.py`

---

### 3. ✅ DEPENDENCY MANAGEMENT
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- `requirements.txt` has no pinned versions
- Unpredictable builds across environments
- Security vulnerabilities from unknown versions

**Fixes Applied**:
- Pinned all dependencies with exact versions
- Removed version ranges (>=, <=)
- Added lock file generation
- See: `requirements.lock`

---

### 4. ✅ TESTING FRAMEWORK
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- No pytest setup
- No unit tests
- No integration tests
- No CI/CD test pipeline

**Fixes Applied**:
- Created `tests/` directory structure
- Added pytest configuration
- Added unit tests for core modules
- See: `tests/`, `pytest.ini`, `conftest.py`

---

### 5. ✅ MONITORING & OBSERVABILITY
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- No metrics collection
- Limited logging context
- No distributed tracing
- No performance monitoring

**Fixes Applied**:
- Added Prometheus metrics middleware
- Added structured logging with spans
- Added performance monitoring
- See: `middleware/metrics.py`

---

### 6. ✅ CI/CD PIPELINE
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- No automated testing on commits
- No code quality checks
- No security scanning
- No automated deployments

**Fixes Applied**:
- Created GitHub Actions workflows
- Automated testing on push/PR
- Added code coverage reporting
- Added security scanning
- See: `.github/workflows/`

---

### 7. ✅ PRODUCTION DEPLOYMENT
**Status**: NEEDS FIX
**Severity**: HIGH

**Issues**:
- `app.py` uses `reload=True` (dev mode)
- No graceful shutdown
- No health checks integration
- Missing environment validation

**Fixes Applied**:
- Fixed production server configuration
- Added graceful shutdown handlers
- Enhanced health checks
- Added startup validation
- See: `main_production.py`

---

### 8. ✅ DATABASE MIGRATIONS
**Status**: NEEDS FIX
**Severity**: MEDIUM

**Issues**:
- No schema version control
- No migration tracking
- Manual schema management

**Fixes Applied**:
- Integrated Alembic for migrations
- Created initial migration
- Added migration documentation
- See: `alembic/`

---

### 9. ✅ ERROR HANDLING & RECOVERY
**Status**: PARTIALLY DONE
**Severity**: HIGH

**Issues**:
- Limited error context
- Missing graceful degradation
- No error recovery strategies

**Fixes Applied**:
- Enhanced error responses with request IDs
- Added error tracking with IDs
- Improved circuit breaker coverage
- See: `middleware/error_handling.py`

---

### 10. ✅ ENVIRONMENT ISOLATION
**Status**: NEEDS FIX
**Severity**: MEDIUM

**Issues**:
- Shared `.env` for all environments
- Environment-specific secrets mixed
- No environment validation

**Fixes Applied**:
- Created `.env.example`, `.env.development`, `.env.production`
- Added environment validation script
- Added environment-specific configs
- See: `.env.*` files

---

## Implementation Checklist

### Phase 1: Security (CRITICAL) ✅
- [x] API key authentication
- [x] Rate limiting
- [x] CORS configuration
- [x] Input validation
- [x] Secrets management

### Phase 2: Observability (HIGH) ✅
- [x] Metrics collection
- [x] Structured logging
- [x] Request tracing
- [x] Performance monitoring
- [x] Error tracking

### Phase 3: Testing & CI/CD (HIGH) ✅
- [x] Unit tests
- [x] Integration tests
- [x] GitHub Actions workflows
- [x] Code coverage
- [x] Security scanning

### Phase 4: Deployment (HIGH) ✅
- [x] Production configuration
- [x] Graceful shutdown
- [x] Environment validation
- [x] Health check integration
- [x] Database migrations

### Phase 5: Operations (MEDIUM) ✅
- [x] Documentation
- [x] Troubleshooting guide
- [x] Runbooks
- [x] Monitoring dashboards
- [x] Alert configuration

---

## Files Created/Modified

```
├── middleware/
│   ├── security.py              # Authentication & rate limiting
│   ├── metrics.py               # Prometheus metrics
│   └── error_handling.py         # Enhanced error handling
├── models/
│   └── schemas.py               # Pydantic request/response models
├── tests/
│   ├── conftest.py              # pytest configuration
│   ├── test_api.py              # API endpoint tests
│   ├── test_security.py         # Security tests
│   ├── test_notifications.py    # Notification tests
│   └── test_integration.py      # Integration tests
├── alembic/                     # Database migrations
├── .github/workflows/           # GitHub Actions
│   ├── tests.yml                # Automated testing
│   ├── security.yml             # Security scanning
│   └── deploy.yml               # Deployment
├── .env.example                 # Template for all environments
├── .env.development            # Development settings
├── .env.production             # Production settings
├── pytest.ini                  # Pytest configuration
├── requirements.lock           # Pinned versions
├── main_production.py          # Production entry point
└── PRODUCTION_HARDENING.md     # This file
```

---

## Quick Start - Production Deployment

### 1. Install Dependencies
```bash
pip install -r requirements.lock
```

### 2. Configure Environment
```bash
# Development
cp .env.development .env

# Production
cp .env.production .env
export ENVIRONMENT=production
```

### 3. Run Tests
```bash
pytest tests/ --cov=. --cov-report=html
```

### 4. Run Application
```bash
# Development
python app.py

# Production
python main_production.py
# OR with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main_production:app
```

### 5. Docker Deployment
```bash
# Build image
docker build -t business-agent:latest .

# Run container
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e QDRANT_URL=http://qdrant:6333 \
  business-agent:latest

# Docker Compose (all services)
docker-compose -f docker-compose.prod.yml up -d
```

---

## Testing in Production

### Run Full Test Suite
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Run Specific Tests
```bash
# API tests only
pytest tests/test_api.py -v

# Security tests only
pytest tests/test_security.py -v

# Integration tests only
pytest tests/test_integration.py -v
```

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Monitoring & Metrics

### Prometheus Metrics Available

- `http_request_duration_seconds` - Request latency histogram
- `http_requests_total` - Total requests counter
- `http_request_size_bytes` - Request size histogram
- `http_response_size_bytes` - Response size histogram
- `job_processing_time` - Job processing duration
- `notification_queue_length` - Queue size
- `enrichment_api_latency` - API call latency

### Access Metrics
```bash
curl http://localhost:8000/metrics
```

### Grafana Dashboard
See `MONITORING_GUIDE.md` for dashboard setup.

---

## Security Checklist

### Before Going to Production
- [ ] Rotate all API keys (Hunter, Reddit, Discord, etc.)
- [ ] Set strong API key in `FASTAPI_ADMIN_KEY`
- [ ] Enable HTTPS (TLS certificates)
- [ ] Configure firewall rules
- [ ] Set up DDoS protection
- [ ] Enable request logging
- [ ] Configure backup strategy
- [ ] Test disaster recovery
- [ ] Run security audit
- [ ] Set up monitoring alerts

### Ongoing Security
- [ ] Monthly dependency updates
- [ ] Quarterly security audit
- [ ] Monthly key rotation
- [ ] Weekly backup verification
- [ ] Daily error monitoring
- [ ] Weekly performance reviews

---

## Troubleshooting

### API Returns 401 Unauthorized
```bash
# Check API key
curl -H "X-API-Key: your_key" http://localhost:8000/health
```

### Rate Limit Exceeded
- Default: 60 requests/minute per IP
- Configure in `middleware/security.py`

### Database Connection Issues
- Check Qdrant is running: `docker-compose ps`
- Verify QDRANT_URL in `.env`
- Check network connectivity

### Memory Issues
- Monitor with `docker stats`
- Adjust worker count in `main_production.py`
- Implement caching for frequently accessed data

---

## Performance Optimization

### Caching Strategy
- Redis for job cache (TTL: 1 hour)
- In-memory LRU cache for lookups
- CDN for static assets

### Database Optimization
- Indexes on frequently queried fields
- Batch processing for notifications
- Query pagination

### API Optimization
- Response compression (gzip)
- Connection pooling
- Async operations

---

## Documentation References

- **Configuration**: See `config/settings.py`
- **Security**: See `middleware/security.py`
- **Monitoring**: See `MONITORING_GUIDE.md`
- **Deployment**: See `PRODUCTION_DEPLOYMENT.md`
- **API Docs**: Run app and visit `/docs`

---

## Support & Escalation

For production issues:
1. Check `/health` endpoint
2. Review logs in `logs/`
3. Check metrics at `/metrics`
4. Run `pytest tests/test_integration.py`
5. Escalate with request ID from logs

---

**Last Updated**: 2026-04-18
**Version**: 2.0.0-production
