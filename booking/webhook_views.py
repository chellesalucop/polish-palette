import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .services.paymongo_service import PayMongoService
from .models import Appointment
from .utils.notifications import notify_user_pair
from .utils.activity_logger import log_booking_activity

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def paymongo_webhook(request):
    """Handle PayMongo webhook events"""
    try:
        # Get the signature from headers
        signature_header = request.headers.get('Paymongo-Signature')
        if not signature_header:
            logger.error("No PayMongo signature found")
            return JsonResponse({'error': 'No signature'}, status=400)
        
        # Get the raw payload
        payload = request.body.decode('utf-8')
        
        # Verify the signature
        paymongo = PayMongoService()
        if not paymongo.verify_webhook_signature(payload, signature_header):
            logger.error("Invalid webhook signature")
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Parse the webhook data
        webhook_data = json.loads(payload)
        event_type = webhook_data.get('data', {}).get('attributes', {}).get('type')
        
        logger.info(f"Received webhook event: {event_type}")
        
        # Handle different event types
        if event_type == 'checkout_session.payment.paid':
            handle_checkout_session_paid(webhook_data)
        elif event_type == 'payment.paid':
            handle_payment_paid(webhook_data)
        elif event_type == 'payment.failed':
            handle_payment_failed(webhook_data)
        
        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': 'Webhook received successfully'
        })
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_checkout_session_paid(webhook_data):
    """Handle successful checkout session payment"""
    try:
        session_data = webhook_data['data']['attributes']['data']
        checkout_id = session_data['id']
        metadata = session_data.get('metadata', {})
        appointment_id = metadata.get('appointment_id')
        
        if appointment_id:
            # Create appointment record after successful payment
            try:
                appointment = Appointment.objects.get(id=appointment_id)
            except Appointment.DoesNotExist:
                # If appointment doesn't exist, create it from metadata
                service_category = metadata.get('service_category')
                service = None
                
                # Get the actual Service object
                if service_category == 'gel_polish':
                    service = Service.objects.filter(name__icontains='Gel Polish').first()
                elif service_category == 'soft_gel_extensions':
                    service = Service.objects.filter(name__icontains='Extensions').first()
                elif service_category == 'removal':
                    service = Service.objects.filter(name__icontains='Removal').first()
                
                appointment = Appointment.objects.create(
                    client=None,  # Will be updated later from session
                    service=service,
                    core_category=service_category,
                    style_complexity=metadata.get('complexity_level'),
                    artist_id=None,  # Will be updated later
                    date=None,  # Will be updated later
                    time=None,  # Will be updated later
                    payment_amount=None,  # Will be updated later
                    status='Approved',
                    payment_status='paid',
                    payment_id=checkout_id,
                    payment_date=timezone.now()
                )
                
                logger.info(f"Created new appointment {appointment.id} after payment")
            else:
                # Update existing appointment
                # Status stays 'Waiting' so artist can approve/reject the paid appointment
                appointment.payment_status = 'paid'
                appointment.payment_id = checkout_id
                appointment.payment_date = timezone.now()
                appointment.save()
                
                logger.info(f"Updated appointment {appointment_id} after payment - waiting for artist approval")
                
                # Send notifications for paid appointment
                _send_payment_notifications(appointment)
        
    except Exception as e:
        logger.error(f"Error handling checkout session paid: {str(e)}")


