# Quick Reference Guide - Business Agent 2.0

## Development Commands

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Update with your API keys

# Start development server
python main.py

# Access API docs
open http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_notifications.py -v

# Run with coverage
pytest --cov=. tests/

# Run in watch mode (requires pytest-watch)
ptw
```

### Code Quality
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Sort imports
isort .

# All of the above
black . && isort . && flake8 . && mypy .
```

---

## Docker Commands

### Development (Docker Compose)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

### Production (Docker Compose)
```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f app

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Docker Image
```bash
# Build production image
docker build -f Dockerfile.prod -t business-agent:latest .

# Run container
docker run -p 8000:8000 -e ENVIRONMENT=production business-agent:latest

# Push to registry
docker tag business-agent:latest myregistry/business-agent:latest
docker push myregistry/business-agent:latest
```

---

## Kubernetes Commands

### Deploy
```bash
# Create namespace
kubectl create namespace business-agent

# Apply all manifests
kubectl apply -f k8s/ -n business-agent

# Check deployment
kubectl get pods -n business-agent
kubectl get services -n business-agent

# View logs
kubectl logs deployment/business-agent-app -n business-agent -f

# Get deployment status
kubectl describe deployment business-agent-app -n business-agent
```

### Manage
```bash
# Scale deployment
kubectl scale deployment business-agent-app --replicas=5 -n business-agent

# Restart pods
kubectl rollout restart deployment/business-agent-app -n business-agent

# Get pod details
kubectl get pods -n business-agent -o wide

# Execute command in pod
kubectl exec -it pod/business-agent-app-xyz -n business-agent -- bash

# Port forward for testing
kubectl port-forward service/business-agent 8000:8000 -n business-agent
```

### Troubleshoot
```bash
# Get all events
kubectl get events -n business-agent

# Describe pod for issues
kubectl describe pod business-agent-app-xyz -n business-agent

# Check resource usage
kubectl top pods -n business-agent

# View logs from failed pod
kubectl logs pod/business-agent-app-xyz -n business-agent --previous
```

---

## API Testing

### Job Search
```bash
# Simple search
curl -X POST http://localhost:8000/api/v1/jobs/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer"}'

# Search with filters
curl -X POST http://localhost:8000/api/v1/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python developer",
    "job_type": "Remote",
    "location": "USA",
    "min_salary": 100000
  }'
```

### Notifications
```bash
# Send notification
curl -X POST http://localhost:8000/api/v1/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Job Opportunity",
    "message": "Senior Python Developer - Remote",
    "priority": "high",
    "channels": ["discord", "trello"]
  }'

# Queue notification
curl -X POST http://localhost:8000/api/v1/notifications/queue \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Job Alert",
    "message": "New posting found",
    "channels": ["discord"]
  }'

# Check queue status
curl http://localhost:8000/api/v1/notifications/queue/status

# Process queue
curl -X POST http://localhost:8000/api/v1/notifications/process-queue

# Test channels
curl -X POST http://localhost:8000/api/v1/notifications/test
```

### Configuration
```bash
# Get current config
curl http://localhost:8000/api/v1/config

# Get job sources
curl http://localhost:8000/api/v1/config/sources

# Health check
curl http://localhost:8000/health
```

### Batch Operations
```bash
# Search and send notifications
for query in "python developer" "javascript engineer" "devops specialist"; do
  echo "Searching: $query"
  curl -X POST http://localhost:8000/api/v1/jobs/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\"}" | jq '.jobs[0] | {title, company, url}'
done
```

---

## Configuration

### View Current Configuration
```bash
# Python
python -c "from config import get_settings; print(get_settings().to_dict())"

# Shell
echo "ENVIRONMENT=$ENVIRONMENT"
echo "OLLAMA_MODEL=$OLLAMA_MODEL"
```

### Update Configuration
```bash
# Edit .env
nano .env

# Reload in Python (requires restart)
# from config import reload_settings
# settings = reload_settings()
```

---

## Logging

### View Logs
```bash
# Application logs
tail -f logs/business_agent.log

# Real-time with filtering
tail -f logs/business_agent.log | grep ERROR

# Get last 100 lines
tail -n 100 logs/business_agent.log

# Search for pattern
grep "notification" logs/business_agent.log

# Count errors
grep -c "ERROR" logs/business_agent.log
```

### Change Log Level
```bash
# In .env
LOG_LEVEL=DEBUG

# Or in code
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

---

## Database Operations

### Qdrant (Vector Database)
```bash
# Connect to Qdrant
docker-compose exec qdrant bash

# List collections
qdrant-cli collection list

# Get collection info
qdrant-cli collection info opportunity_scout_collection

# Create snapshot
qdrant-cli snapshot create

# Restore from snapshot
qdrant-cli snapshot restore snapshot_id
```

### PostgreSQL (Application Database)
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U agent_user -d business_agent

# List tables
\dt

# Count records
SELECT count(*) FROM notifications;

# View recent notifications
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10;

# Backup database
docker-compose exec postgres pg_dump -U agent_user business_agent > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U agent_user business_agent
```

### Redis (Queue)
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check queue size
LLEN notification_queue

# View queue contents
LRANGE notification_queue 0 -1

# Clear queue
FLUSHDB

# Monitor in real-time
MONITOR
```

---

## Monitoring

### Prometheus
```bash
# Access Prometheus
open http://localhost:9090

# Query examples
# - up (all up/down)
# - rate(requests_total[5m]) (request rate)
# - histogram_quantile(0.95, request_duration) (95th percentile latency)
```

### Grafana
```bash
# Access Grafana
open http://localhost:3000

# Default login
username: admin
password: admin

# Create dashboard to query Prometheus metrics
```

