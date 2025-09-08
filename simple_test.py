#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8003"

# Get superadmin token
admin_login = {"email": "testsuperadmin@example.com", "password": "TestSuperAdmin123!"}
response = requests.post(f"{BASE_URL}/api/superadmin/login", json=admin_login)

print(f"Login Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["data"]["token"]
    
    # Test user list
    headers = {"Authorization": f"Bearer {token}"}
    user_response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    print(f"User List Status: {user_response.status_code}")
    print(f"Response: {user_response.text}")
else:
    print(f"Login failed: {response.text}")
