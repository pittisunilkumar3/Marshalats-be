#!/usr/bin/env python3
"""
Test non-existent user email sending
"""

import requests
import json

# Test the forgot password API for non-existent user
url = 'http://localhost:8003/auth/forgot-password'
payload = {'email': 'nonexistent.test@example.com'}

print('🧪 Testing non-existent user email sending...')
print(f'📧 Email: {payload["email"]}')

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f'📊 Status: {response.status_code}')
    print(f'📄 Response: {json.dumps(response.json(), indent=2)}')
except Exception as e:
    print(f'❌ Error: {e}')
