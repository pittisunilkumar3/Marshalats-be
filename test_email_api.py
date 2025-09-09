#!/usr/bin/env python3
"""
Test the forgot password API endpoint
"""

import requests
import json

def test_forgot_password_api():
    """Test the forgot password API endpoint"""
    url = 'http://localhost:8003/auth/forgot-password'
    data = {'email': 'pittisunilkumar3@gmail.com'}

    print('🧪 Testing Forgot Password API')
    print(f'📡 URL: {url}')
    print(f'📧 Email: {data["email"]}')
    print()

    try:
        response = requests.post(url, json=data, timeout=30)
        print(f'📊 Status Code: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ API Response: Success')
            print(f'📄 Message: {result.get("message", "No message")}')
            
            # Check if email_sent field exists
            if 'email_sent' in result:
                print(f'📧 Email Sent: {result["email_sent"]}')
            else:
                print('📧 Email Sent: Not specified in response')
                
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'📄 Response: {response.text}')
            
    except Exception as e:
        print(f'❌ Request failed: {e}')

if __name__ == "__main__":
    test_forgot_password_api()
