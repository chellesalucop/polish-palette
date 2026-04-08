"""
Push-and-Log Notification System for Polish Palette.

- Push (In-App): Django messages framework toast for the active user.
- Log (Email): HTML email sent to the receiving party.
- Bell (Persistent): Saved to Notification model for bell icon popup.
"""
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def notify_user_pair(request, receiver_email, subject, toast_message, email_template, context, toast_level=messages.INFO):
    """
    Send a toast notification to the current user and an HTML email to the receiver.
    Also saves a persistent bell notification for the receiver.

    Args:
        request: The Django request object (for the in-app toast).
        receiver_email: Email of the person who should receive the email.
        subject: Email subject line.
        toast_message: Short text shown as an in-app toast to the current user.
        email_template: Template name inside 'emails/' (without .html).
        context: Dict passed to the email template.
        toast_level: messages level (messages.SUCCESS, messages.INFO, etc.).
    """
    # 1. IN-APP TOAST for the active user
    messages.add_message(request, toast_level, toast_message)

    # 2. PERSISTENT BELL NOTIFICATION for the receiver
    from booking.models import Notification
    bell_message = context.get('plain_text', toast_message)
    if bell_message:
        Notification.objects.create(
            recipient_email=receiver_email,
            message=bell_message,
        )

    # 3. EMAIL to the receiving party
    html_body = render_to_string(f'emails/{email_template}.html', context)
    plain_body = context.get('plain_text', toast_message)

    # Attach logo as inline image
    import os
    from django.core.files.base import ContentFile
    from django.conf import settings
    
    logo_path = os.path.join(settings.BASE_DIR, 'booking/static/images/logo.png')
    with open(logo_path, 'rb') as logo_file:
        logo_content = logo_file.read()
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[receiver_email],
    )
    email.attach_alternative(html_body, 'text/html')
    
    # Attach logo as inline image
    from email.mime.image import MIMEImage
    from email.mime.base import MIMEBase
    from email import encoders
    
    try:
        # Create MIME image object
        logo_mime = MIMEImage(logo_content)
        logo_mime.add_header('Content-ID', '<polishpalattelogo>')
        
        # Attach the image to the email
        email.attach(logo_mime)
        email.send(fail_silently=True)
        
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if it's an encoding-related error
        if 'codec' in str(e) and 'utf-8' in str(e):
            logger.error(f"UTF-8 encoding error in email: {str(e)}")
            logger.error(f"Logo file path: {os.path.join(settings.BASE_DIR, 'booking/static/images/logo.png')}")
            logger.error(f"Logo content length: {len(logo_content)} bytes")
        else:
            logger.error(f"Email sending failed: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
        
        # Re-raise the exception so the calling view can handle it
        raise
