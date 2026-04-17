import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .services.paymongo_service import PayMongoService
from .models import Appointment, Service, Client

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
def create_checkout_session(request):
    """Create a PayMongo checkout session with pending appointment"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        description = data.get('description', 'Nail Appointment Booking')
        booking_data = data.get('booking_data', {})
        
        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)
        
        # Get booking details for validation
        service_category = booking_data.get('service_category')
        artist_id = booking_data.get('artist_id')
        date_str = booking_data.get('date')
        time_str = booking_data.get('time')
        
        # Validate required booking data
        if not all([service_category, artist_id, date_str, time_str]):
            return JsonResponse({'error': 'Missing required booking information'}, status=400)
        
        # Get artist and service objects
        from .models import Artist
        artist = Artist.objects.filter(id=artist_id).first()
        if not artist:
            return JsonResponse({'error': 'Selected artist not found'}, status=400)
        
        service = None
        if service_category:
            service = Service.objects.filter(name__icontains=service_category.replace('_', ' ').title()).first()
        
        # Parse date and time for validation
        from datetime import datetime
        try:
            formatted_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            formatted_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)
        
        # Check for duplicate bookings (same checks as booking_create_view)
        # Check if client already has an appointment for this service category on this day
        daily_service_exists = Appointment.objects.filter(
            client=request.user if request.user.is_authenticated else None,
            date=formatted_date,
            core_category=service_category,
        ).exclude(status__in=['Cancelled', 'Rejected']).exists()
        
        # Check if client already has ANY appointment at this time slot
        time_conflict = Appointment.objects.filter(
            client=request.user if request.user.is_authenticated else None,
            date=formatted_date,
            time=formatted_time,
        ).exclude(status__in=['Cancelled', 'Rejected']).exists()
        
        # Check if artist is already booked at this slot
        artist_conflict = Appointment.objects.filter(
            artist=artist,
            date=formatted_date,
            time=formatted_time,
        ).exclude(status__in=['Cancelled', 'Rejected']).exists()
        
        if daily_service_exists:
            category_display = service_category.replace('_', ' ').title()
            return JsonResponse({
                'error': f'Booking limit reached',
                'message': f'You can only book one {category_display} appointment per day.'
            }, status=400)
        
        if time_conflict:
            return JsonResponse({
                'error': 'Time conflict',
                'message': 'You already have an appointment booked for that time slot.'
            }, status=400)
        
        if artist_conflict:
            return JsonResponse({
                'error': 'Artist unavailable',
                'message': f'{artist.get_full_name()} is already booked at this time. Please choose a different time slot.'
            }, status=400)
        
        # All checks passed - create pending appointment before payment
        appointment = Appointment.objects.create(
            client=request.user if request.user.is_authenticated else None,
            service=service,
            artist=artist,
            date=formatted_date,
            time=formatted_time,
            core_category=service_category,
            style_complexity=booking_data.get('complexity_level'),
            custom_art_description=booking_data.get('custom_art_description', ''),
            payment_amount=amount,
            status='Pending',
            payment_status='pending'
        )
        
        # Generate success and cancel URLs with appointment_id
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://127.0.0.1:8000'
        
        paymongo = PayMongoService()
        result = paymongo.create_checkout_session(
            amount=amount,
            description=description,
            success_url=f"{base_url}/booking/payment-success/?session_id={{CHECKOUT_SESSION_ID}}&booking_id={appointment.id}",
            cancel_url=f"{base_url}/booking/payment-cancelled/?booking_id={appointment.id}",
            metadata={
                'appointment_id': str(appointment.id),
                'service_category': service_category,
                'complexity_level': booking_data.get('complexity_level')
            }
        )
        
        checkout_session = result['data']
        
        return JsonResponse({
            'checkout_session_id': checkout_session['id'],
            'checkout_url': checkout_session['attributes']['checkout_url'],
            'appointment_id': appointment.id
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
