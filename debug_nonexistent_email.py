#!/usr/bin/env python3
"""
Debug non-existent user email sending
"""

import asyncio
from utils.email_service import send_password_reset_email

async def test_nonexistent_user_email():
    print("🧪 Testing email sending for non-existent user...")
    
    try:
        result = await send_password_reset_email(
            to_email="nonexistent.debug@example.com",
            reset_token="invalid_token_user_not_found",
            user_name="User",
            user_exists=False
        )
        
        print(f"📧 Email sending result: {result}")
        print(f"✅ Email sent successfully: {result}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nonexistent_user_email())
