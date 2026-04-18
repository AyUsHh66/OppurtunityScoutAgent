# Production Deployment - Quick Start

## 30 Minutes to Production

### Step 1: Pre-Deployment (5 min)
```bash
# Verify all tests pass
pytest tests/ -v --cov=.

# Update dependencies (optional)
pip install -r requirements.lock

# Generate admin key
export FASTAPI_ADMIN_KEY=$(openssl rand -hex 32)
```

### Step 2: Configure Secrets (5 min)
```bash
# Copy and edit production environment
cp .env.production .env.prod.local

# Set all required keys:
export ENVIRONMENT=production
export OLLAMA_BASE_URL=http://ollama-prod:11434
export QDRANT_URL=http://qdrant-prod:6333
export HUNTER_API_KEY=<your-key>
export DISCORD_BOT_TOKEN=<your-token>
# ... (see .env.production for all variables)
```

### Step 3: Run with Docker Compose (5 min)
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f api
```

### Step 4: Verify Deployment (5 min)
```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"Business Agent 2.0",...}

# Readiness check
curl http://localhost:8000/ready
# Expected: {"ready":true,"environment":"production",...}

# API test
curl -X GET http://localhost:8000/api/v1/config \
  -H "X-API-Key: $FASTAPI_ADMIN_KEY"
```

### Step 5: Setup Monitoring (Optional, 5 min)
```bash
# View metrics
curl http://localhost:8000/metrics

# Setup Prometheus (see MONITORING_GUIDE.md)
# Setup Grafana (see MONITORING_GUIDE.md)
```

---

## Verification Checklist

- [ ] API responds to `/health`
- [ ] API responds to `/ready`
- [ ] Config endpoint accessible with API key
- [ ] Rate limiting works (test with multiple requests)
- [ ] Logs are being written
- [ ] No errors in Docker Compose logs
- [ ] Database connection successful
- [ ] All health checks pass

---

## If Something Goes Wrong

### API Returns 401 (Unauthorized)
```bash
# Missing or invalid API key
curl -H "X-API-Key: $FASTAPI_ADMIN_KEY" http://localhost:8000/api/v1/config
```

### API Returns 503 (Service Unavailable)
```bash
# Check if Qdrant is running
docker-compose -f docker-compose.prod.yml ps

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Connection Refused
```bash
# Check if API container is running
docker ps | grep business-agent

# Check logs
docker-compose -f docker-compose.prod.yml logs api
```

### High Memory Usage
```bash
# Reduce workers (edit docker-compose.prod.yml)
# Original: CMD ["uvicorn", "main:app", "--workers", "4"]
# Reduced: CMD ["uvicorn", "main:app", "--workers", "2"]
```

---

## Production Ready Features Included

✅ **Security**
- API key authentication
- Rate limiting (60 req/min per IP)
- CORS protection
- Input validation
- Request ID tracking

✅ **Monitoring**
- Health checks (/health, /ready, /live)
- Structured logging
- Request tracing
- Performance metrics
- Error tracking

✅ **Reliability**
- Graceful shutdown
- Retry logic
- Circuit breaker pattern
- Error recovery
- Connection pooling

✅ **Operations**
- Docker multi-stage build
- Docker Compose orchestration
- Environment config separation
- Secret management
- Backup strategies

---

## Next Steps

1. **Read Full Docs**: See DEPLOYMENT_GUIDE.md
2. **Setup Monitoring**: See MONITORING_GUIDE.md
3. **Configure Alerts**: Set up Prometheus alerting
4. **Test Failure Scenarios**: Run disaster recovery drills
5. **Plan Maintenance**: Schedule updates and backups

---

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review PRODUCTION_HARDENING.md
3. Run tests: `pytest tests/test_integration.py`
4. Check metrics: `curl http://localhost:8000/metrics`

---

**Version**: 2.0.0-production-ready
**Updated**: 2026-04-18
