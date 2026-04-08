from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class OneTimeMessageMiddleware(MiddlewareMixin):
    """
    Middleware to ensure messages are only displayed once by clearing them
    after they're rendered in templates.
    """
    
    def process_response(self, request, response):
        """
        Clear messages after they've been sent to the template
        to prevent them from reappearing on page refresh.
        """
        # Only clear messages for successful responses (not redirects or errors)
        if response.status_code == 200:
            # Mark messages as shown by adding a header
            response['X-Messages-Shown'] = 'true'
            
            # Clear the messages from the session
            if hasattr(request, '_messages'):
                # Consume all messages so they don't appear again
                list(request._messages)
        
        return response

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        from django.core.exceptions import PermissionDenied
        
        print(f"DEBUG: Middleware processing exception: {exception}")
        
        if isinstance(exception, PermissionDenied) and "2FA required" in str(exception):
            print("DEBUG: PermissionDenied detected, checking session")
            # Check if this is a 2FA redirect
            if request.session.get('2fa_user_email'):
                print("DEBUG: Session has 2fa_user_email, redirecting to 2FA")
                messages.info(request, "A 2FA code has been sent to your email.")
                return redirect('two_factor_verify')
            else:
                print("DEBUG: No 2fa_user_email in session")
                messages.error(request, "Authentication failed. Please try again.")
                return redirect('login')
        
        return None

class BruteForceProtectionMiddleware:
    """Middleware to protect against brute force attacks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is a login attempt
        if request.path in ['/login/', '/artist_login/'] and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            email = request.POST.get('email', '')
            
            # Check rate limits
            if self.is_rate_limited(client_ip, email):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}, Email: {email}")
                messages.error(request, "Too many login attempts. Please try again later.")
                return redirect('login')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        from .utils.auth_utils import get_client_ip
        return get_client_ip(request)
    
    def is_rate_limited(self, ip, email):
        """Check if the IP or email has exceeded rate limits"""
        
        # IP-based rate limiting (max 5 attempts per 15 minutes)
        ip_key = f"login_attempts_ip_{ip}"
        ip_attempts = cache.get(ip_key, 0)
        
        # Email-based rate limiting (max 3 attempts per 15 minutes)
        email_key = f"login_attempts_email_{email}"
        email_attempts = cache.get(email_key, 0)
        
        if ip_attempts >= 5 or email_attempts >= 3:
            return True
        
        # Increment counters
        cache.set(ip_key, ip_attempts + 1, timeout=900)  # 15 minutes
        cache.set(email_key, email_attempts + 1, timeout=900)  # 15 minutes
        
        return False

class PostRedirectGetMiddleware:
    """
    Middleware to prevent form resubmission by ensuring POST requests
    are always followed by redirects (Post/Redirect/Get pattern).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if this is a POST request that rendered a template directly
        if (request.method == 'POST' and 
            response.status_code == 200 and 
            hasattr(response, 'content') and 
            'text/html' in response.get('Content-Type', '')):
            
            # This is likely a form that was rendered without redirect
            # Convert to redirect to prevent resubmission
            
            # Skip admin and auth paths to allow standard form error rendering with data retention
            skip_paths = ['/admin/', '/signup/', '/login/', '/two-factor-verify/', '/artist/login/']
            if any(request.path.startswith(p) for p in skip_paths):
                return response
                
            from django.urls import reverse
            from django.http import HttpResponseRedirect
            
            # Get the current URL name and redirect to it
            if hasattr(request, 'resolver_match') and request.resolver_match:
                url_name = request.resolver_match.view_name # Use view_name instead of url_name to include namespace
                try:
                    return HttpResponseRedirect(reverse(url_name))
                except Exception:
                    # If reverse fails for any reason, just return the original response
                    return response
        
        return response

class RedirectLoopMiddleware:
    """
    Middleware to detect and prevent infinite redirect loops.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_redirects = 10  # Maximum allowed redirects
        self.redirect_timeout = 5  # Seconds before timeout
    
    def __call__(self, request):
        import time
        response = self.get_response(request)
        
        # Track redirects in session
        redirect_count = request.session.get('redirect_count', 0)
        last_redirect_time = request.session.get('last_redirect_time', 0)
        
        current_time = time.time()
        
        # Check if this is a redirect response
        if hasattr(response, 'url') and response.status_code in [301, 302]:
            redirect_count += 1
            request.session['redirect_count'] = redirect_count
            request.session['last_redirect_time'] = current_time
            
            # Check for redirect loop
            if redirect_count > self.max_redirects:
                print(f"WARNING: Redirect loop detected! Count: {redirect_count}")
                # Break the loop with an error page
                from django.shortcuts import render
                return render(request, 'booking/redirect_loop_error.html', status=500)
            
            # Check if redirects are happening too quickly (potential loop)
            elif (current_time - last_redirect_time) < self.redirect_timeout:
                print(f"WARNING: Rapid redirects detected! Time diff: {current_time - last_redirect_time}")
                if redirect_count > 3:
                    from django.shortcuts import render
                    return render(request, 'booking/redirect_loop_error.html', status=500)
        else:
            # Reset redirect count on successful non-redirect response
            if response.status_code == 200:
                request.session['redirect_count'] = 0
        
        return response

class OTPRateLimitMiddleware:
    """Middleware to protect against OTP brute force attacks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is an OTP verification attempt
        if request.path == '/two-factor-verify/' and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            user_email = request.session.get('2fa_user_email', '')
            
            # Check OTP rate limits
            if self.is_otp_rate_limited(client_ip, user_email):
                logger.warning(f"OTP rate limit exceeded for IP: {client_ip}, Email: {user_email}")
                messages.error(request, "Too many OTP attempts. Please request a new code.")
                return redirect('two_factor_verify')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_otp_rate_limited(self, ip, email):
        """Check if OTP attempts have exceeded rate limits"""
        
        # IP-based OTP rate limiting (max 3 attempts per 10 minutes)
        ip_key = f"otp_attempts_ip_{ip}"
        ip_attempts = cache.get(ip_key, 0)
        
        # Email-based OTP rate limiting (max 3 attempts per 10 minutes)
        email_key = f"otp_attempts_email_{email}"
        email_attempts = cache.get(email_key, 0)
        
        if ip_attempts >= 3 or email_attempts >= 3:
            return True
        
        # Increment counters
        cache.set(ip_key, ip_attempts + 1, timeout=600)  # 10 minutes
        cache.set(email_key, email_attempts + 1, timeout=600)  # 10 minutes
        
        return False

class NoCacheMiddleware:
    """
    Middleware to prevent browser caching of authenticated pages.
    This ensures that when a user logs out, they cannot click the 
    'Back' button to see sensitive data.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # If the user is authenticated, we want to prevent the browser from caching the response
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
        return response
