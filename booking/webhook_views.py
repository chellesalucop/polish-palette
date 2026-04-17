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
        # Get the raw payload
        payload = request.body.decode('utf-8')
        logger.info(f"Webhook received. Payload: {payload[:500]}...")
        
        # Get the signature from headers
        signature_header = request.headers.get('Paymongo-Signature')
        logger.info(f"Signature header present: {bool(signature_header)}")
        
        if signature_header:
            # Verify the signature
            paymongo = PayMongoService()
            is_valid = paymongo.verify_webhook_signature(payload, signature_header)
            logger.info(f"Signature verification result: {is_valid}")
        
        # Parse the webhook data
        webhook_data = json.loads(payload)
        
        # PayMongo event structure: data.attributes.type
        event_data = webhook_data.get('data', {})
        attributes = event_data.get('attributes', {})
        event_type = attributes.get('type')
        
        logger.info(f"Received webhook event type: {event_type}")
        
        # Handle different event types
        if event_type == 'checkout_session.payment.paid':
            logger.info("Processing checkout_session.payment.paid event")
            try:
                handle_checkout_session_paid(webhook_data)
                logger.info("checkout_session.payment.paid processed successfully")
            except Exception as handler_error:
                logger.error(f"Error in handle_checkout_session_paid: {str(handler_error)}", exc_info=True)
        elif event_type == 'payment.paid':
            logger.info("Processing payment.paid event")
            try:
                handle_payment_paid(webhook_data)
                logger.info("payment.paid processed successfully")
            except Exception as handler_error:
                logger.error(f"Error in handle_payment_paid: {str(handler_error)}", exc_info=True)
        elif event_type == 'payment.failed':
            logger.info("Processing payment.failed event")
            try:
                handle_payment_failed(webhook_data)
                logger.info("payment.failed processed successfully")
            except Exception as handler_error:
                logger.error(f"Error in handle_payment_failed: {str(handler_error)}", exc_info=True)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
        
        # ALWAYS return 200 success so PayMongo doesn't retry
        return JsonResponse({
            'status': 'success',
            'message': 'Webhook processed',
            'event_type': event_type
        })
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        # Still return 200 to prevent PayMongo retries, but log the error
        return JsonResponse({
            'status': 'error_logged',
            'message': 'Error occurred but acknowledged'
        }, status=200)


def handle_checkout_session_paid(webhook_data):
    """Handle successful checkout session payment"""
    try:
        logger.info(f"handle_checkout_session_paid called with data: {json.dumps(webhook_data, indent=2)[:1000]}")
        
        # PayMongo event structure: data.attributes.data contains the checkout session
        event_attributes = webhook_data.get('data', {}).get('attributes', {})
        session_data = event_attributes.get('data', {})
        
        if not session_data:
            logger.error("No session data found in webhook payload")
            logger.error(f"Available keys: {event_attributes.keys()}")
            return
        
        checkout_id = session_data.get('id')
        session_attrs = session_data.get('attributes', {})
        metadata = session_attrs.get('metadata', {})
        appointment_id = metadata.get('appointment_id')
        
        logger.info(f"Extracted checkout_id: {checkout_id}, appointment_id: {appointment_id}")
        logger.info(f"Metadata: {metadata}")
        
        if not appointment_id:
            logger.error("No appointment_id found in metadata")
            return
        
        # Find and update appointment record after successful payment
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            logger.info(f"Found existing appointment: {appointment.id}")
        except Appointment.DoesNotExist:
            logger.error(f"Appointment {appointment_id} not found!")
            return
        
        # Update existing appointment
        # Status stays 'Waiting' so artist can approve/reject the paid appointment
        appointment.payment_status = 'paid'
        appointment.payment_id = checkout_id
        appointment.payment_date = timezone.now()
        appointment.save()
        
        logger.info(f"Updated appointment {appointment_id} - payment_status: paid, status: {appointment.status}")
        
        # Send notifications for paid appointment
        try:
            _send_payment_notifications(appointment)
            logger.info(f"Payment notifications sent successfully for appointment {appointment_id}")
        except Exception as notify_error:
            logger.error(f"Error sending notifications: {str(notify_error)}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error handling checkout session paid: {str(e)}", exc_info=True)


