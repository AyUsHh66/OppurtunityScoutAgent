"""
Data models and schemas for Business Agent 2.0
"""

from .schemas import (
    JobSearchRequest,
    NotificationRequest,
    LeadQualificationRequest,
    QueueNotificationRequest,
    TestNotificationRequest,
    HealthResponse,
    ReadyResponse,
    JobSearchResponse,
    NotificationResponse,
    QueueStatusResponse,
    ProcessQueueResponse,
    LeadQualificationResponse,
    ConfigResponse,
    ErrorResponse,
    PaginationParams,
)

__all__ = [
    # Requests
    "JobSearchRequest",
    "NotificationRequest",
    "LeadQualificationRequest",
    "QueueNotificationRequest",
    "TestNotificationRequest",
    # Responses
    "HealthResponse",
    "ReadyResponse",
    "JobSearchResponse",
    "NotificationResponse",
    "QueueStatusResponse",
    "ProcessQueueResponse",
    "LeadQualificationResponse",
    "ConfigResponse",
    "ErrorResponse",
    # Utilities
    "PaginationParams",
]
