#!/usr/bin/env python3
"""
Database User Verification Tool
Check if specific users exist in the database and analyze user data
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseUserChecker:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "student_management_db")
        
    async def connect_to_database(self):
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client.get_database(self.db_name)
            print(f"✅ Connected to database: {self.db_name}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def check_specific_user(self, email):
        """Check if a specific user exists"""
        print(f"\n🔍 Checking user: {email}")
        print("-" * 50)
        
        try:
            user = await self.db.users.find_one({"email": email})
            
            if user:
                print(f"✅ User EXISTS in database")
                print(f"📧 Email: {user.get('email')}")
                print(f"👤 Full Name: {user.get('full_name', 'N/A')}")
                print(f"🆔 User ID: {user.get('id')}")
                print(f"📱 Phone: {user.get('phone', 'N/A')}")
                print(f"🔑 Role: {user.get('role', 'N/A')}")
                print(f"✅ Active: {user.get('is_active', 'N/A')}")
                print(f"📅 Created: {user.get('created_at', 'N/A')}")
                return True
            else:
                print(f"❌ User DOES NOT EXIST in database")
                return False
                
        except Exception as e:
            print(f"❌ Error checking user: {e}")
            return False
    
    async def list_all_users(self):
        """List all users in the database"""
        print(f"\n📋 All Users in Database")
        print("-" * 50)
        
        try:
            users = await self.db.users.find({}).to_list(length=None)
            
            if not users:
                print("❌ No users found in database")
                return []
            
            print(f"📊 Total users: {len(users)}")
            print()
            
            for i, user in enumerate(users, 1):
                email = user.get('email', 'No email')
                name = user.get('full_name', 'No name')
                role = user.get('role', 'No role')
                active = user.get('is_active', False)
                status = "✅ Active" if active else "❌ Inactive"
                
                print(f"{i:2d}. {email}")
                print(f"    👤 Name: {name}")
                print(f"    🔑 Role: {role}")
                print(f"    📊 Status: {status}")
                print()
            
            return users
            
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []
    
    async def create_test_user(self, email, name="Test User"):
        """Create a test user for testing"""
        print(f"\n➕ Creating test user: {email}")
        print("-" * 50)
        
        try:
            # Check if user already exists
            existing_user = await self.db.users.find_one({"email": email})
            if existing_user:
                print(f"⚠️  User already exists: {email}")
                return existing_user
            
            # Import required modules for user creation
            import uuid
            from utils.auth import hash_password
            
            # Create new user
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "password": hash_password("testpassword123"),
                "full_name": name,
                "first_name": name.split()[0] if name else "Test",
                "last_name": name.split()[-1] if len(name.split()) > 1 else "User",
                "phone": "+1234567890",
                "role": "student",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                print(f"✅ User created successfully")
                print(f"📧 Email: {email}")
                print(f"👤 Name: {name}")
                print(f"🔑 Password: testpassword123")
                print(f"🆔 ID: {user_data['id']}")
                return user_data
            else:
                print(f"❌ Failed to create user")
                return None
                
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    async def analyze_database_structure(self):
        """Analyze the database structure and collections"""
        print(f"\n🔍 Database Structure Analysis")
        print("-" * 50)
        
        try:
            # List all collections
            collections = await self.db.list_collection_names()
            print(f"📊 Collections in database: {len(collections)}")
            
            for collection in collections:
                count = await self.db[collection].count_documents({})
                print(f"   📁 {collection}: {count} documents")
            
            # Check users collection specifically
            if 'users' in collections:
                print(f"\n👥 Users Collection Analysis:")
                
                # Sample user document structure
                sample_user = await self.db.users.find_one({})
                if sample_user:
                    print(f"📋 Sample user document structure:")
                    for key, value in sample_user.items():
                        value_type = type(value).__name__
                        print(f"   {key}: {value_type}")
                
                # Check for email field variations
                email_variations = [
                    {"email": {"$exists": True}},
                    {"Email": {"$exists": True}},
                    {"EMAIL": {"$exists": True}},
                    {"user_email": {"$exists": True}}
                ]
                
                for variation in email_variations:
                    count = await self.db.users.count_documents(variation)
                    field_name = list(variation.keys())[0]
                    if count > 0:
                        print(f"   📧 {field_name} field: {count} users")
            
        except Exception as e:
            print(f"❌ Error analyzing database: {e}")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("🔌 Database connection closed")
    
    async def run_comprehensive_check(self):
        """Run comprehensive database user check"""
        print("🔍 DATABASE USER VERIFICATION")
        print("=" * 60)
        
        # Connect to database
        if not await self.connect_to_database():
            return
        
        try:
            # Analyze database structure
            await self.analyze_database_structure()
            
            # List all existing users
            users = await self.list_all_users()
            
            # Check specific problematic user
            target_email = "pittisunilkumar4@gmail.com"
            user_exists = await self.check_specific_user(target_email)
            
            # Check the working test user
            working_email = "pittisunilkumar3@gmail.com"
            await self.check_specific_user(working_email)
            
            # Create the missing user if needed
            if not user_exists:
                print(f"\n🔧 SOLUTION: Creating missing user")
                await self.create_test_user(target_email, "Test User 4")
                
                # Verify creation
                print(f"\n✅ Verification after creation:")
                await self.check_specific_user(target_email)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total users in database: {len(users)}")
            print(f"   Target user ({target_email}): {'✅ EXISTS' if user_exists else '❌ MISSING'}")
            print(f"   Working user ({working_email}): Available for comparison")
            
        finally:
            await self.close_connection()

if __name__ == "__main__":
    checker = DatabaseUserChecker()
    asyncio.run(checker.run_comprehensive_check())
