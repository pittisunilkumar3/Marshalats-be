#!/usr/bin/env python3
"""
Check if user exists in database
"""

import asyncio
from utils.database import get_db

async def check_user():
    """Check if the test user exists in database"""
    db = get_db()
    test_email = 'pittisunilkumar3@gmail.com'
    
    print(f'🔍 Checking for user: {test_email}')
    user = await db.users.find_one({'email': test_email})
    
    if user:
        print('✅ User found in database')
        print(f'📧 Email: {user.get("email")}')
        print(f'👤 Name: {user.get("full_name", "N/A")}')
        print(f'🆔 ID: {user.get("id")}')
        print(f'📱 Phone: {user.get("phone", "N/A")}')
        print(f'🔑 Role: {user.get("role", "N/A")}')
    else:
        print('❌ User not found in database')
        print('📝 Available users:')
        users = await db.users.find({}).to_list(length=10)
        for u in users:
            email = u.get("email", "No email")
            name = u.get("full_name", "No name")
            print(f'   - {email} ({name})')

if __name__ == "__main__":
    asyncio.run(check_user())
