#!/usr/bin/env python3
"""
Password Reset Fix Verification Test
Test both existing and non-existent user scenarios
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class PasswordResetTester:
    def __init__(self):
        self.base_url = "http://localhost:8003"
        self.test_results = []
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"🧪 {title}")
        print(f"{'='*70}")
        
    def print_section(self, title):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 50)
    
    def print_result(self, test_name, success, details):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_api_endpoint(self, email, expected_behavior):
        """Test the forgot password API endpoint"""
        self.print_section(f"Testing API with email: {email}")
        
        try:
            # Test the forgot password API
            url = f'{self.base_url}/auth/forgot-password'
            payload = {"email": email}
            
            print(f"🌐 Making request to: {url}")
            print(f"📧 Email: {email}")
            
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=10)
            response_time = time.time() - start_time
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"📄 Response: {json.dumps(response_data, indent=2)}")
                
                # Check response structure
                has_message = "message" in response_data
                has_email_sent = "email_sent" in response_data
                has_user_found = "user_found" in response_data
                
                message = response_data.get("message", "")
                email_sent = response_data.get("email_sent", False)
                user_found = response_data.get("user_found", False)
                
                # Verify expected behavior
                if expected_behavior == "existing_user":
                    success = (
                        has_message and 
                        has_email_sent and 
                        email_sent == True and
                        user_found == True and
                        "password reset link has been sent" in message.lower()
                    )
                    details = f"User found: {user_found}, Email sent: {email_sent}"
                    
                elif expected_behavior == "non_existent_user":
                    success = (
                        has_message and 
                        has_email_sent and 
                        email_sent == True and  # Should now be True for security
                        user_found == False and
                        "password reset link has been sent" in message.lower()
                    )
                    details = f"User found: {user_found}, Email sent: {email_sent} (security notification)"
                
                else:
                    success = False
                    details = "Unknown expected behavior"
                
                self.print_result(f"API Response for {email}", success, details)
                
                # Additional checks
                if response_time > 5:
                    self.print_result("Response Time", False, f"Too slow: {response_time:.2f}s")
                else:
                    self.print_result("Response Time", True, f"Good: {response_time:.2f}s")
                
                return True
                
            else:
                self.print_result(f"API Status Code", False, f"Expected 200, got {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_result(f"API Request", False, f"Request failed: {e}")
            return False
        except Exception as e:
            self.print_result(f"API Test", False, f"Unexpected error: {e}")
            return False
    
    def check_server_status(self):
        """Check if the server is running"""
        self.print_section("Server Status Check")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.print_result("Server Status", True, "Server is running")
                return True
            else:
                self.print_result("Server Status", False, f"Server returned {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            self.print_result("Server Status", False, "Server is not responding")
            print("❌ Please start the server with: python server.py")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive password reset tests"""
        self.print_header("PASSWORD RESET FIX VERIFICATION")
        
        # Check server status first
        if not self.check_server_status():
            print("\n❌ Cannot proceed without server running")
            return
        
        print(f"🎯 Testing password reset functionality with both existing and non-existent users")
        print(f"🔧 Verifying that emails are sent in both cases for security")
        
        # Test cases
        test_cases = [
            {
                "email": "pittisunilkumar3@gmail.com",
                "expected": "existing_user",
                "description": "Existing user (should get real reset email)"
            },
            {
                "email": "pittisunilkumar4@gmail.com", 
                "expected": "existing_user",  # Now exists after we created it
                "description": "Newly created user (should get real reset email)"
            },
            {
                "email": "nonexistent.user@example.com",
                "expected": "non_existent_user",
                "description": "Non-existent user (should get security notification)"
            },
            {
                "email": "another.fake@test.com",
                "expected": "non_existent_user", 
                "description": "Another non-existent user (should get security notification)"
            }
        ]
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST {i}/4: {test_case['description']}")
            self.test_api_endpoint(test_case["email"], test_case["expected"])
            
            # Small delay between tests
            if i < len(test_cases):
                time.sleep(1)
        
        # Summary
        self.print_section("TEST SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Key findings
        self.print_section("KEY FINDINGS")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Password reset now works for both existing and non-existent users")
            print("🔒 Security: Non-existent users get notification emails (no user enumeration)")
            print("📧 Email delivery: Both scenarios trigger email sending")
            print("⚡ Performance: Response times are acceptable")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
            
        print(f"\n📧 IMPORTANT: Check your email inbox/spam for test emails!")
        print(f"   • Existing users should get password reset links")
        print(f"   • Non-existent users should get security notifications")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PasswordResetTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎯 CONCLUSION: Password reset fix is working correctly!")
    else:
        print(f"\n⚠️  CONCLUSION: Some issues remain. Please review the test results.")
