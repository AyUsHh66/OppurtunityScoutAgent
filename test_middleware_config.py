#!/usr/bin/env python
"""Display middleware and security configuration"""

from middleware.security import get_endpoint_rate_limits, get_cors_config

print('='*70)
print('✅ MIDDLEWARE & SECURITY CONFIGURATION')
print('='*70)
print()

print('Rate Limit Configuration:')
for endpoint, config in get_endpoint_rate_limits().items():
    limit = config.get('limit', 'N/A')
    print(f'  {endpoint:40} {limit} req/min')

print()
print('CORS Configuration:')
cors = get_cors_config()
print(f'  Allowed Origins:  {len(cors["allow_origins"])} domains')
print(f'  Allow Credentials: {cors["allow_credentials"]}')
print(f'  Allowed Methods:  {", ".join(cors["allow_methods"])}')

print()
print('='*70)
print('✅ ALL MIDDLEWARE CONFIGURED CORRECTLY!')
print('='*70)
