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
    """
    import logging
    import threading
    import os
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings
    from email.mime.image import MIMEImage

    logger = logging.getLogger(__name__)

    # 1. IN-APP TOAST for the active user (Must be in main thread)
    try:
        messages.add_message(request, toast_level, toast_message)
    except Exception as e:
        logger.warning(f"Could not add toast message: {str(e)}")

    # 2. PERSISTENT BELL NOTIFICATION (Save to DB)
    try:
        from booking.models import Notification
        bell_message = context.get('plain_text', toast_message)
        if bell_message:
            Notification.objects.create(
                recipient_email=receiver_email,
                message=bell_message,
            )
    except Exception as e:
        logger.error(f"Failed to create bell notification: {str(e)}")

    # 3. BACKGROUND EMAIL SENDING
    def send_email_task():
        try:
            # Render templates
            html_body = render_to_string(f'emails/{email_template}.html', context)
            plain_body = context.get('plain_text', toast_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[receiver_email],
            )
            email.attach_alternative(html_body, 'text/html')

            # Handle logo attachment if it exists
            logo_path = os.path.join(settings.BASE_DIR, 'booking/static/images/logo.png')
            if os.path.exists(logo_path):
                try:
                    with open(logo_path, 'rb') as logo_file:
                        logo_content = logo_file.read()
                    
                    logo_mime = MIMEImage(logo_content)
                    logo_mime.add_header('Content-ID', '<polishpalattelogo>')
                    logo_mime.add_header('Content-Disposition', 'inline', filename='logo.png')
                    email.attach(logo_mime)
                except Exception as logo_err:
                    logger.warning(f"Failed to attach logo to email: {str(logo_err)}")

            # Send the email
            # We set fail_silently=False here because it runs in a background thread
            # and we want the error captured in our try/except block.
            email.send(fail_silently=False)
            logger.info(f"Email '{subject}' successfully sent to {receiver_email}")

        except Exception as e:
            logger.error(f"CRITICAL: Failed to send email to {receiver_email}. Type: {type(e).__name__}, Error: {str(e)}")

    # Launch as daemon thread to prevent blocking the response
    email_thread = threading.Thread(target=send_email_task)
    email_thread.daemon = True
    email_thread.start()

