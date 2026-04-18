# Production Deployment Guide - Business Agent 2.0

## Overview

This guide provides comprehensive instructions for deploying Business Agent 2.0 to production with proper scaling, monitoring, and reliability.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling](#scaling)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum (16GB for Mistral model)
- **Storage**: 50GB+ (for embeddings and logs)
- **Network**: Stable internet connection for external APIs

### Software Requirements

- Docker & Docker Compose 20.10+
- Kubernetes 1.24+ (for K8s deployment)
- Python 3.10+ (for local development)
- Redis 6+ (for queue backend)

---

## Environment Setup

### 1. Configuration Management

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

**Critical Settings for Production**:

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
OLLAMA_MODEL=mistral  # Use Mistral for better accuracy
QUEUE_BACKEND=redis   # Use Redis instead of memory
```

### 2. Validation

```bash
# Test configuration
python -c "from config import get_settings; s = get_settings(); print(s.to_dict())"

# Verify all required APIs are configured
python -m pytest tests/test_config.py
```

---

## Docker Deployment

### 1. Build Production Image

```dockerfile
# Use multi-stage build for smaller image
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Production Setup

```yaml
version: '3.8'

services:
  # Ollama LLM
  ollama:
    image: ollama/ollama:latest
    container_name: business-agent-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: business-agent-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT_API_KEY=${QDRANT_API_KEY:-}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for Queues
  redis:
    image: redis:7-alpine
    container_name: business-agent-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL for Notification History
  postgres:
    image: postgres:15-alpine
    container_name: business-agent-postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=business_agent
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=${DB_PASSWORD:-secure_password}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Main Application
  app:
    build: .
    container_name: business-agent-app
    ports:
      - "8000:8000"
    depends_on:
      ollama:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    environment:
      - ENVIRONMENT=production
      - OLLAMA_BASE_URL=http://ollama:11434
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://agent_user:${DB_PASSWORD:-secure_password}@postgres:5432/business_agent
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama_data:
  qdrant_data:
  redis_data:
  postgres_data:

networks:
  default:
    name: business-agent-network
```

### 3. Deployment

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec app python manage.py migrate

# Create admin user
docker-compose exec app python manage.py create_admin

# View logs
docker-compose logs -f app

# Health check
curl http://localhost:8000/health
```

---

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

**Namespace**:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: business-agent
```

**ConfigMap for Configuration**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: business-agent-config
  namespace: business-agent
data:
  ENVIRONMENT: production
  DEBUG: "false"
  LOG_LEVEL: WARNING
  OLLAMA_BASE_URL: http://ollama:11434
  QDRANT_URL: http://qdrant:6333
  REDIS_URL: redis://redis:6379/0
```

**StatefulSets for Services**:

```yaml
# Ollama StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ollama
  namespace: business-agent
spec:
  serviceName: ollama
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        volumeMounts:
        - name: ollama-storage
          mountPath: /root/.ollama
  volumeClaimTemplates:
  - metadata:
      name: ollama-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

### 2. Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: business-agent-app
  namespace: business-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: business-agent
  template:
    metadata:
      labels:
        app: business-agent
    spec:
      containers:
      - name: app
        image: business-agent:latest
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: business-agent-config
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/statefulsets.yaml
kubectl apply -f k8s/deployments.yaml

# Check deployment status
kubectl get pods -n business-agent
kubectl get services -n business-agent

# View logs
kubectl logs -n business-agent deployment/business-agent-app -f

# Scale deployment
kubectl scale deployment business-agent-app -n business-agent --replicas=5
```

---

## Monitoring & Logging

### 1. Structured Logging

The application uses structured JSON logging:

```python
from core_engine.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Event", extra={"trace_id": "xyz", "user_id": "123"})
```

### 2. Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Track notifications sent
notifications_sent = Counter(
    'notifications_sent_total',
    'Total notifications sent',
    ['channel', 'status']
)

# Track job processing time
processing_time = Histogram(
    'job_processing_seconds',
    'Time spent processing job posting'
)
```

### 3. Log Aggregation (ELK Stack)

```yaml
# Filebeat configuration
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/business-agent/*.log
  json.message_key: message
  json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "business-agent-%{+yyyy.mm.dd}"
```

### 4. Alert Rules

```yaml
# Prometheus alert rules
groups:
- name: business-agent
  rules:
  - alert: HighErrorRate
    expr: rate(app_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: QueueBacklog
    expr: queue_size > 1000
    for: 10m
    annotations:
      summary: "Notification queue backlog building up"

  - alert: APILatencyHigh
    expr: histogram_quantile(0.95, api_request_duration_seconds) > 5
    for: 10m
    annotations:
      summary: "API latency is high"
```

---

## Scaling

### 1. Horizontal Scaling

```bash
# Scale application instances
kubectl scale deployment business-agent-app --replicas=10

# Scale with auto-scaling
kubectl autoscale deployment business-agent-app --min=3 --max=10 --cpu-percent=80
```

### 2. Job Processing with Celery

```python
# tasks.py
from celery import Celery

app = Celery('business_agent')

@app.task
def process_job_posting(job_id):
    # Process job asynchronously
    pass

@app.task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    try:
        # Send notification
        pass
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

### 3. Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_notifications_created ON notifications(created_at);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_jobs_company ON jobs(company_id);
CREATE INDEX idx_jobs_created ON jobs(created_at);

-- Archive old records
DELETE FROM notifications WHERE created_at < NOW() - INTERVAL '90 days';
```

---

## Security

### 1. API Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT or API key
    if not is_valid_token(token):
        raise HTTPException(status_code=403)
    return token
```

### 2. Secrets Management

```bash
# Using Kubernetes secrets
kubectl create secret generic business-agent-secrets \
  --from-literal=discord_token=xxx \
  --from-literal=hunter_api_key=yyy \
  -n business-agent

# Reference in deployments
env:
- name: DISCORD_BOT_TOKEN
  valueFrom:
    secretKeyRef:
      name: business-agent-secrets
      key: discord_token
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/jobs")
@limiter.limit("100/minute")
async def search_jobs(query: str):
    pass
```

### 4. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Common Issues

**1. Ollama Connection Timeout**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Increase timeout in config
API_TIMEOUT=60
```

**2. Queue Backlog Building Up**

```bash
# Scale up notification processor
kubectl scale deployment notification-processor --replicas=5

# Check Redis memory
redis-cli INFO memory
```

**3. Database Connection Issues**

```bash
# Check connection pool
SELECT datname, usename, count(*) FROM pg_stat_activity GROUP BY datname, usename;

# Increase max connections if needed
max_connections = 500  # in postgresql.conf
```

**4. Memory Leaks**

```bash
# Profile memory usage
python -m memory_profiler main.py

# Check for unbounded buffers
# Ensure notification deduplicator is cleaning up old entries
```

---

## Performance Tuning

### 1. Database Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### 2. Vector Database Optimization

```bash
# Optimize Qdrant performance
# Set appropriate shard count
# Configure batch insertion for bulk operations
```

### 3. Cache Configuration

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_company_info(company_id: str):
    # Cached for 1 hour
    pass
```

---

## Backup & Recovery

```bash
# Backup Qdrant data
docker-compose exec qdrant qdrant-cli snapshot create

# Backup Postgres
docker-compose exec postgres pg_dump -U agent_user business_agent > backup.sql

# Restore from backup
cat backup.sql | docker-compose exec -T postgres psql -U agent_user business_agent
```

---

## Maintenance

```bash
# Regular health checks
*/5 * * * * curl -f http://localhost:8000/health || alert

# Log rotation
logrotate -f /etc/logrotate.d/business-agent

# Database maintenance
ANALYZE;
VACUUM;
REINDEX;
```

---

## Next Steps

1. **Set up monitoring** with Prometheus + Grafana
2. **Configure alerting** with PagerDuty or similar
3. **Implement CI/CD** with GitHub Actions
4. **Set up disaster recovery** plan
5. **Load test** before production deployment
6. **Create runbooks** for common operational tasks

For questions or issues, check [GitHub Issues](https://github.com/yourrepo/issues) or see TECHNICAL_DOCUMENTATION.md for more details.
