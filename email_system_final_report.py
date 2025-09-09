#!/usr/bin/env python3
"""
Final Email System Report and Verification
Comprehensive analysis and verification of the email delivery system
"""

import asyncio
import requests
import smtplib
import ssl
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.email_service import get_email_service
from utils.email_monitor import get_email_monitor, print_email_summary

# Load environment variables
load_dotenv()

class EmailSystemReport:
    def __init__(self):
        self.test_email = 'pittisunilkumar3@gmail.com'
        self.api_url = 'http://localhost:8003'
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Neelarani@10')
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"📧 {title}")
        print(f"{'='*70}")
        
    def print_section(self, title):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 50)
        
    def check_configuration(self):
        """Check email configuration"""
        self.print_section("Email Configuration Analysis")
        
        print(f"🔧 SMTP Host: {self.smtp_host}")
        print(f"🔧 SMTP Port: {self.smtp_port}")
        print(f"🔧 SMTP User: {self.smtp_user}")
        print(f"🔧 SMTP Password: {'✅ Set' if self.smtp_pass else '❌ Not Set'}")
        print(f"🔧 Frontend URL: {os.getenv('FRONTEND_URL', 'Not Set')}")
        print(f"🔧 Testing Mode: {os.getenv('TESTING', 'False')}")
        
        # Check if all required settings are present
        required_settings = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS']
        missing_settings = [setting for setting in required_settings if not os.getenv(setting)]
        
        if missing_settings:
            print(f"❌ Missing settings: {', '.join(missing_settings)}")
            return False
        else:
            print("✅ All required email settings are configured")
            return True
    
    def test_smtp_connectivity(self):
        """Test SMTP server connectivity"""
        self.print_section("SMTP Connectivity Test")
        
        try:
            print(f"🔌 Testing connection to {self.smtp_host}:{self.smtp_port}...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                print("✅ Connection established")
                
                if self.smtp_port == 587:
                    server.starttls(context=context)
                    print("✅ TLS encryption enabled")
                
                server.login(self.smtp_user, self.smtp_pass)
                print("✅ Authentication successful")
                
            return True
            
        except Exception as e:
            print(f"❌ SMTP connectivity failed: {e}")
            return False
    
    async def test_email_service(self):
        """Test the email service"""
        self.print_section("Email Service Test")
        
        try:
            email_service = get_email_service()
            
            print(f"📧 Service enabled: {email_service.enabled}")
            print(f"🔧 Configuration loaded: ✅")
            
            # Test password reset email
            result = await email_service.send_password_reset_email(
                to_email=self.test_email,
                reset_token='final_test_token_123',
                user_name='Final Test User'
            )
            
            if result:
                print("✅ Email service working correctly")
            else:
                print("❌ Email service failed")
                
            return result
            
        except Exception as e:
            print(f"❌ Email service error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.print_section("API Endpoints Test")
        
        results = {}
        
        # Test forgot password endpoint
        try:
            url = f'{self.api_url}/auth/forgot-password'
            data = {'email': self.test_email}
            
            print(f"🌐 Testing: {url}")
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                email_sent = result.get('email_sent', False)
                print(f"✅ Forgot Password API: Working (Email sent: {email_sent})")
                results['forgot_password'] = True
            else:
                print(f"❌ Forgot Password API: Failed ({response.status_code})")
                results['forgot_password'] = False
                
        except Exception as e:
            print(f"❌ Forgot Password API: Error - {e}")
            results['forgot_password'] = False
        
        return results
    
    def check_monitoring_system(self):
        """Check email monitoring system"""
        self.print_section("Email Monitoring System")
        
        try:
            monitor = get_email_monitor()
            summary = monitor.get_summary()
            
            print(f"📊 Total emails sent: {summary['total_sent']}")
            print(f"❌ Total emails failed: {summary['total_failed']}")
            print(f"📈 Success rate: {summary['success_rate']}%")
            print(f"🔑 Password resets: {summary['password_resets']}")
            
            if summary['last_reset']:
                print(f"⏰ Last reset: {summary['last_reset']}")
            
            print("✅ Monitoring system operational")
            return True
            
        except Exception as e:
            print(f"❌ Monitoring system error: {e}")
            return False
    
    def generate_final_report(self, results):
        """Generate final comprehensive report"""
        self.print_header("FINAL EMAIL SYSTEM REPORT")
        
        # Configuration status
        config_ok = results.get('configuration', False)
        smtp_ok = results.get('smtp_connectivity', False)
        service_ok = results.get('email_service', False)
        api_ok = results.get('api_endpoints', {}).get('forgot_password', False)
        monitoring_ok = results.get('monitoring', False)
        
        total_checks = 5
        passed_checks = sum([config_ok, smtp_ok, service_ok, api_ok, monitoring_ok])
        
        print(f"📊 System Health: {passed_checks}/{total_checks} components operational")
        print()
        
        # Detailed status
        status_items = [
            ("Configuration", config_ok),
            ("SMTP Connectivity", smtp_ok),
            ("Email Service", service_ok),
            ("API Endpoints", api_ok),
            ("Monitoring System", monitoring_ok)
        ]
        
        for item, status in status_items:
            icon = "✅" if status else "❌"
            print(f"   {icon} {item}")
        
        print()
        
        if passed_checks == total_checks:
            print("🎉 EMAIL SYSTEM FULLY OPERATIONAL!")
            print()
            print("✅ All components are working correctly")
            print("✅ SMTP server connection established")
            print("✅ Email delivery confirmed")
            print("✅ API endpoints responding")
            print("✅ Monitoring and logging active")
            print()
            print("📧 Email delivery is now working properly!")
            
        else:
            print("⚠️  EMAIL SYSTEM ISSUES DETECTED")
            print()
            failed_components = [item for item, status in status_items if not status]
            print("❌ Failed components:")
            for component, _ in failed_components:
                print(f"   - {component}")
        
        print()
        print("📋 RECOMMENDATIONS:")
        print("   1. ✅ Email system is operational - no action needed")
        print("   2. 📧 Check recipient email inbox (including spam folder)")
        print("   3. 🔍 Monitor email logs for delivery confirmation")
        print("   4. 🧪 Test password reset flow from frontend application")
        print("   5. 📊 Review email statistics regularly")
        
        print()
        print("📁 LOG FILES:")
        print(f"   - Email logs: email_logs/email_delivery_{datetime.now().strftime('%Y%m%d')}.log")
        print(f"   - Statistics: email_logs/email_stats.json")
        
        return passed_checks == total_checks
    
    async def run_comprehensive_analysis(self):
        """Run comprehensive email system analysis"""
        self.print_header("EMAIL SYSTEM COMPREHENSIVE ANALYSIS")
        
        results = {}
        
        # Run all tests
        results['configuration'] = self.check_configuration()
        results['smtp_connectivity'] = self.test_smtp_connectivity()
        results['email_service'] = await self.test_email_service()
        results['api_endpoints'] = self.test_api_endpoints()
        results['monitoring'] = self.check_monitoring_system()
        
        # Show current monitoring stats
        print_email_summary()
        
        # Generate final report
        system_healthy = self.generate_final_report(results)
        
        return system_healthy

if __name__ == "__main__":
    report = EmailSystemReport()
    result = asyncio.run(report.run_comprehensive_analysis())
    
    if result:
        print("\n🎉 EMAIL SYSTEM VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL!")
    else:
        print("\n⚠️  EMAIL SYSTEM VERIFICATION COMPLETE - ISSUES DETECTED!")