def _send_payment_notifications(appointment):
    """Send email notifications and log activity for paid appointment"""
    try:
        from django.contrib import messages
        from .views import _broadcast_booking_update
        
        client = appointment.client
        artist = appointment.artist
        service = appointment.service
        
        if not client or not artist:
            logger.warning(f"Cannot send notifications: missing client or artist for appointment {appointment.id}")
            return
        
        # Format date and time strings
        appt_date_str = appointment.date.strftime('%B %d, %Y') if appointment.date else 'TBD'
        appt_time_str = appointment.time.strftime('%I:%M %p') if appointment.time else 'TBD'
        service_name = service.name if service else 'Nail Service'
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://127.0.0.1:8000'
        
        # Create booking label
        booking_label = service_name
        if appointment.style_complexity:
            booking_label += f" • {appointment.get_style_complexity_display()}"
        
        # Log booking activity
        log_booking_activity(
            appointment=appointment,
            activity_type='booking_created',
            description=f"Paid booking created by {client.get_full_name()} for {service_name} with {artist.get_full_name()}",
            user=client,
            request=None,
            metadata={
                'service_category': appointment.core_category,
                'complexity_level': appointment.style_complexity,
                'payment_status': 'paid',
                'payment_id': appointment.payment_id
            }
        )
        
        # Broadcast WebSocket update to artist
        _broadcast_booking_update(appointment, {
            'event': 'new_booking',
            'appointment_id': appointment.id,
            'client_name': client.get_full_name(),
            'service_name': service_name,
            'appointment_date': appt_date_str,
            'appointment_time': appt_time_str,
            'status': 'Waiting',
            'payment_status': 'paid',
        })
        
        # Create a mock request for notify_user_pair (needed for both emails)
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        mock_request = MockRequest(client)
        
        # Send email to artist
        artist_email = artist.user.email if artist.user else artist.email
        if artist_email:
            notify_user_pair(
                mock_request,
                receiver_email=artist_email,
                subject=f'New Paid Appointment Request – {booking_label}',
                toast_message=f'New paid booking request for {booking_label} on {appt_date_str}! Please approve or reject.',
                email_template='new_booking_artist',
                context={
                    'artist_name': artist.get_full_name(),
                    'client_name': f'{client.first_name} {client.last_name}',
                    'service_name': booking_label,
                    'appointment_date': appt_date_str,
                    'appointment_time': appt_time_str,
                    'dashboard_url': f'{base_url}/artist/dashboard/',
                    'reference_info': f"Payment Status: Paid via PayMongo | Action Required: Please approve or reject",
                    'plain_text': f'New paid booking request by {client.first_name} for {booking_label} on {appt_date_str} at {appt_time_str}. Payment confirmed. Please approve or reject this appointment.',
                },
                toast_level=messages.INFO,
            )
        
        # Send email to client
        notify_user_pair(
            mock_request,
            receiver_email=client.email,
            subject=f'Payment Received – Waiting for Artist Approval – {booking_label}',
            toast_message=f'Your payment for {booking_label} was successful! Waiting for artist approval.',
            email_template='appointment_waiting',
            context={
                'client_name': client.first_name,
                'artist_name': artist.get_full_name(),
                'service_name': booking_label,
                'appointment_date': appt_date_str,
                'appointment_time': appt_time_str,
                'appointments_url': f'{base_url}/appointments/',
                'duration_info': f'Payment confirmed (ID: {appointment.payment_id}). Waiting for artist approval.',
                'plain_text': f'Your payment for {booking_label} on {appt_date_str} at {appt_time_str} was successful. Payment ID: {appointment.payment_id}. Your appointment is now waiting for artist approval.',
            },
        )
        
        logger.info(f"Sent payment notifications for appointment {appointment.id}")
        
    except Exception as e:
        logger.error(f"Error sending payment notifications: {str(e)}")


def handle_payment_paid(webhook_data):
    """Handle successful payment"""
    try:
        payment_data = webhook_data['data']['attributes']['data']
        payment_id = payment_data['id']
        metadata = payment_data.get('metadata', {})
        appointment_id = metadata.get('appointment_id')
        
        if appointment_id:
            # Update appointment payment status
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.payment_status = 'paid'
            appointment.payment_id = payment_id
            appointment.status = 'Approved'
            appointment.payment_date = timezone.now()
            appointment.save()
            
            logger.info(f"Appointment {appointment_id} payment confirmed")
        
    except Exception as e:
        logger.error(f"Error handling payment paid: {str(e)}")


def handle_payment_failed(webhook_data):
    """Handle failed payment"""
    try:
        payment_data = webhook_data['data']['attributes']['data']
        metadata = payment_data.get('metadata', {})
        appointment_id = metadata.get('appointment_id')
        
        if appointment_id:
            # Update appointment status to payment failed
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.payment_status = 'failed'
            appointment.status = 'Cancelled'
            appointment.save()
            
            logger.info(f"Appointment {appointment_id} payment failed")
        
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")
