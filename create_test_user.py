#!/usr/bin/env python3
"""
Create a test user for email testing
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from utils.auth import hash_password
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

async def create_test_user():
    """Create a test user for email testing"""
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    db = client.get_database(db_name)
    
    test_email = 'pittisunilkumar3@gmail.com'
    
    print(f'🔍 Checking for existing user: {test_email}')
    existing_user = await db.users.find_one({'email': test_email})
    
    if existing_user:
        print('✅ User already exists')
        print(f'📧 Email: {existing_user.get("email")}')
        print(f'👤 Name: {existing_user.get("full_name", "N/A")}')
        print(f'🆔 ID: {existing_user.get("id")}')
    else:
        print('➕ Creating test user...')
        
        # Create test user
        user_data = {
            "id": str(uuid.uuid4()),
            "email": test_email,
            "password": hash_password("testpassword123"),
            "full_name": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "role": "student",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_data)
        
        if result.inserted_id:
            print('✅ Test user created successfully')
            print(f'📧 Email: {test_email}')
            print(f'👤 Name: Test User')
            print(f'🔑 Password: testpassword123')
            print(f'🆔 ID: {user_data["id"]}')
        else:
            print('❌ Failed to create test user')
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
