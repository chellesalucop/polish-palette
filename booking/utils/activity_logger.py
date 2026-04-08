"""
Activity logging utilities for tracking user actions throughout the system.
"""

from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.http import HttpRequest
from ..models import ActivityLog, Client, Artist


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent string from request."""
    return request.META.get('HTTP_USER_AGENT', '')


def log_client_activity(user, activity_type, description, request=None, 
                       appointment=None, service=None, metadata=None):
    """
    Log activity for a client user.
    
    Args:
        user: Client user object
        activity_type: Activity type from ActivityLog.ACTIVITY_TYPES
        description: Human-readable description
        request: HttpRequest object (optional)
        appointment: Related appointment (optional)
        service: Related service (optional)
        metadata: Additional metadata (optional)
    """
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    return ActivityLog.log_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        appointment=appointment,
        service=service,
        metadata=metadata,
        user_type='client'
    )


def log_artist_activity(artist, activity_type, description, request=None,
                       appointment=None, service=None, metadata=None):
    """
    Log activity for an artist.
    
    Args:
        artist: Artist object
        activity_type: Activity type from ActivityLog.ACTIVITY_TYPES
        description: Human-readable description
        request: HttpRequest object (optional)
        appointment: Related appointment (optional)
        service: Related service (optional)
        metadata: Additional metadata (optional)
    """
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    return ActivityLog.log_activity(
        artist=artist,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        appointment=appointment,
        service=service,
        metadata=metadata,
        user_type='artist'
    )


def log_admin_activity(user, activity_type, description, request=None,
                       appointment=None, service=None, metadata=None):
    """
    Log activity for an admin user.
    
    Args:
        user: Admin user object (Client model with is_staff=True)
        activity_type: Activity type from ActivityLog.ACTIVITY_TYPES
        description: Human-readable description
        request: HttpRequest object (optional)
        appointment: Related appointment (optional)
        service: Related service (optional)
        metadata: Additional metadata (optional)
    """
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    return ActivityLog.log_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        appointment=appointment,
        service=service,
        metadata=metadata,
        user_type='admin'
    )


def log_system_activity(activity_type, description, metadata=None):
    """
    Log system-level activities.
    
    Args:
        activity_type: Activity type from ActivityLog.ACTIVITY_TYPES
        description: Human-readable description
        metadata: Additional metadata (optional)
    """
    return ActivityLog.log_activity(
        activity_type=activity_type,
        description=description,
        metadata=metadata,
        user_type='system'
    )


def log_booking_activity(appointment, activity_type, description, user=None, 
                        artist=None, request=None, metadata=None):
    """
    Log booking-related activities.
    
    Args:
        appointment: Appointment object
        activity_type: Activity type from ActivityLog.ACTIVITY_TYPES
        description: Human-readable description
        user: Client user (optional)
        artist: Artist (optional)
        request: HttpRequest object (optional)
        metadata: Additional metadata (optional)
    """
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    # Determine user type and set appropriate parameters
    if user:
        return ActivityLog.log_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            appointment=appointment,
            service=appointment.service,
            metadata=metadata,
            user_type='client'
        )
    elif artist:
        return ActivityLog.log_activity(
            artist=artist,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            appointment=appointment,
            service=appointment.service,
            metadata=metadata,
            user_type='artist'
        )
    else:
        # System action on booking
        return ActivityLog.log_activity(
            activity_type=activity_type,
            description=description,
            appointment=appointment,
            service=appointment.service,
            metadata=metadata,
            user_type='system'
        )


# Django signal receivers for automatic login/logout logging
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Automatically log user login."""
    if isinstance(user, Client):
        if user.is_staff:
            log_admin_activity(
                user=user,
                activity_type='login',
                description=f"Admin {user.get_full_name()} logged in",
                request=request,
                metadata={'login_time': timezone.now().isoformat()}
            )
        else:
            log_client_activity(
                user=user,
                activity_type='login',
                description=f"Client {user.get_full_name()} logged in",
                request=request,
                metadata={'login_time': timezone.now().isoformat()}
            )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Automatically log user logout."""
    if isinstance(user, Client):
        if user.is_staff:
            log_admin_activity(
                user=user,
                activity_type='logout',
                description=f"Admin {user.get_full_name()} logged out",
                request=request,
                metadata={'logout_time': timezone.now().isoformat()}
            )
        else:
            log_client_activity(
                user=user,
                activity_type='logout',
                description=f"Client {user.get_full_name()} logged out",
                request=request,
                metadata={'logout_time': timezone.now().isoformat()}
            )


def log_failed_login(email, request=None, reason="Invalid credentials"):
    """Log failed login attempts."""
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    return ActivityLog.log_activity(
        activity_type='failed_login',
        description=f"Failed login attempt for email: {email} - {reason}",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={
            'email': email,
            'reason': reason,
            'attempt_time': timezone.now().isoformat()
        },
        user_type='system'
    )


def log_artist_login(artist, request=None):
    """Log artist login."""
    return log_artist_activity(
        artist=artist,
        activity_type='login',
        description=f"Artist {artist.get_full_name()} logged in",
        request=request,
        metadata={'login_time': timezone.now().isoformat()}
    )


def log_artist_logout(artist, request=None):
    """Log artist logout."""
    return log_artist_activity(
        artist=artist,
        activity_type='logout',
        description=f"Artist {artist.get_full_name()} logged out",
        request=request,
        metadata={'logout_time': timezone.now().isoformat()}
    )
