"""
Security utilities for input validation and sanitization
"""
import re
import html
import logging
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.conf import settings
import xml.etree.ElementTree as ET
from xml.dom import minidom

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Centralized security validation class"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(--|#|\/\*|\*\/)",
        r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT|ONLOAD|ONERROR)\b)",
        r"(<[^>]*>)",
        r"(\b(WAITFOR|DELAY|BENCHMARK|SLEEP)\b)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"onchange\s*=",
        r"onsubmit\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"<img[^>]*onerror[^>]*>",
        r"<svg[^>]*>.*?</svg>",
    ]
    
    @classmethod
    def sanitize_input(cls, input_data):
        """
        Sanitize input data to prevent XSS and injection attacks
        """
        if not input_data:
            return input_data
            
        if isinstance(input_data, str):
            # Check for XSS patterns first (before HTML escaping)
            for pattern in cls.XSS_PATTERNS:
                if re.search(pattern, input_data, re.IGNORECASE | re.DOTALL):
                    logger.warning(f"XSS attempt detected: {input_data}")
                    raise ValidationError("Invalid input detected")
            
            # HTML escape
            sanitized = html.escape(input_data)
            
            # Remove any remaining HTML tags after escaping
            sanitized = strip_tags(sanitized)
            
            return sanitized.strip()
        
        return input_data
    
    @classmethod
    def validate_sql_injection(cls, input_data):
        """
        Check for SQL injection patterns
        """
        if not input_data:
            return
            
        if isinstance(input_data, str):
            for pattern in cls.SQL_INJECTION_PATTERNS:
                if re.search(pattern, input_data, re.IGNORECASE):
                    logger.warning(f"SQL injection attempt detected: {input_data}")
                    raise ValidationError("Invalid characters detected in input")
    
    @classmethod
    def validate_email_security(cls, email):
        """
        Enhanced email validation with security checks
        """
        if not email:
            return
            
        # Basic email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r"'",
            r'"',
            r";",
            r"--",
            r"/\*",
            r"\*/",
            r"xp_",
            r"sp_",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                logger.warning(f"Dangerous pattern in email: {email}")
                raise ValidationError("Invalid email format")
        
        # Length check
        if len(email) > 254:
            raise ValidationError("Email address too long")
    
    @classmethod
    def validate_name_field(cls, name):
        """
        Validate name fields (first name, last name)
        """
        if not name:
            return
            
        # Allow only letters, spaces, hyphens, and apostrophes
        name_pattern = r"^[a-zA-Z\s\-']+$"
        if not re.match(name_pattern, name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes")
        
        # Length checks
        if len(name) < 2 or len(name) > 50:
            raise ValidationError("Name must be between 2 and 50 characters")
        
        # Consecutive Limit: No character more than 2 times consecutively
        if re.search(r'(.)\1{2,}', name, re.IGNORECASE):
            raise ValidationError("A letter cannot appear more than 2 times in a row.")
        
        # Global Frequency: For strings > 10 chars, no character > 40% of length
        letters_only = re.sub(r'\s', '', name).lower()
        if len(letters_only) > 10:
            from collections import Counter
            counts = Counter(letters_only)
            for char, count in counts.items():
                if count / len(letters_only) > 0.4:
                    raise ValidationError("A single letter appears too frequently in this name.")
        
        # Consonant Cluster Limit: Max 4 consecutive consonants
        if re.search(r'[^aeiou\s]{5,}', name, re.IGNORECASE):
            raise ValidationError("Too many consecutive consonants.")
        
        # Prevent script tags and other dangerous content
        cls.validate_sql_injection(name)
        cls.sanitize_input(name)
    
    @classmethod
    def normalize_name(cls, name):
        """
        Normalize name: trim leading/trailing whitespace and collapse multiple internal spaces.
        Returns empty string for None/whitespace-only input.
        """
        if not name:
            return ''
        normalized = name.strip()
        normalized = re.sub(r'\s{2,}', ' ', normalized)
        return normalized
    
    @classmethod
    def validate_phone_number(cls, phone):
        """
        Validate phone number with security checks
        """
        if not phone:
            return
            
        # Phone number pattern
        phone_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError("Invalid phone number format")
        
        # Check for dangerous patterns
        cls.validate_sql_injection(phone)
    
    @classmethod
    def validate_password_security(cls, password):
        """
        Enhanced password validation with security checks
        """
        if not password:
            return
            
        # Length check
        if len(password) < 8 or len(password) > 128:
            raise ValidationError("Password must be between 8 and 128 characters")
        
        # Check for common passwords (basic check)
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in common_passwords:
            raise ValidationError("Please choose a stronger password")
        
        # Check for SQL injection patterns in password
        cls.validate_sql_injection(password)
    
    @classmethod
    def secure_xml_parser(cls, xml_string):
        """
        Secure XML parsing to prevent XXE attacks
        """
        try:
            # Disable DTD and external entities to prevent XXE
            parser = ET.XMLParser(resolve_entities=False)
            
            # Parse the XML
            root = ET.fromstring(xml_string, parser=parser)
            
            return root
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValidationError("Invalid XML format")
        except Exception as e:
            logger.error(f"XML security error: {e}")
            raise ValidationError("XML security violation detected")
    
    @classmethod
    def validate_otp(cls, otp):
        """
        Validate OTP input
        """
        if not otp:
            return
            
        # OTP should be exactly 6 digits
        if not re.match(r'^\d{6}$', otp):
            raise ValidationError("Invalid OTP format")
        
        # Check for injection attempts
        cls.validate_sql_injection(otp)
    
    @classmethod
    def sanitize_form_data(cls, form_data):
        """
        Sanitize all form data
        """
        sanitized_data = {}
        
        for key, value in form_data.items():
            if isinstance(value, str):
                # First validate against injection
                cls.validate_sql_injection(value)
                # Then sanitize
                sanitized_data[key] = cls.sanitize_input(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        cls.validate_sql_injection(item)
                        sanitized_list.append(cls.sanitize_input(item))
                    else:
                        sanitized_list.append(item)
                sanitized_data[key] = sanitized_list
            else:
                sanitized_data[key] = value
        
        return sanitized_data

class SecurityMiddleware:
    """Custom middleware for additional security checks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://res.cloudinary.com; "
            "connect-src 'self' https://cdn.jsdelivr.net; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
