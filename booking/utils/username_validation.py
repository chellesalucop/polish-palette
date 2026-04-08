"""
Username Validation & Security Utility
URL-friendly identifier validation with injection attack prevention
"""

import re
from django.core.exceptions import ValidationError


class UsernameValidator:
    """
    Utility class for validating and securing usernames
    """
    
    # Reserved usernames that shouldn't be allowed
    RESERVED_USERNAMES = [
        'admin', 'administrator', 'root', 'staff', 'moderator', 'support', 'help',
        'system', 'api', 'www', 'mail', 'email', 'info', 'contact', 'about',
        'terms', 'privacy', 'policy', 'legal', 'copyright', 'trademark',
        'login', 'logout', 'register', 'signup', 'signin', 'signout',
        'profile', 'account', 'settings', 'dashboard', 'home', 'index',
        'search', 'browse', 'explore', 'discover', 'trending', 'popular',
        'new', 'latest', 'recent', 'featured', 'recommended', 'suggested',
        'nailtech', 'appointment', 'booking', 'service', 'artist', 'client',
        'user', 'users', 'member', 'members', 'guest', 'anonymous',
        'null', 'undefined', 'test', 'demo', 'sample', 'example', 'placeholder',
        'bot', 'robot', 'crawler', 'spider', 'scraper', 'automated',
        'security', 'verify', 'confirm', 'activate', 'validate', 'authenticate',
        'forgot', 'reset', 'recover', 'change', 'update', 'edit', 'delete',
        'create', 'add', 'remove', 'upload', 'download', 'export', 'import',
        'backup', 'restore', 'archive', 'delete', 'remove', 'clear', 'clean',
        'debug', 'dev', 'development', 'staging', 'production', 'live',
        'beta', 'alpha', 'preview', 'demo', 'trial', 'free', 'premium',
        'pro', 'plus', 'gold', 'silver', 'bronze', 'basic', 'advanced',
        'webmaster', 'owner', 'founder', 'creator', 'author', 'editor',
        'manager', 'director', 'executive', 'president', 'ceo', 'cfo', 'cto',
        'sales', 'marketing', 'advertising', 'promotion', 'campaign', 'offer',
        'discount', 'coupon', 'deal', 'special', 'limited', 'exclusive',
        'news', 'blog', 'forum', 'community', 'social', 'network', 'group',
        'chat', 'message', 'notification', 'alert', 'warning', 'error',
        'success', 'failure', 'pending', 'processing', 'completed', 'cancelled',
        'active', 'inactive', 'online', 'offline', 'available', 'busy',
        'open', 'closed', 'public', 'private', 'hidden', 'visible', 'secret',
        'temporary', 'permanent', 'fixed', 'mobile', 'desktop', 'tablet',
        'phone', 'email', 'sms', 'call', 'voice', 'video', 'audio',
        'image', 'photo', 'picture', 'video', 'document', 'file', 'download',
        'upload', 'share', 'like', 'follow', 'subscribe', 'unsubscribe',
        'comment', 'review', 'rating', 'feedback', 'report', 'flag',
        'spam', 'abuse', 'harassment', 'bullying', 'inappropriate',
        'illegal', 'fraud', 'scam', 'phishing', 'malware', 'virus',
        'hack', 'crack', 'exploit', 'vulnerability', 'security', 'breach',
        'data', 'information', 'content', 'media', 'assets', 'resources',
        'tools', 'utilities', 'features', 'functions', 'options', 'preferences',
        'configuration', 'setup', 'installation', 'maintenance', 'upgrade', 'update',
        'version', 'release', 'patch', 'hotfix', 'bug', 'issue', 'problem',
        'solution', 'fix', 'repair', 'restore', 'recover', 'backup', 'sync'
    ]
    
    @staticmethod
    def normalize_username(username):
        """
        Normalize username for consistent storage
        
        Args:
            username (str): Raw username input
            
        Returns:
            str: Normalized username (lowercase, stripped)
        """
        if not username:
            return ''
        
        # Convert to lowercase and strip whitespace
        username = str(username).lower().strip()
        
        # Remove any leading/trailing quotes
        if username.startswith('"') and username.endswith('"'):
            username = username[1:-1]
        
        return username
    
    @staticmethod
    def validate_username_format(username):
        """
        Validate username format and structure
        
        Args:
            username (str): Username to validate
            
        Returns:
            str: Normalized username
            
        Raises:
            ValidationError: If username format is invalid
        """
        if not username:
            raise ValidationError('Username is required')
        
        # Normalize first
        username = UsernameValidator.normalize_username(username)
        
        # Check length constraints
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long')
        
        if len(username) > 15:
            raise ValidationError('Username must be no more than 15 characters long')
        
        # Check allowed characters (alphanumeric, dots, underscores only)
        if not re.match(r'^[a-z0-9._]+$', username):
            raise ValidationError('Username can only contain letters, numbers, dots, and underscores')
        
        # Check for invalid patterns
        if username.startswith('.') or username.startswith('_'):
            raise ValidationError('Username cannot start with a dot or underscore')
        
        if username.endswith('.') or username.endswith('_'):
            raise ValidationError('Username cannot end with a dot or underscore')
        
        # Check for consecutive dots or underscores
        if '..' in username or '__' in username:
            raise ValidationError('Username cannot contain consecutive dots or underscores')
        
        # Check for spaces (shouldn't happen with regex, but double-check)
        if ' ' in username:
            raise ValidationError('Username cannot contain spaces')
        
        return username
    
    @staticmethod
    def is_reserved_username(username):
        """
        Check if username is reserved
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if reserved, False otherwise
        """
        if not username:
            return False
        
        normalized_username = UsernameValidator.normalize_username(username)
        return normalized_username in UsernameValidator.RESERVED_USERNAMES
    
    @staticmethod
    def validate_username_security(username):
        """
        Comprehensive username validation with security checks
        
        Args:
            username (str): Username to validate
            
        Returns:
            str: Normalized username
            
        Raises:
            ValidationError: If username fails any validation
        """
        # Format validation
        username = UsernameValidator.validate_username_format(username)
        
        # Reserved username check
        if UsernameValidator.is_reserved_username(username):
            raise ValidationError('This username is reserved and cannot be used')
        
        # Additional security checks
        if UsernameValidator.is_suspicious_username(username):
            raise ValidationError('This username is not allowed')
        
        return username
    
    @staticmethod
    def is_suspicious_username(username):
        """
        Check for suspicious username patterns
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if suspicious, False otherwise
        """
        if not username:
            return False
        
        username = UsernameValidator.normalize_username(username)
        
        # Check for patterns that might indicate automated accounts
        suspicious_patterns = [
            r'^[0-9]+$',  # All numbers
            r'^[._]+$',    # Only special characters
            r'admin.*',      # Starts with admin
            r'.*admin$',      # Ends with admin
            r'.*admin.*',     # Contains admin
            r'test.*',        # Starts with test
            r'.*test$',        # Ends with test
            r'.*test.*',      # Contains test
            r'demo.*',        # Starts with demo
            r'.*demo$',        # Ends with demo
            r'.*demo.*',       # Contains demo
            r'bot.*',         # Starts with bot
            r'.*bot$',         # Ends with bot
            r'.*bot.*',       # Contains bot
            r'spam.*',        # Starts with spam
            r'.*spam$',        # Ends with spam
            r'.*spam.*',       # Contains spam
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, username):
                return True
        
        return False
    
    @staticmethod
    def generate_username_suggestions(base_username):
        """
        Generate username suggestions if taken
        
        Args:
            base_username (str): Base username to build from
            
        Returns:
            list: List of suggested usernames
        """
        if not base_username:
            return []
        
        base = UsernameValidator.normalize_username(base_username)
        suggestions = []
        
        # Remove invalid characters and limit length
        base = re.sub(r'[^a-z0-9._]', '', base)[:10]
        
        # Generate variations
        suggestions.append(f"{base}01")
        suggestions.append(f"{base}_2024")
        suggestions.append(f"{base}.user")
        suggestions.append(f"user_{base}")
        suggestions.append(f"{base}_official")
        
        # Add numbers if no special chars
        if '.' not in base and '_' not in base:
            suggestions.append(f"{base}_{2024}")
            suggestions.append(f"{base}{123}")
        
        # Filter out reserved names and duplicates
        filtered_suggestions = []
        for suggestion in suggestions:
            if (not UsernameValidator.is_reserved_username(suggestion) and 
                len(suggestion) >= 3 and 
                len(suggestion) <= 15 and
                suggestion not in filtered_suggestions):
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def is_url_safe(username):
        """
        Check if username is safe for URL usage
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if URL-safe, False otherwise
        """
        if not username:
            return False
        
        # URL-safe characters (no spaces, special chars that need encoding)
        url_safe_pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(url_safe_pattern, username))
