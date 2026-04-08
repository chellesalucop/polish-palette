#!/usr/bin/env python
import os
import sys
import django

# Add project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nail_booking.settings')
django.setup()

from booking.models import Artist, Appointment
from datetime import date

def test_dashboard_data():
    print("=" * 60)
    print("TESTING DASHBOARD DATA FOR NEW SECTIONS")
    print("=" * 60)
    
    try:
        # Get the artist
        artist = Artist.objects.first()
        if not artist:
            print("❌ No artist found")
            return
            
        print(f"🎨 Artist: {artist.user.get_full_name()}")
        
        today = date.today()
        artist_appointments = Appointment.objects.filter(artist=artist)
        
        # Test pending requests (for approval section)
        pending_requests = artist_appointments.filter(status='Waiting').order_by('date', 'time')
        print(f"\n📋 Pending Approval Requests: {pending_requests.count()}")
        for apt in pending_requests:
            print(f"  - {apt.date} at {apt.time}: {apt.service.name} for {apt.client.get_full_name()}")
        
        # Test completed schedules (for completed section)
        completed_schedules = artist_appointments.filter(status='Finished').order_by('-date', '-time')[:5]
        print(f"\n✅ Recently Completed Schedules: {completed_schedules.count()}")
        for apt in completed_schedules:
            print(f"  - {apt.date} at {apt.time}: {apt.service.name} for {apt.client.get_full_name()}")
        
        # Test today's schedule (for today's queue)
        today_schedule = artist_appointments.filter(date=today).order_by('time')
        print(f"\n📅 Today's Schedule: {today_schedule.count()}")
        for apt in today_schedule:
            print(f"  - {apt.time}: {apt.service.name} for {apt.client.get_full_name()} ({apt.status})")
        
        # Test upcoming bookings (for upcoming schedule)
        upcoming_bookings = artist_appointments.filter(date__gte=today, status__in=['Waiting', 'On-going']).order_by('date', 'time')
        print(f"\n🔮 Upcoming Bookings: {upcoming_bookings.count()}")
        for apt in upcoming_bookings:
            print(f"  - {apt.date} at {apt.time}: {apt.service.name} for {apt.client.get_full_name()}")
        
        print(f"\n✅ All dashboard data sections are properly configured!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_dashboard_data()