### Metrics
```bash
# Get Prometheus metrics
curl http://localhost:8000/metrics

# Filter by job search
curl http://localhost:8000/metrics | grep job_search

# Get notification metrics
curl http://localhost:8000/metrics | grep notification
```

---

## Debugging

### Python Debugger
```bash
# Set breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Commands:
# n - next line
# s - step into
# c - continue
# p var - print variable
# h - help
```

### Code Inspection
```bash
# Start interactive Python
python

# Import and inspect
from config import get_settings
settings = get_settings()
print(dir(settings))

# Check configuration
from perception.job_search import create_default_search_engine
engine = create_default_search_engine()
print(engine.sources)
```

### API Debugging
```bash
# Enable verbose logging
LOG_LEVEL=DEBUG python main.py

# Test with httpie (easier than curl)
# Install: pip install httpie
https POST localhost:8000/api/v1/jobs/search query="python developer"

# Use Python requests
python -c "
import requests
resp = requests.get('http://localhost:8000/health')
print(resp.json())
"
```

---

## Performance Monitoring

### Request Profiling
```bash
# Using py-spy (install: pip install py-spy)
py-spy record -o profile.svg python main.py

# Using cProfile
python -m cProfile -s cumtime main.py
```

### Memory Profiling
```bash
# Using memory_profiler (install: pip install memory-profiler)
python -m memory_profiler main.py

# Or use tracker
python -c "
import tracemalloc
tracemalloc.start()
# ... run code ...
current, peak = tracemalloc.get_traced_memory()
print(f'Current: {current / 1024 / 1024}MB; Peak: {peak / 1024 / 1024}MB')
"
```

### Load Testing
```bash
# Using locust (install: pip install locust)
locust -f locustfile.py -u 100 -r 10 --run-time 1m

# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

---

## Common Tasks

### Add New Job Source
```python
# 1. Edit perception/job_search.py
# 2. Create new JobSource subclass
class MyJobSource(JobSource):
    def get_source_name(self) -> str:
        return "my_source"
    
    def search(self, query, filters=None):
        # Implement search logic
        pass

# 3. Register in JobSearchEngine
engine = JobSearchEngine()
engine.register_source(MyJobSource())
```

### Add New Notification Channel
```python
# 1. Edit tools/notifications.py
# 2. Create new NotificationChannel subclass
class MyChannel(NotificationChannel):
    def get_channel_name(self) -> str:
        return "my_channel"
    
    def send(self, notification):
        # Implement send logic
        pass

# 3. Register in NotificationManager
manager = NotificationManager()
manager.register_channel(MyChannel())
```

### Deploy to Production
```bash
# 1. Update .env for production
ENVIRONMENT=production
DEBUG=false

# 2. Build and push image
docker build -f Dockerfile.prod -t myregistry/business-agent:v1.0 .
docker push myregistry/business-agent:v1.0

# 3. Deploy with Kubernetes or Docker Compose
kubectl apply -f k8s/
# or
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
kubectl get pods -n business-agent
curl http://localhost:8000/health
```

---

## Useful Aliases

Add to `.bashrc` or `.zshrc`:

```bash
# Docker shortcuts
alias ba-up="docker-compose -f docker-compose.prod.yml up -d"
alias ba-down="docker-compose -f docker-compose.prod.yml down"
alias ba-logs="docker-compose -f docker-compose.prod.yml logs -f app"
alias ba-test="docker-compose -f docker-compose.prod.yml exec app pytest"

# Kubernetes shortcuts
alias ba-k-get="kubectl get pods -n business-agent"
alias ba-k-logs="kubectl logs deployment/business-agent-app -n business-agent -f"
alias ba-k-scale="kubectl scale deployment business-agent-app -n business-agent --replicas"

# API shortcuts
alias ba-health="curl http://localhost:8000/health | jq"
alias ba-config="curl http://localhost:8000/api/v1/config | jq"
alias ba-search="curl -X POST http://localhost:8000/api/v1/jobs/search -H 'Content-Type: application/json' -d"

# Development
alias ba-fmt="black . && isort ."
alias ba-lint="flake8 . && mypy ."
alias ba-test-local="pytest --cov=. tests/"
```

---

## Emergency Procedures

### Service Down
```bash
# 1. Check status
docker-compose -f docker-compose.prod.yml ps

# 2. View logs
docker-compose -f docker-compose.prod.yml logs app | tail -100

# 3. Restart problematic service
docker-compose -f docker-compose.prod.yml restart app

# 4. If still down, check configuration
cat .env | grep -E "(OLLAMA|QDRANT|REDIS|DISCORD)"

# 5. Full restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Database Corruption
```bash
# 1. Create backup of volumes
docker volume create backup-qdrant
docker run --rm -v qdrant_data:/data -v backup-qdrant:/backup alpine cp -r /data /backup

# 2. Restart database
docker-compose -f docker-compose.prod.yml restart qdrant

# 3. Restore if needed
docker volume rm qdrant_data
docker run --rm -v backup-qdrant:/backup -v qdrant_data:/data alpine cp -r /backup /data
```

### High Memory Usage
```bash
# 1. Check memory
docker stats

# 2. Restart services
docker-compose -f docker-compose.prod.yml restart app

# 3. Check for memory leaks
python -m memory_profiler main.py

# 4. Clear caches if applicable
docker-compose exec redis redis-cli FLUSHDB
```

---

## Useful Resources

- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Project Root**: Check `PRODUCTION_READY.md` and `PRODUCTION_DEPLOYMENT.md`

---

**Print this for easy reference!**
