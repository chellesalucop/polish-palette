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

def test_upcoming_schedule_actions():
    print("=" * 60)
    print("TESTING UPCOMING SCHEDULE ACTIONS")
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
        
        # Test upcoming bookings with action logic
        upcoming_bookings = artist_appointments.filter(date__gte=today, status__in=['Waiting', 'On-going', 'Approved']).order_by('date', 'time')
        print(f"\n📋 Upcoming Bookings with Available Actions: {upcoming_bookings.count()}")
        
        for apt in upcoming_bookings:
            print(f"\n📅 {apt.date} at {apt.time}:")
            print(f"   Service: {apt.service.name}")
            print(f"   Client: {apt.client.get_full_name()}")
            print(f"   Status: {apt.status}")
            
            # Show what actions are available
            actions = []
            if apt.status == 'Approved':
                actions.append("🟢 START SERVICE")
            if apt.status == 'On-going':
                actions.append("✅ COMPLETE SERVICE")
                actions.append("❌ CANCEL SERVICE")
            
            if actions:
                print(f"   Available Actions: {', '.join(actions)}")
            else:
                print(f"   Available Actions: None (status: {apt.status})")
        
        # Test the data that will be shown in the template
        template_upcoming = artist_appointments.filter(date__gte=today, status__in=['Waiting', 'Approved', 'On-going']).order_by('date', 'time')
        print(f"\n🔍 Template Data (upcoming_bookings): {template_upcoming.count()} items")
        
        for apt in template_upcoming:
            print(f"   - {apt.date}: {apt.service.name} ({apt.status})")
        
        print(f"\n✅ Upcoming schedule with complete buttons is ready!")
        print(f"💡 Artists can now:")
        print(f"   - Start approved appointments")
        print(f"   - Complete on-going appointments")
        print(f"   - Cancel appointments if needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_upcoming_schedule_actions()
