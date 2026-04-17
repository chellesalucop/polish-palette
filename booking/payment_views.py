from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Appointment


@login_required
def payment_success_view(request):
    """Handle successful payment return from PayMongo"""
    session_id = request.GET.get('session_id')
    appointment_id = request.GET.get('booking_id')
    
    if not appointment_id:
        messages.error(request, 'Booking information not found.')
        return redirect('dashboard')
    
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Verify appointment belongs to current user
        if appointment.client and appointment.client != request.user:
            messages.error(request, 'Invalid appointment.')
            return redirect('dashboard')
        
        # Check if payment was successful (should be updated by webhook)
        if appointment.payment_status == 'paid':
            if appointment.date and appointment.time:
                messages.success(request, 
                    f'Payment successful! Your appointment on {appointment.date} at {appointment.time} has been confirmed.')
            else:
                messages.success(request, 
                    'Payment successful! Your appointment details will be updated shortly.')
        else:
            messages.info(request, 
                'Payment is being processed. You will receive a confirmation once payment is verified.')
        
        return redirect('appointments_list')
        
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('dashboard')


@login_required
def payment_cancelled_view(request):
    """Handle cancelled payment from PayMongo"""
    booking_id = request.GET.get('booking_id')
    
    if not booking_id:
        messages.error(request, 'Booking information not found.')
        return redirect('dashboard')
    
    try:
        appointment = get_object_or_404(Appointment, id=booking_id)
        
        # Verify appointment belongs to current user
        if appointment.client and appointment.client != request.user:
            messages.error(request, 'Invalid appointment.')
            return redirect('dashboard')
        
        # Update appointment status
        appointment.payment_status = 'cancelled'
        appointment.status = 'Cancelled'
        appointment.save()
        
        messages.info(request, 'Payment was cancelled. Your appointment has been cancelled.')
        return redirect('dashboard')
        
    except Exception as e:
        messages.error(request, f'Error processing cancellation: {str(e)}')
        return redirect('dashboard')
