# Business Agent 2.0 - Production Deployment Guide

## Pre-Deployment Checklist

### Security
- [ ] All API keys rotated
- [ ] Set strong `FASTAPI_ADMIN_KEY`
- [ ] Enable TLS/HTTPS
- [ ] Configure firewall rules
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Set up secrets management

### Infrastructure
- [ ] Production database configured
- [ ] Redis cache setup (optional)
- [ ] Backup strategy planned
- [ ] Logging centralized (ELK/Splunk)
- [ ] Monitoring configured (Prometheus/Grafana)
- [ ] Alerting setup

### Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Integration testing done
- [ ] Smoke tests pass in staging

### Documentation
- [ ] Runbooks created
- [ ] Escalation procedures documented
- [ ] Incident response plan ready
- [ ] Deployment procedure tested

---

## Deployment Methods

### 1. Docker (Recommended)

#### Build Image
```bash
docker build -t business-agent:2.0.0 -f Dockerfile.prod .
docker tag business-agent:2.0.0 your-registry/business-agent:2.0.0
docker push your-registry/business-agent:2.0.0
```

#### Run Container
```bash
docker run -d \
  --name business-agent \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e QDRANT_URL=http://qdrant:6333 \
  -e FASTAPI_ADMIN_KEY=$(openssl rand -hex 32) \
  -v /var/log/business_agent:/app/logs \
  your-registry/business-agent:2.0.0
```

#### Docker Compose (All Services)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

See `docker-compose.prod.yml` for full configuration.

### 2. Kubernetes

#### Deploy to K8s
```bash
# Create namespace
kubectl create namespace business-agent

# Create secrets
kubectl create secret generic business-agent-keys \
  --from-literal=fastapi-admin-key=$(openssl rand -hex 32) \
  --from-literal=hunter-api-key=$HUNTER_API_KEY \
  -n business-agent

# Apply manifests
kubectl apply -f k8s/ -n business-agent

# Check deployment
kubectl get deployments -n business-agent
kubectl get pods -n business-agent
```

### 3. Traditional VM/Server

#### Prerequisites
```bash
# Python 3.10+
python --version

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

#### Install & Run
```bash
# Install dependencies
pip install -r requirements.lock

# Configure environment
export ENVIRONMENT=production
cat > .env.production.local << EOF
OLLAMA_BASE_URL=http://ollama-server:11434
QDRANT_URL=http://qdrant-server:6333
FASTAPI_ADMIN_KEY=$(openssl rand -hex 32)
EOF

# Run with gunicorn (production ASGI server)
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --timeout 120 \
  app_production:app
```

---

## Post-Deployment

### Health Checks
```bash
# Basic health
curl https://your-domain/health

# Readiness
curl https://your-domain/ready

# Liveness
curl https://your-domain/live
```

### Verify Services
```bash
# Check logs
tail -f logs/business_agent.log

# Test API
curl -X GET https://your-domain/api/v1/config \
  -H "X-API-Key: your-admin-key"

# Run smoke tests
pytest tests/test_api.py -v
```

### Monitor Performance
```bash
# View metrics
curl https://your-domain/metrics

# Check resource usage
docker stats
# or
top -p $(pgrep -f app_production)
```

---

## Scaling & Performance

### Horizontal Scaling
```bash
# Scale with Docker Compose
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Performance Tuning
- Workers: `cpu_count * 2 + 1` (gunicorn)
- Batch size: Adjust based on memory
- Timeouts: Increase for slow networks
- Cache: Enable Redis for hot paths

---

## Troubleshooting

### API Not Responding
```bash
# Check if running
curl http://localhost:8000/health

# Check logs
docker logs business-agent  # Docker
tail -f logs/business_agent.log  # Direct
journalctl -u business-agent  # Systemd

# Restart
docker restart business-agent
# or
systemctl restart business-agent
```

### High Memory Usage
```bash
# Check top consumers
docker stats

# Reduce workers
# Edit: gunicorn -w 2 (instead of 4)

# Enable memory limits
docker run -m 2g business-agent:2.0.0
```

### Database Connection Issues
```bash
# Check Qdrant
curl http://qdrant:6333/health

# Verify network
docker network ls
docker network inspect business_agent_network

# Check logs
docker logs qdrant
```

###  Rate Limit Issues
```bash
# Check rate limit config
curl https://your-domain/api/v1/config

# Adjust limits in middleware/security.py
# Then redeploy
```

---

## Monitoring & Alerts

### Prometheus Metrics
Metrics available at `/metrics`

Key metrics:
- `http_request_duration_seconds` - Request latency
- `http_requests_total` - Total requests
- `http_request_size_bytes` - Request size
- `job_processing_time` - Job processing duration

### Grafana Dashboards
See MONITORING_GUIDE.md for dashboard setup.

### Alerts to Configure
```yaml
# Example alerts
- Request latency > 2s
- Error rate > 1%
- API key validation failures > 10/min
- Rate limit hits > 100/min
- Memory usage > 80%
- Disk usage > 90%
```

---

## Backup & Disaster Recovery

### Database Backup
```bash
# Backup Qdrant
docker exec qdrant \
  curl -X POST http://localhost:6333/collections/opportunity_scout_collection/snapshots

# Backup to file
docker cp qdrant:/data ./qdrant-backup
```

### Recovery Procedure
```bash
# Restore Qdrant
docker cp ./qdrant-backup qdrant:/data
docker restart qdrant

# Verify
curl http://qdrant:6333/health
```

### Disaster Recovery Plan
1. Keep database backups off-site
2. Test recovery procedures monthly
3. Document recovery steps
4. Have rollback plan ready

---

## Maintenance

### Regular Tasks
- [ ] Daily: Check logs for errors
- [ ] Daily: Verify health checks pass
- [ ] Weekly: Review metrics
- [ ] Weekly: Backup database
- [ ] Monthly: Test recovery procedure
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

### Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update
pip install --upgrade -r requirements.lock

# Test
pytest tests/

# Deploy
docker build -t business-agent:2.0.1 .
```

### Upgrade Application
```bash
# Pull new version
git pull origin main

# Run tests
pytest tests/

# Build
docker build -t business-agent:2.0.1 .

# Test in staging
docker run -e ENVIRONMENT=staging business-agent:2.0.1

# Deploy to production
docker service update --image business-agent:2.0.1 business-agent
```

---

## Support & Escalation

For production issues:

1. **Check Health** - Verify `/health` and `/ready` endpoints
2. **Review Logs** - Check `logs/business_agent.log` for errors
3. **Check Metrics** - Review `/metrics`  for anomalies
4. **Run Diagnostics** - `pytest tests/test_integration.py`
5. **Escalate** - Include request IDs and timestamps

---

## Contact & Resources

- **Documentation**: See PRODUCTION_HARDENING.md
- **API Docs**: https://your-domain/docs
- **Monitoring**: https://your-domain/metrics
- **Issues**: GitHub Issues
- **Support**: Send request ID to support@example.com

---

**Last Updated**: 2026-04-18
**Version**: 2.0.0
