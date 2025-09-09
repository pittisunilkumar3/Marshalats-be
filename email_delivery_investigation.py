#!/usr/bin/env python3
"""
Deep Email Delivery Investigation Tool
Comprehensive analysis of email delivery issues
"""

import asyncio
import smtplib
import socket
import dns.resolver
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailDeliveryInvestigator:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.from_email = os.getenv('SMTP_FROM', 'info@sveats.cyberdetox.in')
        
    def print_header(self, title):
        print(f"\n{'='*70}")
        print(f"🔍 {title}")
        print(f"{'='*70}")
        
    def print_section(self, title):
        print(f"\n📋 {title}")
        print("-" * 50)
        
    async def check_smtp_connection(self):
        """Test SMTP connection and authentication"""
        self.print_section("SMTP Connection Test")
        
        try:
            print(f"🌐 Connecting to {self.smtp_host}:{self.smtp_port}")
            
            # Test connection
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.set_debuglevel(1)  # Enable debug output
            
            print("✅ Connection established")
            
            # Test STARTTLS
            server.starttls()
            print("✅ STARTTLS successful")
            
            # Test authentication
            server.login(self.smtp_user, self.smtp_pass)
            print("✅ Authentication successful")
            
            server.quit()
            print("✅ SMTP connection test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            return False
    
    def check_dns_records(self):
        """Check DNS records for email authentication"""
        self.print_section("DNS Records Check")
        
        domain = self.smtp_host
        
        # Check MX record
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            print(f"✅ MX Records found for {domain}:")
            for mx in mx_records:
                print(f"   📧 {mx}")
        except Exception as e:
            print(f"❌ MX Record check failed: {e}")
        
        # Check SPF record
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            spf_found = False
            for txt in txt_records:
                if 'v=spf1' in str(txt):
                    print(f"✅ SPF Record found: {txt}")
                    spf_found = True
            if not spf_found:
                print("⚠️  No SPF record found")
        except Exception as e:
            print(f"❌ SPF Record check failed: {e}")
    
    def check_blacklist_status(self):
        """Check if domain/IP is blacklisted"""
        self.print_section("Blacklist Status Check")
        
        try:
            # Get IP address of SMTP server
            ip = socket.gethostbyname(self.smtp_host)
            print(f"📍 SMTP Server IP: {ip}")
            
            # Check some common blacklists
            blacklists = [
                'zen.spamhaus.org',
                'bl.spamcop.net',
                'dnsbl.sorbs.net'
            ]
            
            for bl in blacklists:
                try:
                    # Reverse IP for blacklist check
                    reversed_ip = '.'.join(reversed(ip.split('.')))
                    query = f"{reversed_ip}.{bl}"
                    
                    result = socket.gethostbyname(query)
                    print(f"❌ BLACKLISTED on {bl}: {result}")
                except socket.gaierror:
                    print(f"✅ NOT blacklisted on {bl}")
                except Exception as e:
                    print(f"⚠️  Could not check {bl}: {e}")
                    
        except Exception as e:
            print(f"❌ Blacklist check failed: {e}")
    
    async def send_test_email_with_tracking(self, to_email):
        """Send a test email with detailed tracking"""
        self.print_section(f"Sending Test Email to {to_email}")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🧪 EMAIL DELIVERY TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Reply-To'] = self.from_email
            
            # Text version
            text_body = f"""
EMAIL DELIVERY INVESTIGATION TEST

This is a test email to verify email delivery.

Timestamp: {datetime.now().isoformat()}
From: {self.from_email}
SMTP Server: {self.smtp_host}:{self.smtp_port}

If you receive this email, the delivery system is working correctly.

Please check the following locations if you don't see this email:
1. Spam/Junk folder
2. Promotions tab (Gmail)
3. Updates tab (Gmail)
4. All Mail folder

Best regards,
Email Delivery Investigation System
            """.strip()
            
            # HTML version
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Delivery Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f0f8ff; padding: 20px; text-align: center; border-radius: 8px; }}
        .content {{ background-color: #ffffff; padding: 20px; border: 1px solid #ddd; margin-top: 10px; }}
        .info {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .timestamp {{ font-family: monospace; background-color: #f5f5f5; padding: 10px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 EMAIL DELIVERY TEST</h1>
            <p>Email Delivery Investigation System</p>
        </div>
        
        <div class="content">
            <h2>Test Email Received Successfully!</h2>
            
            <div class="info">
                <strong>📧 Email Details:</strong><br>
                <div class="timestamp">
                    Timestamp: {datetime.now().isoformat()}<br>
                    From: {self.from_email}<br>
                    SMTP Server: {self.smtp_host}:{self.smtp_port}<br>
                    To: {to_email}
                </div>
            </div>
            
            <p>If you receive this email, the delivery system is working correctly.</p>
            
            <div class="info">
                <strong>🔍 If you don't see other emails, check:</strong>
                <ul>
                    <li>📁 Spam/Junk folder</li>
                    <li>📢 Promotions tab (Gmail)</li>
                    <li>📰 Updates tab (Gmail)</li>
                    <li>📂 All Mail folder</li>
                </ul>
            </div>
            
            <p>Best regards,<br>Email Delivery Investigation System</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            
            result = server.send_message(msg)
            server.quit()
            
            print(f"✅ Test email sent successfully to {to_email}")
            print(f"📧 Message ID: {msg.get('Message-ID', 'Not available')}")
            print(f"⏰ Sent at: {datetime.now().isoformat()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
    
    def print_email_location_guide(self, email):
        """Print comprehensive guide for finding emails"""
        self.print_section("📧 WHERE TO FIND YOUR EMAILS")
        
        print(f"""
🎯 IMMEDIATE ACTION STEPS for {email}:

1. 🌐 GMAIL WEB INTERFACE (https://gmail.com)
   • Click "All Mail" on left sidebar
   • Search: from:{self.from_email}
   • Search: subject:"Password Reset Request"
   • Search: "Martial Arts Academy"

2. 🗑️ CHECK SPAM FOLDER (MOST LIKELY LOCATION)
   • Click "Spam" folder in Gmail
   • Look for emails from "Martial Arts Academy"
   • If found, click "Not Spam" to whitelist

3. 📱 MOBILE APP CHECK
   • Open Gmail mobile app
   • Pull down to refresh
   • Check "All mail" section
   • Search for "sveats" or "martial"

4. 📂 CHECK ALL GMAIL TABS
   • Primary inbox
   • Promotions tab
   • Updates tab
   • Social tab

⏰ TIMING: Emails may take 5-30 minutes to appear for new senders.

🚨 MOST LIKELY: Your emails are in the SPAM folder!
        """)

async def main():
    investigator = EmailDeliveryInvestigator()
    
    investigator.print_header("DEEP EMAIL DELIVERY INVESTIGATION")
    
    print("🎯 This tool will perform comprehensive email delivery analysis")
    print("📧 We'll test every aspect of email delivery to find the issue")
    
    # Get email to test
    test_email = input("\n📧 Enter your email address to test: ").strip()
    if not test_email:
        test_email = "pittisunilkumar3@gmail.com"
        print(f"Using default: {test_email}")
    
    # Run all checks
    await investigator.check_smtp_connection()
    investigator.check_dns_records()
    investigator.check_blacklist_status()
    
    # Send test email
    await investigator.send_test_email_with_tracking(test_email)
    
    # Print location guide
    investigator.print_email_location_guide(test_email)
    
    investigator.print_header("INVESTIGATION COMPLETE")
    print("✅ All tests completed. Check the results above.")
    print("📧 A test email has been sent - check your spam folder!")

if __name__ == "__main__":
    asyncio.run(main())
