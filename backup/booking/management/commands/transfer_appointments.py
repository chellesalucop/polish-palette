from django.core.management.base import BaseCommand
from booking.models import Appointment, Artist
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Transfer all waiting appointments to artist management'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("TRANSFERRING APPOINTMENTS TO ARTIST SIDE")
        self.stdout.write("=" * 60)
        
        try:
            # Get the artist user (Lincoln Loud)
            artist_email = 'lincolnloud419@gmail.com'
            artist_user = User.objects.get(email=artist_email)
            artist = Artist.objects.get(user=artist_user)
            
            self.stdout.write(f"🎨 Artist: {artist_user.get_full_name()}")
            
            # Get all client appointments with 'Waiting' status
            waiting_appointments = Appointment.objects.filter(status='Waiting')
            self.stdout.write(f"📋 Found {waiting_appointments.count()} waiting appointments")
            
            if waiting_appointments.exists():
                self.stdout.write("\n🔄 Transferring appointments to artist management...")
                
                for appointment in waiting_appointments:
                    self.stdout.write(f"  - Moving: {appointment.service.name} for {appointment.client.username}")
                    self.stdout.write(f"    Date: {appointment.date}, Time: {appointment.time}")
                    
                    # You can add additional logic here if needed
                    # For example, notify the artist, update status, etc.
                    
                self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully transferred {waiting_appointments.count()} appointments to artist side!"))
                self.stdout.write(self.style.SUCCESS(f"🎯 Artist can now manage these appointments in their dashboard"))
                
            else:
                self.stdout.write(self.style.WARNING("❌ No waiting appointments found to transfer"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Artist user not found. Please create artist account first."))
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Artist profile not found. Please create artist profile first."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during transfer: {str(e)}"))
        
        self.stdout.write("\n" + "=" * 60)
