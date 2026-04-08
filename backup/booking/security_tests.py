"""
Security tests to validate input sanitization and protection against attacks
"""
import re
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from booking.security_utils import SecurityValidator

Client = get_user_model()

class SecurityTests(TestCase):
    """Test security measures against various attack vectors"""
    
    def setUp(self):
        self.client = Client()
        self.test_email = 'test@example.com'
        self.test_password = 'SecureTest123!'
    
    def test_sql_injection_detection(self):
        """Test SQL injection patterns are detected"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' --",
            "' UNION SELECT * FROM users --",
            "'; DELETE FROM clients; --",
            "' OR 'x'='x",
            "1' OR '1'='1' /*",
        ]
        
        for attempt in sql_injection_attempts:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_sql_injection(attempt)
    
    def test_xss_prevention(self):
        """Test XSS patterns are detected and sanitized"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<body onload=alert('xss')>",
            "vbscript:msgbox('xss')",
        ]
        
        for attempt in xss_attempts:
            with self.assertRaises(ValidationError):
                SecurityValidator.sanitize_input(attempt)
    
    def test_email_validation_security(self):
        """Test email validation against injection attempts"""
        malicious_emails = [
            "test@example.com'; DROP TABLE users; --",
            "test@example.com' OR '1'='1",
            "test@example.com<script>alert('xss')</script>",
            "test@example.com\x00null",
            "test@example.com\r\nBcc: victim@example.com",
        ]
        
        for email in malicious_emails:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_email_security(email)
    
    def test_name_field_validation(self):
        """Test name field validation against injection"""
        malicious_names = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "test\x00null",
            "test\r\nBcc: victim@example.com",
        ]
        
        for name in malicious_names:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_name_field(name)
    
    def test_phone_number_validation(self):
        """Test phone number validation against injection"""
        malicious_phones = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "1234567890' OR '1'='1",
        ]
        
        for phone in malicious_phones:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_phone_number(phone)
    
    def test_password_security(self):
        """Test password validation against common passwords and injection"""
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "admin",
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
        ]
        
        for password in weak_passwords:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_password_security(password)
    
    def test_otp_validation(self):
        """Test OTP validation against injection"""
        malicious_otps = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "1234567",  # Too long
            "12345",    # Too short
            "abcdef",   # Non-numeric
        ]
        
        for otp in malicious_otps:
            with self.assertRaises(ValidationError):
                SecurityValidator.validate_otp(otp)
    
    def test_form_data_sanitization(self):
        """Test form data sanitization"""
        malicious_data = {
            'first_name': "<script>alert('xss')</script>",
            'last_name': "'; DROP TABLE users; --",
            'email': "test@example.com' OR '1'='1",
            'password': "admin",
        }
        
        with self.assertRaises(ValidationError):
            SecurityValidator.sanitize_form_data(malicious_data)
    
    def test_xml_security(self):
        """Test XML parsing security against XXE attacks"""
        malicious_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>"""
        
        with self.assertRaises(ValidationError):
            SecurityValidator.secure_xml_parser(malicious_xml)
    
    def test_login_view_security(self):
        """Test login view against injection attacks"""
        malicious_login_data = {
            'email': "test@example.com' OR '1'='1",
            'password': "'; DROP TABLE users; --",
        }
        
        response = self.client.post(reverse('login'), malicious_login_data)
        self.assertEqual(response.status_code, 200)
        # Should not redirect to dashboard on malicious input
        self.assertNotEqual(response.status_code, 302)
    
    def test_signup_view_security(self):
        """Test signup view against injection attacks"""
        malicious_signup_data = {
            'first_name': "<script>alert('xss')</script>",
            'last_name': "'; DROP TABLE users; --",
            'email': "test@example.com' OR '1'='1",
            'password': "admin",
            'confirm_password': "admin",
        }
        
        response = self.client.post(reverse('signup'), malicious_signup_data)
        self.assertEqual(response.status_code, 200)
        # Should not create user with malicious data
        self.assertFalse(Client.objects.filter(email__contains="OR '1'='1").exists())
    
    def test_otp_view_security(self):
        """Test OTP verification view against injection"""
        session = self.client.session
        session['2fa_user_email'] = 'test@example.com'
        session['2fa_login_method'] = 'email'
        session.save()
        
        malicious_otp_data = {
            'otp': "'; DROP TABLE users; --",
        }
        
        response = self.client.post(reverse('two_factor_verify'), malicious_otp_data)
        self.assertEqual(response.status_code, 200)
        # Should not authenticate with malicious OTP
        self.assertNotEqual(response.status_code, 302)

class SecurityHeadersTest(TestCase):
    """Test security headers are properly set"""
    
    def test_security_headers(self):
        """Test that security headers are present in responses"""
        response = self.client.get(reverse('login'))
        
        # Check for security headers
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        
        self.assertIn('Content-Security-Policy', response)

# Manual security testing functions
def run_security_tests():
    """Run all security tests manually"""
    print("Running Security Tests...")
    
    # Test SQL Injection Detection
    print("\n1. Testing SQL Injection Detection...")
    sql_attempts = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM users --",
    ]
    
    for attempt in sql_attempts:
        try:
            SecurityValidator.validate_sql_injection(attempt)
            print(f"❌ FAILED: SQL injection not detected: {attempt}")
        except ValidationError:
            print(f"✅ PASSED: SQL injection detected: {attempt}")
    
    # Test XSS Prevention
    print("\n2. Testing XSS Prevention...")
    xss_attempts = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
    ]
    
    for attempt in xss_attempts:
        try:
            SecurityValidator.sanitize_input(attempt)
            print(f"❌ FAILED: XSS not detected: {attempt}")
        except ValidationError:
            print(f"✅ PASSED: XSS detected: {attempt}")
    
    # Test Email Security
    print("\n3. Testing Email Security...")
    malicious_emails = [
        "test@example.com'; DROP TABLE users; --",
        "test@example.com<script>alert('xss')</script>",
    ]
    
    for email in malicious_emails:
        try:
            SecurityValidator.validate_email_security(email)
            print(f"❌ FAILED: Malicious email not detected: {email}")
        except ValidationError:
            print(f"✅ PASSED: Malicious email detected: {email}")
    
    print("\nSecurity tests completed!")

if __name__ == '__main__':
    run_security_tests()
