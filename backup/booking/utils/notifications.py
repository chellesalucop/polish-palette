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
        toast_level: messages level (messages.SUCCESS, messages.INFO, etc.)
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

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[receiver_email],
    )
    email.attach_alternative(html_body, 'text/html')
    email.send(fail_silently=True)
