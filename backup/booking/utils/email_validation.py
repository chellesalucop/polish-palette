"""
Email Validation & Security Utility
High-integrity email validation with RFC compliance and security features
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings


class EmailValidator:
    """
    Utility class for validating and securing email addresses
    """
    
    # List of common disposable email domains
    DISPOSABLE_DOMAINS = [
        '10minutemail.com', '20minutemail.com', 'guerrillamail.com', 'mailinator.com',
        'temp-mail.org', 'throwaway.email', 'yopmail.com', 'maildrop.cc',
        'tempmail.org', '10mail.org', 'mailcatch.com', 'zippymail.info',
        'sharklasers.com', 'grr.la', 'spamgourmet.com', 'mailnesia.com',
        'tempmail.de', 'deadaddress.com', 'mailnull.com', 'jetable.org',
        'nospam.ze.tc', 'nospam4.us', 'trashmail.io', 'tempmail.org',
        'mail2rss.com', 'spambox.me', 'tempmail.info', 'yopmail.net',
        'coolmail.com', 'mailtemp.org', 'throwaway.email', 'tempmail.dev',
        'temp-email.info', 'tempmail.plus', 'fakemail.fr', 'tempmail.app',
        'temp-email.org', 'tempmail.io', 'emailtemp.org', 'tempemail.net',
        'tempmail.co', 'tempmail.us', 'tempmail.email', 'tempmail.link',
        'tempmail.site', 'tempmail.space', 'tempmail.world', 'tempmail.online',
        'tempmail.app', 'tempmail.live', 'tempmail.store', 'tempmail.tech',
        'tempmail.cloud', 'tempmail.solutions', 'tempmail.services', 'tempmail.systems',
        'tempmail.platform', 'tempmail.tools', 'tempmail.works', 'tempmail.zone',
        'tempmail.network', 'tempmail.center', 'tempmail.space', 'tempmail.host',
        'tempmail.server', 'tempmail.site', 'tempmail.web', 'tempmail.tech',
        'tempmail.pro', 'tempmail.xyz', 'tempmail.club', 'tempmail.fun',
        'tempmail.life', 'tempmail.co', 'tempmail.io', 'tempmail.email',
        'tempmail.online', 'tempmail.website', 'tempmail.app', 'tempmail.dev',
        'tempmail.test', 'tempmail.demo', 'tempmail.sample', 'tempmail.example',
        'tempmail.fake', 'tempmail.dummy', 'tempmail.mock', 'tempmail.virtual',
        'tempmail.temporary', 'tempmail.short', 'tempmail.quick', 'tempmail.fast',
        'tempmail.easy', 'tempmail.simple', 'tempmail.basic', 'tempmail.free',
        'tempmail.premium', 'tempmail.pro', 'tempmail.plus', 'tempmail.gold',
        'tempmail.silver', 'tempmail.bronze', 'tempmail.platinum', 'tempmail.diamond',
        'tempmail.vip', 'tempmail.special', 'tempmail.exclusive', 'tempmail.limited',
        'tempmail.unlimited', 'tempmail.infinity', 'tempmail.eternal', 'tempmail.forever',
        'tempmail.always', 'tempmail.never', 'tempmail.constant', 'tempmail.permanent',
        'tempmail.temporary', 'tempmail.moment', 'tempmail.instant', 'tempmail.now',
        'tempmail.today', 'tempmail.tomorrow', 'tempmail.week', 'tempmail.month',
        'tempmail.year', 'tempmail.decade', 'tempmail.century', 'tempmail.millennium',
    ]
    
    # Common email providers that might be suspicious
    SUSPICIOUS_DOMAINS = [
        'qq.com', '163.com', '126.com', 'sina.com',  # Chinese providers
        'mail.ru', 'yandex.ru', 'list.ru',          # Russian providers
        'web.de', 'gmx.de', 't-online.de',          # German providers
    ]
    
    @staticmethod
    def normalize_email(email):
        """
        Normalize email address for consistent storage
        
        Args:
            email (str): Raw email address
            
        Returns:
            str: Normalized email address (lowercase, stripped)
        """
        if not email:
            return ''
        
        # Convert to lowercase and strip whitespace
        email = str(email).lower().strip()
        
        # Remove any leading/trailing quotes
        if email.startswith('"') and email.endswith('"'):
            email = email[1:-1]
        
        return email
    
    @staticmethod
    def validate_email_format(email):
        """
        Validate email format with RFC compliance
        
        Args:
            email (str): Email address to validate
            
        Returns:
            str: Normalized email address
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email:
            raise ValidationError('Email address is required')
        
        # Normalize first
        email = EmailValidator.normalize_email(email)
        
        # Basic format check
        if '@' not in email:
            raise ValidationError('Email must contain @ symbol')
        
        # Split into local and domain parts
        local, domain = email.rsplit('@', 1)
        
        # Validate local part
        if not local:
            raise ValidationError('Email local part cannot be empty')
        
        if len(local) > 64:
            raise ValidationError('Email local part is too long (max 64 characters)')
        
        # Check for consecutive dots
        if '..' in local:
            raise ValidationError('Email local part cannot contain consecutive dots')
        
        # Check for leading/trailing dots
        if local.startswith('.') or local.endswith('.'):
            raise ValidationError('Email local part cannot start or end with a dot')
        
        # Validate domain part
        if not domain:
            raise ValidationError('Email domain part cannot be empty')
        
        if len(domain) > 253:
            raise ValidationError('Email domain is too long (max 253 characters)')
        
        # Check for valid domain format
        if not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', domain):
            raise ValidationError('Email domain format is invalid')
        
        # Use Django's built-in validator for comprehensive checks
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValidationError(f'Invalid email format: {e.messages[0] if e.messages else "Unknown error"}')
        
        return email
    
    @staticmethod
    def is_disposable_email(email):
        """
        Check if email is from a disposable email service
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if disposable, False otherwise
        """
        if not email:
            return False
        
        domain = email.split('@')[-1].lower()
        return domain in EmailValidator.DISPOSABLE_DOMAINS
    
    @staticmethod
    def is_suspicious_domain(email):
        """
        Check if email is from a potentially suspicious domain
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if suspicious, False otherwise
        """
        if not email:
            return False
        
        domain = email.split('@')[-1].lower()
        return domain in EmailValidator.SUSPICIOUS_DOMAINS
    
    @staticmethod
    def validate_email_security(email):
        """
        Comprehensive email validation with security checks
        
        Args:
            email (str): Email address to validate
            
        Returns:
            str: Normalized email address
            
        Raises:
            ValidationError: If email fails any validation
        """
        # Basic format validation
        email = EmailValidator.validate_email_format(email)
        
        # Check for disposable email
        if EmailValidator.is_disposable_email(email):
            raise ValidationError('Disposable email addresses are not allowed. Please use a permanent email address.')
        
        # Check for suspicious domains (warning only)
        if EmailValidator.is_suspicious_domain(email):
            # Log this for security monitoring but don't block
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Suspicious domain registration attempt: {email}')
        
        return email
    
    @staticmethod
    def get_email_domain(email):
        """
        Extract domain from email address
        
        Args:
            email (str): Email address
            
        Returns:
            str: Domain part of email
        """
        if not email or '@' not in email:
            return ''
        
        return email.split('@')[-1].lower()
    
    @staticmethod
    def get_email_local_part(email):
        """
        Extract local part from email address
        
        Args:
            email (str): Email address
            
        Returns:
            str: Local part of email
        """
        if not email or '@' not in email:
            return ''
        
        return email.split('@')[0].lower()
    
    @staticmethod
    def is_common_provider(email):
        """
        Check if email is from a common email provider
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if common provider, False otherwise
        """
        if not email:
            return False
        
        domain = EmailValidator.get_email_domain(email)
        common_providers = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'aol.com', 'icloud.com', 'protonmail.com', 'tutanota.com',
            'zoho.com', 'yandex.com', 'mail.com', 'gmx.com'
        ]
        
        return domain in common_providers
