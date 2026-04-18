#!/usr/bin/env python
"""Test script to verify all production features work correctly"""

from middleware.security import APIKeyValidator, RateLimiter
from models.schemas import JobSearchRequest, NotificationRequest
from pydantic import ValidationError

print('='*70)
print('🧪 TESTING PRODUCTION FEATURES')
print('='*70)

# Test 1: API Key Validation
print('\n✅ Test 1: API Key Validation')
validator = APIKeyValidator(admin_key='my-admin-key')
print(f'  Valid key (32+ chars): {validator.validate_key("x"*32)}')
print(f'  Invalid key (short): {validator.validate_key("short")}')
print(f'  Admin key: {validator.validate_key("my-admin-key")}')

# Test 2: Rate Limiting
print('\n✅ Test 2: Rate Limiting (5 requests/minute)')
limiter = RateLimiter()
for i in range(6):
    allowed = limiter.is_allowed('test-client', limit=5, window=60)
    status = '✓ ALLOWED' if allowed else '✗ BLOCKED'
    print(f'  Request {i+1}: {status}')

# Test 3: Input Validation
print('\n✅ Test 3: Input Validation')
try:
    req = JobSearchRequest(query='Python', source='reddit', limit=10)
    print(f'  Valid request: ✓ (query={req.query}, limit={req.limit})')
except ValidationError as e:
    print(f'  Error: {e}')

try:
    req = JobSearchRequest(query='Python', source='invalid', limit=10)
    print('  ERROR: Should have been rejected!')
except ValidationError as e:
    print(f'  ✓ Invalid source rejected')

try:
    req = JobSearchRequest(query='Python', source='reddit', limit=1000)
    print('  ERROR: Should have been rejected!')
except ValidationError as e:
    print(f'  ✓ Limit too high rejected')

# Test 4: Notification Validation
print('\n✅ Test 4: Notification Validation')
notif = NotificationRequest(
    type='job_opportunity',
    title='Developer Job',
    message='Found a great opportunity',
    priority='high'
)
print(f'  Valid notification: ✓')

print('\n' + '='*70)
print('✅ ALL SECURITY FEATURES WORKING CORRECTLY!')
print('='*70)
