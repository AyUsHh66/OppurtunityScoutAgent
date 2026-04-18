"""
Request/Response schemas for API validation
Uses Pydantic for type checking and validation
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum


class JobSearchRequest(BaseModel):
    """Request body for job search"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    source: Optional[str] = Field(
        "reddit",
        regex="^(reddit|hackernews|rss|linkedin|indeed)$",
        description="Job source"
    )
    limit: int = Field(10, ge=1, le=100, description="Max results")
    location: Optional[str] = Field(None, max_length=100, description="Location filter")
    
    class Config:
        example = {
            "query": "Python developer",
            "source": "reddit",
            "limit": 10,
            "location": "Remote"
        }


class NotificationRequest(BaseModel):
    """Request body for sending notifications"""
    type: str = Field(
        ...,
        regex="^(job_opportunity|qualified_lead|enrichment_complete|system_alert)$",
        description="Notification type"
    )
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, max_length=1000, description="Message body")
    details: Optional[Dict[str, Any]] = Field(None, description="Extra details")
    priority: Optional[str] = Field(
        "normal",
        regex="^(low|normal|high|critical)$",
        description="Priority level"
    )
    target_channels: Optional[List[str]] = Field(
        ["discord"],
        description="Target channels"
    )
    
    @validator("target_channels")
    def validate_channels(cls, v):
        valid = {"discord", "email", "trello", "notion"}
        if not all(c in valid for c in v):
            raise ValueError(f"Invalid channels. Must be in {valid}")
        return v
    
    class Config:
        example = {
            "type": "job_opportunity",
            "title": "Senior Python Developer",
            "message": "Found matching job",
            "priority": "high",
            "target_channels": ["discord"]
        }


class LeadQualificationRequest(BaseModel):
    """Request body for lead qualification"""
    title: str = Field(..., min_length=1, max_length=200, description="Lead title")
    description: str = Field(..., min_length=1, max_length=2000, description="Lead details")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    source: Optional[str] = Field(None, max_length=100, description="Data source")
    
    class Config:
        example = {
            "title": "Looking for web developer",
            "description": "Startup seeking experienced React developer...",
            "company": "TechStartup Inc",
            "source": "reddit"
        }


class QueueNotificationRequest(BaseModel):
    """Request body for queueing notifications"""
    notification: NotificationRequest = Field(..., description="Notification to queue")
    process_after: Optional[int] = Field(0, ge=0, description="Delay in seconds")
    
    class Config:
        example = {
            "notification": {
                "type": "job_opportunity",
                "title": "Senior Python Developer",
                "message": "Found matching job",
            },
            "process_after": 300
        }


class TestNotificationRequest(BaseModel):
    """Request body for testing notification channels"""
    channels: List[str] = Field(
        ["discord"],
        description="Channels to test"
    )
    
    @validator("channels")
    def validate_channels(cls, v):
        valid = {"discord", "email", "trello", "notion"}
        if not all(c in valid for c in v):
            raise ValueError(f"Invalid channels. Must be in {valid}")
        return v
    
    class Config:
        example = {
            "channels": ["discord", "email"]
        }


# Response schemas

class HealthResponse(BaseModel):
    """Response from health check"""
    status: str
    service: str
    version: Optional[str] = None
    timestamp: Optional[str] = None


class ReadyResponse(BaseModel):
    """Response from readiness check"""
    ready: bool
    environment: str
    version: str
    checks: Optional[Dict[str, bool]] = None


class JobSearchResponse(BaseModel):
    """Response from job search"""
    query: str
    source: str
    results: List[Dict[str, Any]]
    count: int
    timestamp: str


class NotificationResponse(BaseModel):
    """Response from notification send"""
    success: bool
    channels_sent: List[str]
    message_id: Optional[str] = None
    error: Optional[str] = None


class QueueStatusResponse(BaseModel):
    """Response with queue status"""
    total_queued: int
    pending: int
    failed: int
    last_processed: Optional[str] = None


class ProcessQueueResponse(BaseModel):
    """Response from processing queue"""
    processed: int
    failed: int
    errors: Optional[List[Dict[str, Any]]] = None


class LeadQualificationResponse(BaseModel):
    """Response from lead qualification"""
    score: float = Field(..., ge=0, le=10, description="Qualification score")
    reasoning: str
    factors: Dict[str, Any]
    recommendation: str
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")


class ConfigResponse(BaseModel):
    """Response with current configuration"""
    environment: str
    debug: bool
    llm_model: str
    job_sources: List[str]
    notification_channels: List[str]
    version: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    status_code: int


# Pagination and filtering

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(0, ge=0, description="Skip first N results")
    limit: int = Field(10, ge=1, le=100, description="Max results")
    sort_by: Optional[str] = Field(None, description="Sort field")
    descending: Optional[bool] = Field(False, description="Sort order")
