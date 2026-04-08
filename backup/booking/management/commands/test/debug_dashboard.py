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

def debug_dashboard_data():
    print("=" * 60)
    print("DEBUGGING DASHBOARD DATA")
    print("=" * 60)
    
    try:
        # Get the artist (same as in view)
        artist = Artist.objects.first()
        if not artist:
            print("❌ No artist found")
            return
            
        print(f"🎨 Artist: {artist.user.get_full_name()}")
        
        # Replicate the exact view logic
        today = date.today()
        artist_appointments = Appointment.objects.filter(artist=artist)
        
        print(f"📅 Today: {today}")
        print(f"📊 Total appointments: {artist_appointments.count()}")
        
        # Check the exact query from the view
        upcoming_bookings = artist_appointments.filter(
            date__gte=today, 
            status__in=['Waiting', 'On-going']
        ).order_by('date', 'time')
        
        print(f"🔍 Upcoming bookings query: {upcoming_bookings.count()} found")
        
        # Show the actual data that would be passed to template
        print("\n📋 Upcoming bookings data:")
        for booking in upcoming_bookings:
            print(f"  Date: {booking.date}")
            print(f"  Time: {booking.time}")
            print(f"  Service: {booking.service.name}")
            print(f"  Client: {booking.client.get_full_name()}")
            print(f"  Status: {booking.status}")
            print("---")
            
        # Test regroup logic (similar to template)
        from itertools import groupby
        from operator import attrgetter
        
        # Sort by date first (groupby requires sorted data)
        sorted_bookings = sorted(upcoming_bookings, key=attrgetter('date'))
        
        print("\n📊 Grouped by date (like template regroup):")
        for booking_date, group in groupby(sorted_bookings, key=attrgetter('date')):
            bookings_list = list(group)
            print(f"  {booking_date}: {len(bookings_list)} booking(s)")
            for booking in bookings_list:
                print(f"    - {booking.time}: {booking.service.name}")
                
        # Check if there are any issues with the date filtering
        print(f"\n🔍 Debug info:")
        print(f"  Today's date: {today}")
        print(f"  Date filter condition: date__gte={today}")
        print(f"  Status filter condition: status__in=['Waiting', 'On-going']")
        
        # Show all appointments with dates for comparison
        all_appointments = Appointment.objects.filter(artist=artist).order_by('date')
        print(f"\n📅 All appointments by date:")
        for apt in all_appointments:
            meets_date_filter = apt.date >= today
            meets_status_filter = apt.status in ['Waiting', 'On-going']
            print(f"  {apt.date}: {apt.service.name} ({apt.status}) - Date OK: {meets_date_filter}, Status OK: {meets_status_filter}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_dashboard_data()
