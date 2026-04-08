#!/usr/bin/env python
import os
import sys
import django

# Add project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nail_booking.settings')
django.setup()

from booking.models import Appointment, Artist
from django.contrib.auth import get_user_model

User = get_user_model()

def transfer_appointments_to_artist():
    print("=" * 60)
    print("TRANSFERRING APPOINTMENTS TO ARTIST SIDE")
    print("=" * 60)
    
    try:
        # Get the artist user (Lincoln Loud)
        artist_email = 'lincolnloud419@gmail.com'
        artist_user = User.objects.get(email=artist_email)
        artist = Artist.objects.get(user=artist_user)
        
        print(f"🎨 Artist: {artist_user.get_full_name()}")
        
        # Get all client appointments with 'Waiting' status
        waiting_appointments = Appointment.objects.filter(status='Waiting')
        print(f"📋 Found {waiting_appointments.count()} waiting appointments")
        
        if waiting_appointments.exists():
            print("\n🔄 Transferring appointments to artist management...")
            
            for appointment in waiting_appointments:
                print(f"  - Moving: {appointment.service.name} for {appointment.client.username}")
                print(f"    Date: {appointment.date}, Time: {appointment.time}")
                
                # You can add additional logic here if needed
                # For example, notify the artist, update status, etc.
                
            print(f"\n✅ Successfully transferred {waiting_appointments.count()} appointments to artist side!")
            print(f"🎯 Artist can now manage these appointments in their dashboard")
            
        else:
            print("❌ No waiting appointments found to transfer")
            
    except User.DoesNotExist:
        print("❌ Artist user not found. Please create artist account first.")
    except Artist.DoesNotExist:
        print("❌ Artist profile not found. Please create artist profile first.")
    except Exception as e:
        print(f"❌ Error during transfer: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    transfer_appointments_to_artist()
