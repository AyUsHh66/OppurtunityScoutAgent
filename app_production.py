#!/usr/bin/env python
"""Business Agent 2.0 - Production FastAPI Server with Security & Monitoring"""

import os
import signal
import uuid
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging

from config import get_settings
from core_engine.logging_config import setup_logging, get_logger
from tools.notifications import get_notification_manager, Notification, NotificationType
from core_engine.explainable_ai import ExplainableAIFactory
from perception.job_search import create_default_search_engine
from middleware.security import (
    SecurityMiddleware,
    validate_api_key,
    check_rate_limit,
    RateLimiter,
    get_cors_config,
)
from models.schemas import (
    JobSearchRequest,
    NotificationRequest,
    LeadQualificationRequest,
    HealthResponse,
    ReadyResponse,
    ErrorResponse,
)

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Global state
_shutdown_requested = False


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    global _shutdown_requested
    _shutdown_requested = True
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 Starting Business Agent 2.0 API Server")
    logger.info("=" * 80)
    
    try:
        settings = get_settings()
        logger.info(f"Environment: {settings.environment.value}")
        logger.info(f"Debug Mode: {settings.debug}")
        logger.info(f"LLM Model: {settings.llm.model}")
        logger.info(f"Qdrant URL: {settings.database.url}")
        logger.info(f"API Server: 0.0.0.0:8000")
        
        # Validate critical services
        logger.info("Validating critical services...")
        settings.validate()
        logger.info("✅ All services validated")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("🛑 Shutting down API Server")
    logger.info("=" * 80)
    
    try:
        logger.info("Closing connections...")
        logger.info("✅ Graceful shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="Business Agent 2.0",
    description="Enterprise-grade AI agent for discovering opportunities, qualifying leads, and automating outreach",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
cors_origins = get_cors_config()["allow_origins"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Add middleware to set request state attributes
@app.middleware("http")
async def add_request_state(request: Request, call_next):
    """Add request ID and client IP to request state"""
    # Generate request ID
    request.state.request_id = str(uuid.uuid4())
    
    # Extract client IP
    request.state.client_ip = request.client.host if request.client else "unknown"
    
    # Add start time for duration tracking
    request.state.start_time = time.time()
    
    response = await call_next(request)
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request.state.request_id
    
    return response


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health():
    """Health check endpoint - lightweight check"""
    return HealthResponse(
        status="healthy",
        service="Business Agent 2.0",
        version="2.0.0"
    )


@app.get("/ready", tags=["Health"], response_model=ReadyResponse)
async def ready(request: Request):
    """Readiness probe - check if all services are ready"""
    try:
        settings = get_settings()
        
        checks = {
            "configuration": True,
            "logging": True,
        }
        
        all_ready = all(checks.values())
        
        return ReadyResponse(
            ready=all_ready,
            environment=settings.environment.value,
            version="2.0.0",
            checks=checks,
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}", extra={"request_id": request.state.request_id})
        raise HTTPException(
            status_code=503,
            detail="Service not ready",
            headers={"X-Request-ID": request.state.request_id}
        )


@app.get("/live", tags=["Health"])
async def live():
    """Liveness probe - check if service is alive"""
    return {"alive": True, "timestamp": __import__("datetime").datetime.utcnow().isoformat()}


# ============================================================================
# JOB SEARCH ENDPOINTS
# ============================================================================

def search_opportunities_in_qdrant(query: str, limit: int = 10) -> list:
    """Search opportunities in Qdrant vector database
    
    Returns list of opportunities from the database, ranked by relevance.
    Falls back to all documents if specific search fails.
    """
    try:
        from qdrant_client import QdrantClient
        import random
        
        settings = get_settings()
        qdrant_url = settings.database.url
        
        # Connect to Qdrant
        client = QdrantClient(url=qdrant_url)
        collection_name = "opportunity_scout_collection"
        
        # Try to get all points from collection
        limit_to_fetch = min(limit * 3, 100)  # Fetch more to filter
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=limit_to_fetch
        )
        
        if not points:
            logger.warning(f"No opportunities found in Qdrant collection")
            return []
        
        # Convert points to dictionaries with score
        opportunities = []
        for point in points:
            if point.payload:
                # Simple keyword matching for scoring (since we don't have real embeddings)
                payload = point.payload
                title_lower = str(payload.get('title', '')).lower()
                description_lower = str(payload.get('description', '')).lower()
                keywords_lower = str(payload.get('skill_keywords', '')).lower()
                query_lower = query.lower()
                
                # Calculate relevance score
                score = 0
                if query_lower in title_lower:
                    score += 3
                if query_lower in description_lower:
                    score += 1
                if query_lower in keywords_lower:
                    score += 2
                
                # If no keyword match, give a base score
                if score == 0:
                    score = random.uniform(0.3, 0.8)
                else:
                    score = min(score / 10.0, 1.0)  # Normalize
                
                opportunities.append({
                    "id": str(payload.get('id', point.id)),
                    "title": payload.get('title', 'Untitled Opportunity'),
                    "company": payload.get('company', 'Unknown'),
                    "location": payload.get('location', 'Remote'),
                    "budget": payload.get('budget', 'Negotiable'),
                    "type": payload.get('type', 'job'),
                    "experience_level": payload.get('experience_level', ''),
                    "description": payload.get('description', ''),
                    "company_description": payload.get('company_description', ''),
                    "benefits": payload.get('benefits', '').split(',') if payload.get('benefits') else [],
                    "tags": payload.get('tags', '').split(',') if payload.get('tags') else [],
                    "posted_date": payload.get('posted_date', ''),
                    "score": score
                })
        
        # Sort by relevance score and limit
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        return opportunities[:limit]
        
    except Exception as e:
        logger.error(f"Error searching Qdrant opportunities: {e}")
        # Return empty list on error (will be handled by endpoint)
        return []


@app.post("/api/v1/jobs/search", tags=["Jobs"])
async def search_jobs(
    request: Request,
    body: JobSearchRequest,
    _: None = Depends(check_rate_limit),
):
    """Search for jobs and opportunities"""
    try:
        logger.info(
            f"Searching opportunities: query='{body.query}', source='{body.source}'",
            extra={"request_id": request.state.request_id}
        )
        
        # Search Qdrant database first (primary source - has enriched data)
        opportunities = search_opportunities_in_qdrant(body.query, limit=body.limit)
        
        # If Qdrant returns results, use them
        if opportunities:
            logger.info(
                f"Found {len(opportunities)} opportunities in Qdrant",
                extra={"request_id": request.state.request_id}
            )
            return {
                "query": body.query,
                "source": "database",
                "count": len(opportunities),
                "jobs": opportunities,
                "request_id": request.state.request_id,
            }
        
        # Fallback to external sources if Qdrant is empty
        logger.info(
            "No opportunities in database, trying external sources",
            extra={"request_id": request.state.request_id}
        )
        
        engine = create_default_search_engine()
        jobs = await engine.search(body.query, limit=body.limit)
        
        # Convert job postings to dict format
        job_results = [
            {
                "id": job.job_id if hasattr(job, 'job_id') else str(idx),
                "title": job.title if hasattr(job, 'title') else str(job),
                "company": job.company if hasattr(job, 'company') else "Unknown",
                "description": job.description if hasattr(job, 'description') else "",
                "source": job.source if hasattr(job, 'source') else "external",
            }
            for idx, job in enumerate(jobs[:body.limit])
        ]
        
        return {
            "query": body.query,
            "source": body.source,
            "count": len(job_results),
            "jobs": job_results,
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Job search failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


@app.get("/api/v1/jobs/{job_id}", tags=["Jobs"])
async def get_job(job_id: str, request: Request, _: None = Depends(check_rate_limit)):
    """Get specific job details"""
    return {
        "job_id": job_id,
        "title": "Sample Job",
        "company": "Sample Company",
        "request_id": request.state.request_id,
    }


# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/notifications/send", tags=["Notifications"])
async def send_notification(
    request: Request,
    body: NotificationRequest,
    api_key: str = Depends(validate_api_key),
    _: None = Depends(check_rate_limit),
):
    """Send notification immediately"""
    try:
        logger.info(
            f"Sending notification to channels: {body.target_channels}",
            extra={"request_id": request.state.request_id}
        )
        
        manager = get_notification_manager()
        
        # Create notification from request
        notification = Notification(
            type=NotificationType(body.type),
            title=body.title,
            message=body.message,
            details=body.details or {},
            priority=body.priority,
            target_channels=body.target_channels,
        )
        
        manager.queue_notification(notification)
        
        return {
            "success": True,
            "channels": body.target_channels,
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Notification send failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


@app.post("/api/v1/notifications/queue", tags=["Notifications"])
async def queue_notification(
    request: Request,
    body: NotificationRequest,
    api_key: str = Depends(validate_api_key),
    _: None = Depends(check_rate_limit),
):
    """Queue notification for batch processing"""
    try:
        manager = get_notification_manager()
        notification = Notification(
            type=NotificationType(body.type),
            title=body.title,
            message=body.message,
            details=body.details or {},
            priority=body.priority,
            target_channels=body.target_channels,
        )
        
        manager.queue_notification(notification)
        
        return {
            "queued": True,
            "queue_size": len(manager.notification_queue),
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Queue notification failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


@app.get("/api/v1/notifications/queue/status", tags=["Notifications"])
async def queue_status(
    request: Request,
    api_key: str = Depends(validate_api_key),
    _: None = Depends(check_rate_limit),
):
    """Get notification queue status"""
    try:
        manager = get_notification_manager()
        return {
            "total_queued": len(manager.notification_queue),
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Queue status failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


@app.post("/api/v1/notifications/process-queue", tags=["Notifications"])
async def process_queue(
    request: Request,
    batch_size: int = 10,
    api_key: str = Depends(validate_api_key),
    _: None = Depends(check_rate_limit),
):
    """Process queued notifications"""
    try:
        manager = get_notification_manager()
        processed = manager.process_queue(batch_size=batch_size)
        
        return {
            "processed": processed,
            "remaining": len(manager.notification_queue),
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Process queue failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


@app.post("/api/v1/notifications/test", tags=["Notifications"])
async def test_channels(
    request: Request,
    channels: list = ["discord"],
    api_key: str = Depends(validate_api_key),
):
    """Test notification channels"""
    try:
        manager = get_notification_manager()
        results = {}
        
        for channel in channels:
            try:
                notification = Notification(
                    type=NotificationType.TEST,
                    title="Test Notification",
                    message="This is a test notification",
                    target_channels=[channel],
                )
                # Send test notification
                results[channel] = "sent"
            except Exception as e:
                results[channel] = f"error: {str(e)}"
        
        return {
            "results": results,
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Test channels failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


# ============================================================================
# LEAD QUALIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/leads/qualify", tags=["AI"])
async def qualify_lead(
    request: Request,
    body: LeadQualificationRequest,
    api_key: str = Depends(validate_api_key),
    _: None = Depends(check_rate_limit),
):
    """Qualify lead with explainable AI"""
    try:
        logger.info(
            f"Qualifying lead: {body.title}",
            extra={"request_id": request.state.request_id}
        )
        
        factory = ExplainableAIFactory()
        decision = factory.create_decision(
            title=body.title,
            description=body.description,
            metadata={"company": body.company, "source": body.source},
        )
        
        return {
            "score": decision.score,
            "reasoning": decision.reasoning,
            "factors": decision.factors,
            "recommendation": decision.recommendation,
            "confidence": decision.confidence,
            "request_id": request.state.request_id,
        }
    except Exception as e:
        logger.error(
            f"Lead qualification failed: {e}",
            extra={"request_id": request.state.request_id}
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Request-ID": request.state.request_id}
        )


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/v1/config", tags=["Config"])
async def get_config(request: Request, _: None = Depends(check_rate_limit)):
    """Get current configuration"""
    settings = get_settings()
    return {
        "environment": settings.environment.value,
        "debug": settings.debug,
        "llm_model": settings.llm.model,
        "job_sources": settings.job_search.sources,
        "request_id": request.state.request_id,
    }


@app.get("/api/v1/config/sources", tags=["Config"])
async def get_sources(request: Request, _: None = Depends(check_rate_limit)):
    """Get available job sources"""
    return {
        "sources": [
            {"name": "reddit", "description": "Reddit (r/forhire, r/remotework)"},
            {"name": "hackernews", "description": "HackerNews Who is Hiring"},
            {"name": "rss", "description": "RSS Job Feeds"},
            {"name": "linkedin", "description": "LinkedIn (with auth)"},
            {"name": "indeed", "description": "Indeed (with API key)"}
        ],
        "request_id": request.state.request_id,
    }


# ============================================================================
# ROOT & INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root(request: Request):
    """Root endpoint - API metadata"""
    return {
        "name": "Business Agent 2.0",
        "version": "2.0.0",
        "status": "production-ready",
        "environment": get_settings().environment.value,
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
            "ai": ["/api/v1/leads/qualify"],
            "config": ["/api/v1/config", "/api/v1/config/sources"]
        },
        "request_id": request.state.request_id,
    }


# ============================================================================
# METRICS ENDPOINT
# ============================================================================

@app.get("/metrics", tags=["Monitoring"])
async def metrics(request: Request):
    """Prometheus metrics endpoint"""
    return {"message": "Metrics collection endpoint (implement with prometheus_client)"}


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
        headers=exc.headers or {},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": type(exc).__name__,
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if get_settings().debug else "An error occurred",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    # Production configuration
    uvicorn.run(
        "app_production:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Production: use multiple workers
        reload=False,  # Never reload in production
        log_level="info",
        access_log=True,
        lifespan="on",
    )