def _send_payment_notifications(appointment):
    """Send email notifications and log activity for paid appointment"""
    try:
        from django.contrib import messages
        from .views import _broadcast_booking_update
        
        client = appointment.client
        artist = appointment.artist
        service = appointment.service
        
        logger.info(f"Sending notifications for appointment {appointment.id}: client={client}, artist={artist}, service={service}")
        
        if not client:
            logger.warning(f"Cannot send notifications: missing client for appointment {appointment.id}")
            return
        if not artist:
            logger.warning(f"Cannot send notifications: missing artist for appointment {appointment.id}")
            return
        
        # Format date and time strings
        appt_date_str = appointment.date.strftime('%B %d, %Y') if appointment.date else 'TBD'
        appt_time_str = appointment.time.strftime('%I:%M %p') if appointment.time else 'TBD'
        service_name = service.name if service else 'Nail Service'
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://127.0.0.1:8000'
        
        logger.info(f"Appointment details: {service_name} on {appt_date_str} at {appt_time_str}")
        
        # Create booking label
        booking_label = service_name
        if appointment.style_complexity:
            booking_label += f" • {appointment.get_style_complexity_display()}"
        
        # Log booking activity
        try:
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
            logger.info(f"Booking activity logged successfully")
        except Exception as activity_error:
            logger.error(f"Error logging booking activity: {str(activity_error)}", exc_info=True)
        
        # Broadcast WebSocket update to artist
        try:
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
            logger.info(f"WebSocket broadcast sent successfully")
        except Exception as ws_error:
            logger.error(f"Error broadcasting WebSocket update: {str(ws_error)}", exc_info=True)
        
        # Create a mock request for notify_user_pair (needed for both emails)
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        mock_request = MockRequest(client)
        
        # Send email to artist
        try:
            artist_email = artist.user.email if (artist.user and artist.user.email) else artist.email
            logger.info(f"Artist email: {artist_email}")
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
                logger.info(f"Artist email sent successfully to {artist_email}")
            else:
                logger.warning(f"No email found for artist {artist.id}")
        except Exception as artist_email_error:
            logger.error(f"Error sending artist email: {str(artist_email_error)}", exc_info=True)
        
        # Send email to client
        try:
            client_email = client.email if client.email else (client.user.email if hasattr(client, 'user') and client.user else None)
            logger.info(f"Client email: {client_email}")
            if client_email:
                notify_user_pair(
                    mock_request,
                    receiver_email=client_email,
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
                logger.info(f"Client email sent successfully to {client_email}")
            else:
                logger.warning(f"No email found for client {client.id}")
        except Exception as client_email_error:
            logger.error(f"Error sending client email: {str(client_email_error)}", exc_info=True)
        
        logger.info(f"All payment notifications processed for appointment {appointment.id}")
        
    except Exception as e:
        logger.error(f"Error in _send_payment_notifications: {str(e)}", exc_info=True)


def handle_payment_paid(webhook_data):
    """Handle successful payment"""
    try:
        logger.info(f"handle_payment_paid called")
        
        event_attributes = webhook_data.get('data', {}).get('attributes', {})
        payment_data = event_attributes.get('data', {})
        
        if not payment_data:
            logger.error("No payment data found in webhook")
            return
        
        payment_id = payment_data.get('id')
        payment_attrs = payment_data.get('attributes', {})
        metadata = payment_attrs.get('metadata', {})
        appointment_id = metadata.get('appointment_id')
        
        logger.info(f"Payment {payment_id} for appointment {appointment_id}")
        
        if appointment_id:
            # Update appointment payment status
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                appointment.payment_status = 'paid'
                appointment.payment_id = payment_id
                # Status stays 'Waiting' for artist approval
                appointment.payment_date = timezone.now()
                appointment.save()
                
                logger.info(f"Appointment {appointment_id} payment confirmed, status kept as {appointment.status}")
                
                # Send notifications
                try:
                    _send_payment_notifications(appointment)
                except Exception as notify_error:
                    logger.error(f"Error in notifications: {str(notify_error)}", exc_info=True)
            except Appointment.DoesNotExist:
                logger.error(f"Appointment {appointment_id} not found")
        
    except Exception as e:
        logger.error(f"Error handling payment paid: {str(e)}", exc_info=True)


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
