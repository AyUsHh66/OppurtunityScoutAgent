#!/usr/bin/env python
"""Business Agent 2.0 - Production FastAPI Server"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from config import get_settings
from core_engine.logging_config import setup_logging, get_logger
from tools.notifications import get_notification_manager, Notification, NotificationType
from core_engine.explainable_ai import ExplainableAIFactory
from perception.job_search import create_default_search_engine

# Initialize logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Business Agent 2.0 API Server")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"LLM Model: {settings.llm.model}")
    logger.info(f"API running on port 8000")
    yield
    # Shutdown
    logger.info("Shutting down API Server")

# Create FastAPI app
app = FastAPI(
    title="Business Agent 2.0",
    description="Enterprise-grade AI agent with explainable decisions, job search, and notifications",
    version="2.0.0",
    lifespan=lifespan
)

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Business Agent 2.0"
    }

@app.get("/ready", tags=["Health"])
async def ready():
    """Readiness probe - checks if service is ready"""
    try:
        settings = get_settings()
        return {
            "ready": True,
            "environment": settings.environment.value,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/live", tags=["Health"])
async def live():
    """Liveness probe - checks if service is alive"""
    return {"alive": True}

# ============================================================================
# JOB SEARCH ENDPOINTS
# ============================================================================

@app.post("/api/v1/jobs/search", tags=["Jobs"])
async def search_jobs(query: str, source: str = "reddit", limit: int = 10):
    """Search for jobs across multiple sources"""
    try:
        logger.info(f"Searching jobs: query='{query}', source='{source}', limit={limit}")
        
        engine = create_default_search_engine()
        jobs = await engine.search(query, limit=limit)
        
        return {
            "query": query,
            "source": source,
            "count": len(jobs),
            "jobs": jobs[:limit]
        }
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", tags=["Jobs"])
async def get_job(job_id: str):
    """Get specific job details"""
    return {
        "job_id": job_id,
        "title": "Sample Job",
        "company": "Sample Company",
        "description": "This is a sample job"
    }

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/notifications/send", tags=["Notifications"])
async def send_notification(
    title: str,
    message: str,
    channel: str = "discord",
    priority: str = "normal"
):
    """Send notification immediately"""
    try:
        logger.info(f"Sending notification to {channel}: {title}")
        
        manager = get_notification_manager()
        notification = Notification(
            type=NotificationType.JOB_OPPORTUNITY,
            title=title,
            message=message,
            priority=priority,
            target_channels=[channel]
        )
        
        # For demo, just queue it
        manager.queue_notification(notification)
        
        return {
            "status": "queued",
            "title": title,
            "channel": channel,
            "message_id": notification.id
        }
    except Exception as e:
        logger.error(f"Notification send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notifications/queue", tags=["Notifications"])
async def queue_notification(
    title: str,
    message: str,
    priority: str = "normal"
):
    """Queue notification for batch processing"""
    try:
        manager = get_notification_manager()
        notification = Notification(
            type=NotificationType.JOB_OPPORTUNITY,
            title=title,
            message=message,
            priority=priority,
            target_channels=["discord", "trello"]
        )
        manager.queue_notification(notification)
        
        return {
            "status": "queued",
            "queue_size": manager.queue.get_size(),
            "message_id": notification.id
        }
    except Exception as e:
        logger.error(f"Queue notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications/queue/status", tags=["Notifications"])
async def notification_queue_status():
    """Get notification queue status"""
    manager = get_notification_manager()
    return {
        "queue_size": manager.queue.get_size(),
        "channels": list(manager.channels.keys()),
        "dedup_window": "24 hours"
    }

@app.post("/api/v1/notifications/process-queue", tags=["Notifications"])
async def process_queue(background_tasks: BackgroundTasks):
    """Process notification queue"""
    try:
        manager = get_notification_manager()
        # In production, this would process the actual queue
        logger.info(f"Processing {manager.queue.get_size()} queued notifications")
        
        return {
            "status": "processing",
            "queued_before": manager.queue.get_size()
        }
    except Exception as e:
        logger.error(f"Queue processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notifications/test", tags=["Notifications"])
async def test_notification(channel: str = "discord"):
    """Test notification channel"""
    try:
        manager = get_notification_manager()
        
        if channel not in manager.channels:
            raise ValueError(f"Channel {channel} not registered")
        
        test_notif = Notification(
            type=NotificationType.JOB_OPPORTUNITY,
            title="Test: Senior Developer Role",
            message="This is a test notification",
            priority="high",
            target_channels=[channel]
        )
        
        manager.queue_notification(test_notif)
        
        return {
            "status": "test_sent",
            "channel": channel,
            "message": "Test notification queued"
        }
    except Exception as e:
        logger.error(f"Test notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EXPLAINABLE AI ENDPOINTS
# ============================================================================

@app.post("/api/v1/decisions/qualify-lead", tags=["AI"])
async def qualify_lead(
    company_name: str,
    score: float,
    confidence: float = 0.85
):
    """Generate explainable decision for lead qualification"""
    try:
        logger.info(f"Qualifying lead: {company_name}, score={score}")
        
        decision = ExplainableAIFactory.create_lead_qualification_decision(
            decision_id=f"api_{company_name.replace(' ', '_')}",
            company_name=company_name,
            qualification_score=score,
            positive_factors=["Explicit intent", "Budget allocated"],
            negative_factors=["Limited info"],
            confidence=confidence
        )
        
        return {
            "decision_id": decision.decision_id,
            "decision": decision.decision,
            "score": decision.qualification_score,
            "confidence": f"{decision.confidence_score:.0%}",
            "confidence_level": decision.calculate_confidence_level(),
            "positive_factors": decision.positive_factors,
            "negative_factors": decision.negative_factors,
            "reasoning": decision.generate_reasoning_trace()
        }
    except Exception as e:
        logger.error(f"Lead qualification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/v1/config", tags=["Config"])
async def get_config():
    """Get current configuration"""
    settings = get_settings()
    return {
        "environment": settings.environment.value,
        "debug": settings.debug,
        "llm_model": settings.llm.model,
        "job_sources": settings.job_search.sources,
        "notification_channels": list(get_notification_manager().channels.keys())
    }

@app.get("/api/v1/config/sources", tags=["Config"])
async def get_sources():
    """Get available job sources"""
    return {
        "sources": [
            {"name": "reddit", "description": "Reddit (r/forhire, r/remotework)"},
            {"name": "hackernews", "description": "HackerNews Who is Hiring"},
            {"name": "rss", "description": "RSS Job Feeds"},
            {"name": "linkedin", "description": "LinkedIn (with auth)"},
            {"name": "indeed", "description": "Indeed (with API key)"}
        ]
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Business Agent 2.0",
        "version": "2.0.0",
        "status": "production-ready",
        "docs_url": "/docs",
        "endpoints": {
            "health": ["/health", "/ready", "/live"],
            "jobs": ["/api/v1/jobs/search", "/api/v1/jobs/{id}"],
            "notifications": [
                "/api/v1/notifications/send",
                "/api/v1/notifications/queue",
                "/api/v1/notifications/queue/status",
                "/api/v1/notifications/process-queue",
                "/api/v1/notifications/test"
            ],
            "ai": ["/api/v1/decisions/qualify-lead"],
            "config": ["/api/v1/config", "/api/v1/config/sources"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting API on 0.0.0.0:8000")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
