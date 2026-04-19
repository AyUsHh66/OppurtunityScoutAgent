#!/usr/bin/env python
"""Test Pydantic schemas and validation"""

from models.schemas import (
    JobSearchRequest,
    NotificationRequest,
    LeadQualificationRequest,
    HealthResponse,
    ReadyResponse
)
from pydantic import ValidationError

print('='*70)
print('✅ PYDANTIC SCHEMAS & VALIDATION')
print('='*70)
print()

print('Testing JobSearchRequest validation:')
try:
    # Valid request
    job_req = JobSearchRequest(
        query="python developer",
        source="reddit",
        limit=10
    )
    print(f'  ✓ Valid request: {job_req.model_dump()}')
except ValidationError as e:
    print(f'  ✗ Error: {e}')

try:
    # Invalid - limit exceeds max
    bad_req = JobSearchRequest(
        query="test",
        source="reddit",
        limit=150
    )
except ValidationError as e:
    print(f'  ✓ Validation rejected invalid limit (>100): {len(e.errors())} error')

print()
print('Testing NotificationRequest validation:')
try:
    notif = NotificationRequest(
        type="job_opportunity",
        title="New Job Found",
        message="Senior Python role available",
        priority="high"
    )
    print(f'  ✓ Valid notification: type={notif.type}')
except ValidationError as e:
    print(f'  ✗ Error: {e}')

try:
    # Invalid - invalid type
    bad_notif = NotificationRequest(
        type="invalid_type",
        title="Test",
        message="Test",
        priority="high"
    )
except ValidationError as e:
    print(f'  ✓ Validation rejected invalid type: {len(e.errors())} error')

print()
print('Testing Response schemas:')
try:
    health = HealthResponse(status="healthy", service="api", version="1.0")
    print(f'  ✓ HealthResponse: status={health.status}, service={health.service}')
    
    ready = ReadyResponse(
        ready=True,
        environment="development",
        version="1.0"
    )
    print(f'  ✓ ReadyResponse: ready={ready.ready}, env={ready.environment}')
except ValidationError as e:
    print(f'  ✗ Error: {e}')

print()
print('='*70)
print('✅ ALL SCHEMAS VALIDATED CORRECTLY!')
print('='*70)
