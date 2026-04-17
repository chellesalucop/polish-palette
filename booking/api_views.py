import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .services.paymongo_service import PayMongoService
from .models import Appointment, Service

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def create_checkout_session(request):
    """Create a PayMongo checkout session"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        description = data.get('description', 'Nail Appointment Booking')
        booking_data = data.get('booking_data', {})
        
        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)
        
        # Generate success and cancel URLs (no appointment creation yet)
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://127.0.0.1:8000'
        
        # Create checkout session without appointment first
        paymongo = PayMongoService()
        result = paymongo.create_checkout_session(
            amount=amount,
            description=description,
            success_url=f"{base_url}/booking/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/booking/payment-cancelled/",
            metadata={
                'service_category': booking_data.get('service_category'),
                'complexity_level': booking_data.get('complexity_level')
            }
        )
        
        checkout_session = result['data']
        
        return JsonResponse({
            'checkout_session_id': checkout_session['id'],
            'checkout_url': checkout_session['attributes']['checkout_url']
        })
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_payment_status(request):
    """Get payment status for an appointment"""
    try:
        appointment_id = request.GET.get('booking_id')
        if not appointment_id:
            return JsonResponse({'error': 'Appointment ID is required'}, status=400)
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            return JsonResponse({
                'payment_status': appointment.payment_status,
                'booking_status': appointment.status,
                'payment_id': appointment.payment_id
            })
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
        
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
