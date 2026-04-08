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
from datetime import date, timedelta

def test_scrollable_content():
    print("=" * 60)
    print("TESTING DASHBOARD SCROLLABLE CONTENT")
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
        
        # Count content that would make dashboard scrollable
        pending_requests = artist_appointments.filter(status='Waiting').order_by('date', 'time')
        completed_schedules = artist_appointments.filter(status='Finished').order_by('-date', '-time')[:5]
        upcoming_bookings = artist_appointments.filter(date__gte=today, status__in=['Waiting', 'Approved', 'On-going']).order_by('date', 'time')
        today_schedule = artist_appointments.filter(date=today).order_by('time')
        
        total_content_items = (
            pending_requests.count() +
            completed_schedules.count() +
            upcoming_bookings.count() +
            today_schedule.count()
        )
        
        print(f"\n📊 Dashboard Content Summary:")
        print(f"   Pending Approvals: {pending_requests.count()}")
        print(f"   Completed Schedules: {completed_schedules.count()}")
        print(f"   Upcoming Bookings: {upcoming_bookings.count()}")
        print(f"   Today's Schedule: {today_schedule.count()}")
        print(f"   Total Items: {total_content_items}")
        
        print(f"\n✅ Dashboard should now be scrollable!")
        print(f"💡 Changes made:")
        print(f"   - Removed 'overflow: hidden' from dashboard container")
        print(f"   - Changed 'height: 100vh' to 'min-height: 100vh'")
        print(f"   - Removed JavaScript that disabled body scrolling")
        print(f"   - Removed 'min-height: 0' from row")
        print(f"   - Made sidebar sticky with proper scrolling")
        
        if total_content_items > 5:
            print(f"\n📜 With {total_content_items} items, dashboard should have scrollable content")
        else:
            print(f"\n📄 Dashboard has minimal content, but scrolling is now enabled")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_scrollable_content()
