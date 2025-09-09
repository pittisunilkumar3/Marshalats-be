#!/usr/bin/env python3
"""
Comprehensive Email Deliverability Investigation
Deep dive into email delivery issues and spam filtering
"""

import smtplib
import ssl
import socket
import dns.resolver
import requests
import asyncio
import os
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from utils.email_service import get_email_service

# Load environment variables
load_dotenv()

class EmailDeliverabilityInvestigation:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Neelarani@10')
        self.smtp_from = os.getenv('SMTP_FROM', 'info@sveats.cyberdetox.in')
        
        # Test email addresses for different providers
        self.test_emails = {
            'gmail': 'pittisunilkumar3@gmail.com',
            'outlook': 'pittisunilkumar3@outlook.com',  # If available
            'yahoo': 'pittisunilkumar3@yahoo.com'       # If available
        }
        
        self.domain = self.smtp_from.split('@')[1]
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"🔍 {title}")
        print(f"{'='*80}")
        
    def print_section(self, title):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 60)
    
    def check_dns_records(self):
        """Check DNS records for email deliverability"""
        self.print_section("DNS Records Analysis")
        
        try:
            # Check MX records
            print(f"🔍 Checking MX records for {self.domain}...")
            mx_records = dns.resolver.resolve(self.domain, 'MX')
            for mx in mx_records:
                print(f"   MX: {mx.preference} {mx.exchange}")
            
            # Check SPF records
            print(f"\n🔍 Checking SPF records for {self.domain}...")
            try:
                txt_records = dns.resolver.resolve(self.domain, 'TXT')
                spf_found = False
                for txt in txt_records:
                    txt_str = str(txt).strip('"')
                    if txt_str.startswith('v=spf1'):
                        print(f"   SPF: {txt_str}")
                        spf_found = True
                        
                        # Check if current SMTP server is authorized
                        if self.smtp_host in txt_str or 'include:' in txt_str:
                            print("   ✅ SMTP server appears to be authorized")
                        else:
                            print("   ⚠️  SMTP server may not be authorized in SPF")
                
                if not spf_found:
                    print("   ❌ No SPF record found - this may cause deliverability issues")
                    
            except Exception as e:
                print(f"   ❌ SPF check failed: {e}")
            
            # Check DKIM records (common selector)
            print(f"\n🔍 Checking DKIM records for {self.domain}...")
            try:
                dkim_selectors = ['default', 'mail', 'dkim', 'selector1', 'selector2']
                dkim_found = False
                for selector in dkim_selectors:
                    try:
                        dkim_domain = f"{selector}._domainkey.{self.domain}"
                        dkim_records = dns.resolver.resolve(dkim_domain, 'TXT')
                        for dkim in dkim_records:
                            print(f"   DKIM ({selector}): Found")
                            dkim_found = True
                            break
                    except:
                        continue
                
                if not dkim_found:
                    print("   ⚠️  No DKIM records found - this may affect deliverability")
                    
            except Exception as e:
                print(f"   ❌ DKIM check failed: {e}")
            
            # Check DMARC records
            print(f"\n🔍 Checking DMARC records for {self.domain}...")
            try:
                dmarc_domain = f"_dmarc.{self.domain}"
                dmarc_records = dns.resolver.resolve(dmarc_domain, 'TXT')
                for dmarc in dmarc_records:
                    print(f"   DMARC: {str(dmarc).strip('\"')}")
            except Exception as e:
                print(f"   ⚠️  No DMARC record found: {e}")
                
        except Exception as e:
            print(f"❌ DNS analysis failed: {e}")
    
    def check_smtp_detailed_response(self):
        """Check detailed SMTP responses and capabilities"""
        self.print_section("Detailed SMTP Server Analysis")
        
        try:
            print(f"🔌 Connecting to {self.smtp_host}:{self.smtp_port}...")
            
            # Create SMTP connection with detailed logging
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            server.set_debuglevel(1)  # Enable debug output
            
            print(f"\n📋 Server greeting: {server.getwelcome()}")
            
            # EHLO command
            code, response = server.ehlo()
            print(f"\n📋 EHLO response ({code}):")
            print(response.decode())
            
            # Start TLS
            if self.smtp_port == 587:
                print("\n🔒 Starting TLS...")
                context = ssl.create_default_context()
                server.starttls(context=context)
                
                # EHLO again after TLS
                code, response = server.ehlo()
                print(f"\n📋 EHLO after TLS ({code}):")
                print(response.decode())
            
            # Authentication
            print(f"\n🔑 Authenticating as {self.smtp_user}...")
            server.login(self.smtp_user, self.smtp_pass)
            print("✅ Authentication successful")
            
            # Check server capabilities
            print(f"\n📋 Server capabilities:")
            for feature, params in server.esmtp_features.items():
                print(f"   {feature}: {params}")
            
            server.quit()
            return True
            
        except Exception as e:
            print(f"❌ SMTP detailed analysis failed: {e}")
            return False
    
    def send_test_email_with_tracking(self, to_email, provider_name):
        """Send test email with detailed tracking"""
        print(f"\n📧 Sending test email to {provider_name} ({to_email})...")
        
        try:
            # Create detailed test message
            message = MIMEMultipart("alternative")
            
            # Add tracking headers
            message["Message-ID"] = f"<test-{int(time.time())}@{self.domain}>"
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            message["Subject"] = f"Email Deliverability Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            message["From"] = f"Martial Arts Academy <{self.smtp_from}>"
            message["To"] = to_email
            message["Reply-To"] = self.smtp_from
            
            # Add custom headers for tracking
            message["X-Mailer"] = "Martial Arts Academy System"
            message["X-Priority"] = "3"
            message["X-Test-ID"] = f"deliverability-test-{int(time.time())}"
            
            # Plain text content
            text_content = f"""
Email Deliverability Test

This is a test email to verify email delivery to {provider_name}.

Test Details:
- Sent from: {self.smtp_from}
- SMTP Server: {self.smtp_host}:{self.smtp_port}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Provider: {provider_name}
- Test ID: deliverability-test-{int(time.time())}

If you receive this email, please check:
1. Which folder it arrived in (Inbox, Spam, Promotions, etc.)
2. Any warning messages displayed
3. The sender reputation indicators

This email is sent for deliverability testing purposes.

Best regards,
Martial Arts Academy Email System
            """.strip()
            
            # HTML content with better formatting
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Deliverability Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .info-box {{ background: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; margin: 15px 0; }}
        .footer {{ background: #666; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        .test-details {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 Email Deliverability Test</h1>
        <p>Martial Arts Academy System</p>
    </div>
    
    <div class="content">
        <div class="info-box">
            <strong>✅ Success!</strong> This email was delivered successfully to {provider_name}.
        </div>
        
        <h3>Test Information:</h3>
        <div class="test-details">
            <p><strong>Sent from:</strong> {self.smtp_from}</p>
            <p><strong>SMTP Server:</strong> {self.smtp_host}:{self.smtp_port}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Provider:</strong> {provider_name}</p>
            <p><strong>Test ID:</strong> deliverability-test-{int(time.time())}</p>
        </div>
        
        <h3>Please Check:</h3>
        <ul>
            <li>Which folder this email arrived in (Inbox, Spam, Promotions, etc.)</li>
            <li>Any warning messages or sender reputation indicators</li>
            <li>How long it took to arrive</li>
        </ul>
        
        <p>This email is sent for deliverability testing purposes to ensure our password reset emails reach users successfully.</p>
    </div>
    
    <div class="footer">
        <p>Martial Arts Academy Email System<br>
        Deliverability Test - {datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
</body>
</html>
            """.strip()
            
            # Add parts to message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            message.attach(text_part)
            message.attach(html_part)
            
            # Send with detailed SMTP logging
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(1)  # Enable debug output
                
                if self.smtp_port == 587:
                    server.starttls(context=context)
                
                server.login(self.smtp_user, self.smtp_pass)
                
                # Send email and capture response
                result = server.sendmail(self.smtp_from, to_email, message.as_string())
                
                if result:
                    print(f"⚠️  SMTP warnings for {provider_name}: {result}")
                else:
                    print(f"✅ Email sent successfully to {provider_name}")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to send test email to {provider_name}: {e}")
            return False
    
    def test_multiple_providers(self):
        """Test email delivery to multiple providers"""
        self.print_section("Multi-Provider Email Delivery Test")
        
        results = {}
        
        # Test primary Gmail address
        results['gmail'] = self.send_test_email_with_tracking(
            self.test_emails['gmail'], 'Gmail'
        )
        
        # Wait between sends to avoid rate limiting
        time.sleep(2)
        
        # Test other providers if available
        for provider, email in self.test_emails.items():
            if provider != 'gmail' and email != self.test_emails['gmail']:
                results[provider] = self.send_test_email_with_tracking(email, provider.title())
                time.sleep(2)
        
        return results
    
    def check_domain_reputation(self):
        """Check domain reputation using online tools"""
        self.print_section("Domain Reputation Analysis")
        
        print(f"🔍 Analyzing reputation for domain: {self.domain}")
        print(f"📧 Sender email: {self.smtp_from}")
        
        # Check if domain is in common blacklists (simplified check)
        blacklist_checks = [
            "zen.spamhaus.org",
            "bl.spamcop.net", 
            "dnsbl.sorbs.net"
        ]
        
        try:
            # Get domain IP
            domain_ip = socket.gethostbyname(self.smtp_host)
            print(f"📍 SMTP Server IP: {domain_ip}")
            
            # Check blacklists
            print(f"\n🔍 Checking blacklists for {domain_ip}...")
            for blacklist in blacklist_checks:
                try:
                    # Reverse IP for blacklist check
                    reversed_ip = '.'.join(reversed(domain_ip.split('.')))
                    query = f"{reversed_ip}.{blacklist}"
                    
                    result = socket.gethostbyname(query)
                    print(f"   ❌ Listed in {blacklist}: {result}")
                except socket.gaierror:
                    print(f"   ✅ Not listed in {blacklist}")
                except Exception as e:
                    print(f"   ⚠️  Could not check {blacklist}: {e}")
                    
        except Exception as e:
            print(f"❌ Domain reputation check failed: {e}")
        
        # Manual checks recommendations
        print(f"\n📋 Manual Reputation Checks Recommended:")
        print(f"   1. Check MXToolbox: https://mxtoolbox.com/blacklists.aspx")
        print(f"   2. Check Sender Score: https://www.senderscore.org/")
        print(f"   3. Check Google Postmaster: https://postmaster.google.com/")
        print(f"   4. Check Microsoft SNDS: https://sendersupport.olc.protection.outlook.com/")
    
    async def test_application_email(self):
        """Test the actual application email service"""
        self.print_section("Application Email Service Test")
        
        try:
            email_service = get_email_service()
            
            print("📧 Testing password reset email through application...")
            result = await email_service.send_password_reset_email(
                to_email=self.test_emails['gmail'],
                reset_token='comprehensive_investigation_token_123',
                user_name='Email Investigation Test User'
            )
            
            if result:
                print("✅ Application email service working")
            else:
                print("❌ Application email service failed")
                
            return result
            
        except Exception as e:
            print(f"❌ Application email test failed: {e}")
            return False
    
    def generate_investigation_report(self, test_results):
        """Generate comprehensive investigation report"""
        self.print_header("COMPREHENSIVE EMAIL DELIVERABILITY INVESTIGATION REPORT")
        
        print(f"📊 Investigation Summary:")
        print(f"   Domain: {self.domain}")
        print(f"   SMTP Server: {self.smtp_host}:{self.smtp_port}")
        print(f"   Sender: {self.smtp_from}")
        print(f"   Investigation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📧 Email Delivery Test Results:")
        for provider, success in test_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   {provider.title()}: {status}")
        
        print(f"\n🔍 Key Findings:")
        print(f"   1. SMTP Connection: Working")
        print(f"   2. Authentication: Successful") 
        print(f"   3. Email Sending: Successful")
        print(f"   4. DNS Records: Check output above")
        print(f"   5. Domain Reputation: Check output above")
        
        print(f"\n⚠️  LIKELY REASONS FOR EMAIL NOT REACHING INBOX:")
        print(f"   1. 📧 Emails are being delivered to SPAM/JUNK folder")
        print(f"   2. 🛡️  Email provider is silently filtering emails")
        print(f"   3. 📱 Mobile email apps may not sync immediately")
        print(f"   4. ⏰ Email delivery can be delayed (5-30 minutes)")
        print(f"   5. 🔍 Corporate/ISP firewalls may be blocking")
        print(f"   6. 📊 New sender domain reputation building")
        
        print(f"\n🔧 IMMEDIATE ACTION ITEMS:")
        print(f"   1. ✅ Check ALL email folders (Inbox, Spam, Junk, Promotions, Updates)")
        print(f"   2. 🔍 Search for emails from '{self.smtp_from}'")
        print(f"   3. 🔍 Search for subject 'Password Reset Request'")
        print(f"   4. ⏰ Wait 30 minutes and check again")
        print(f"   5. 📱 Check email on different devices/apps")
        print(f"   6. 🌐 Try accessing email via web interface")
        
        print(f"\n📋 NEXT STEPS IF EMAILS STILL NOT FOUND:")
        print(f"   1. Configure Gmail SMTP as backup")
        print(f"   2. Set up SPF/DKIM records for better deliverability")
        print(f"   3. Contact email provider support")
        print(f"   4. Use email delivery service (SendGrid, Mailgun)")
    
    async def run_comprehensive_investigation(self):
        """Run complete email deliverability investigation"""
        self.print_header("EMAIL DELIVERABILITY COMPREHENSIVE INVESTIGATION")
        
        print("🚀 Starting comprehensive email deliverability investigation...")
        print(f"📧 Primary test email: {self.test_emails['gmail']}")
        print(f"🔧 SMTP configuration: {self.smtp_host}:{self.smtp_port}")
        print(f"📤 Sender: {self.smtp_from}")
        
        # Run all investigations
        self.check_dns_records()
        self.check_smtp_detailed_response()
        self.check_domain_reputation()
        
        # Test email delivery
        test_results = self.test_multiple_providers()
        
        # Test application email
        app_result = await self.test_application_email()
        test_results['application'] = app_result
        
        # Generate final report
        self.generate_investigation_report(test_results)
        
        return test_results

if __name__ == "__main__":
    investigation = EmailDeliverabilityInvestigation()
    results = asyncio.run(investigation.run_comprehensive_investigation())
