from django.core.cache import cache

def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def clear_otp_rate_limit(request, email):
    """Clear the OTP rate limit for the given IP and email."""
    ip = get_client_ip(request)
    ip_key = f"otp_attempts_ip_{ip}"
    email_key = f"otp_attempts_email_{email}"
    
    cache.delete(ip_key)
    cache.delete(email_key)
    print(f"DEBUG: Cleared OTP rate limits for IP: {ip}, Email: {email}")
