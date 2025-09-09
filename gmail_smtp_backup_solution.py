#!/usr/bin/env python3
"""
Gmail SMTP Backup Solution
Configure Gmail SMTP as a reliable backup for email delivery
"""

import os
import smtplib
import ssl
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class GmailSMTPSetup:
    def __init__(self):
        self.gmail_user = "pittisunilkumar3@gmail.com"  # Your Gmail address
        self.gmail_app_password = ""  # Will be set by user
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"📧 {title}")
        print(f"{'='*70}")
        
    def print_section(self, title):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 50)
    
    def generate_app_password_instructions(self):
        """Generate instructions for creating Gmail App Password"""
        self.print_section("Gmail App Password Setup Instructions")
        
        print("🔐 To use Gmail SMTP, you need to create an App Password:")
        print()
        print("1. 🌐 Go to your Google Account settings:")
        print("   https://myaccount.google.com/")
        print()
        print("2. 🔒 Navigate to Security > 2-Step Verification")
        print("   (You must have 2-Step Verification enabled)")
        print()
        print("3. 📱 Scroll down to 'App passwords' and click it")
        print()
        print("4. 🏷️  Select 'Mail' and 'Other (Custom name)'")
        print("   Enter: 'Martial Arts Academy System'")
        print()
        print("5. 📋 Copy the 16-character app password generated")
        print("   (It will look like: abcd efgh ijkl mnop)")
        print()
        print("6. ✅ Use this app password in the configuration below")
        
    def test_gmail_smtp(self, app_password):
        """Test Gmail SMTP configuration"""
        self.print_section("Testing Gmail SMTP Configuration")
        
        try:
            print("🔌 Connecting to Gmail SMTP...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                print("✅ Connected to Gmail SMTP")
                
                print("🔑 Authenticating...")
                server.login(self.gmail_user, app_password)
                print("✅ Authentication successful")
                
                # Send test email
                print("📧 Sending test email...")
                success = self.send_test_email(server)
                
                if success:
                    print("🎉 Gmail SMTP test successful!")
                    return True
                else:
                    print("❌ Test email failed")
                    return False
                    
        except Exception as e:
            print(f"❌ Gmail SMTP test failed: {e}")
            return False
    
    def send_test_email(self, server):
        """Send a test email via Gmail SMTP"""
        try:
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Gmail SMTP Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            message["From"] = self.gmail_user
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
Gmail SMTP Backup Test

This email was sent using Gmail SMTP as a backup email service.

Test Details:
- Sent from: {self.gmail_user}
- SMTP Server: smtp.gmail.com:465
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Purpose: Backup email service verification

If you receive this email, Gmail SMTP is working correctly as a backup.

Best regards,
Martial Arts Academy Email System
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Gmail SMTP Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
        .header {{ background: #4285f4; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ background: #666; color: white; padding: 15px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 Gmail SMTP Backup Test</h1>
        <p>Martial Arts Academy System</p>
    </div>
    
    <div class="content">
        <div class="success">
            <strong>✅ Success!</strong> Gmail SMTP backup is working correctly.
        </div>
        
        <h3>Test Information:</h3>
        <p><strong>Sent from:</strong> {self.gmail_user}</p>
        <p><strong>SMTP Server:</strong> smtp.gmail.com:465</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Purpose:</strong> Backup email service verification</p>
        
        <p>This confirms that Gmail SMTP can be used as a reliable backup for password reset emails.</p>
    </div>
    
    <div class="footer">
        <p>Martial Arts Academy Email System<br>
        Gmail SMTP Backup Test</p>
    </div>
</body>
</html>
            """.strip()
            
            # Add parts to message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            server.sendmail(self.gmail_user, self.test_email, message.as_string())
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
    
    def generate_env_configuration(self, app_password):
        """Generate .env configuration for Gmail SMTP"""
        self.print_section("Gmail SMTP Configuration")
        
        print("📝 Add these lines to your .env file for Gmail SMTP backup:")
        print()
        print("# Gmail SMTP Backup Configuration")
        print(f"GMAIL_SMTP_HOST=smtp.gmail.com")
        print(f"GMAIL_SMTP_PORT=465")
        print(f"GMAIL_SMTP_USER={self.gmail_user}")
        print(f"GMAIL_SMTP_PASS={app_password}")
        print(f"GMAIL_SMTP_FROM={self.gmail_user}")
        print()
        print("📋 To switch to Gmail SMTP, update these variables:")
        print(f"SMTP_HOST=smtp.gmail.com")
        print(f"SMTP_PORT=465")
        print(f"SMTP_USER={self.gmail_user}")
        print(f"SMTP_PASS={app_password}")
        print(f"SMTP_FROM={self.gmail_user}")
    
    def create_backup_email_service(self):
        """Create a backup email service configuration"""
        self.print_section("Backup Email Service Implementation")
        
        backup_service_code = '''
# Add this to utils/email_service.py for Gmail backup

class GmailBackupService:
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 465
        self.smtp_user = os.getenv('GMAIL_SMTP_USER', '')
        self.smtp_pass = os.getenv('GMAIL_SMTP_PASS', '')
        self.smtp_from = os.getenv('GMAIL_SMTP_FROM', self.smtp_user)
        self.enabled = bool(self.smtp_user and self.smtp_pass)
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        if not self.enabled:
            return False
            
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_from
            message["To"] = to_email
            
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_from, to_email, message.as_string())
            
            return True
            
        except Exception as e:
            logger.error(f"Gmail backup email failed: {e}")
            return False

# Usage in main email service:
async def send_email_with_backup(to_email, subject, body, html_body=None):
    # Try primary SMTP first
    primary_service = get_email_service()
    if await primary_service.send_email(to_email, subject, body, html_body):
        return True
    
    # Fallback to Gmail backup
    backup_service = GmailBackupService()
    return await backup_service.send_email(to_email, subject, body, html_body)
        '''
        
        print("📄 Backup service implementation:")
        print(backup_service_code)
    
    def run_gmail_setup(self):
        """Run the complete Gmail SMTP setup process"""
        self.print_header("GMAIL SMTP BACKUP SETUP")
        
        print("🚀 Setting up Gmail SMTP as a backup email service...")
        print(f"📧 Gmail account: {self.gmail_user}")
        
        # Show instructions
        self.generate_app_password_instructions()
        
        # Get app password from user
        print("\n" + "="*50)
        app_password = input("📋 Enter your Gmail App Password (16 characters): ").strip()
        
        if len(app_password) != 16:
            print("❌ Invalid app password length. Should be 16 characters.")
            return False
        
        # Test Gmail SMTP
        if self.test_gmail_smtp(app_password):
            print("\n🎉 Gmail SMTP setup successful!")
            
            # Generate configuration
            self.generate_env_configuration(app_password)
            self.create_backup_email_service()
            
            print("\n📋 NEXT STEPS:")
            print("1. ✅ Gmail SMTP is working as backup")
            print("2. 📝 Update your .env file with Gmail configuration")
            print("3. 🔄 Restart your application server")
            print("4. 🧪 Test password reset functionality")
            
            return True
        else:
            print("\n❌ Gmail SMTP setup failed")
            print("🔧 Please check your app password and try again")
            return False

if __name__ == "__main__":
    setup = GmailSMTPSetup()
    setup.run_gmail_setup()
