import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .services.paymongo_service import PayMongoService
from .models import Appointment

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
                appointment.status = 'Approved'
                appointment.payment_status = 'paid'
                appointment.payment_id = checkout_id
                appointment.payment_date = timezone.now()
                appointment.save()
                
                logger.info(f"Updated appointment {appointment_id} after payment")
        
    except Exception as e:
        logger.error(f"Error handling checkout session paid: {str(e)}")


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
