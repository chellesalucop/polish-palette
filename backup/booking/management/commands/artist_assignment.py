from django.core.management.base import BaseCommand
from booking.models import Appointment, Artist
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix artist assignments for all appointments'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("FIXING ARTIST ASSIGNMENTS")
        self.stdout.write("=" * 60)
        
        try:
            # Get the correct artist (Lincoln Loud)
            artist_email = 'lincolnloud419@gmail.com'
            artist_user = User.objects.get(email=artist_email)
            correct_artist = Artist.objects.get(user=artist_user)
            
            self.stdout.write(f"🎨 Target Artist: {correct_artist.user.get_full_name()}")
            
            # Get all appointments and reassign them to Lincoln Loud
            appointments = Appointment.objects.all()
            self.stdout.write(f"📋 Found {appointments.count()} appointments")
            
            updated_count = 0
            for appointment in appointments:
                if appointment.artist.user.email != artist_email:
                    self.stdout.write(f"  - Reassigning: {appointment.service.name}")
                    self.stdout.write(f"    From: {appointment.artist.user.get_full_name()}")
                    self.stdout.write(f"    To: {correct_artist.user.get_full_name()}")
                    self.stdout.write(f"    Client: {appointment.client.username}")
                    
                    # Reassign to correct artist
                    appointment.artist = correct_artist
                    appointment.save()
                    updated_count += 1
                    self.stdout.write(f"    ✅ Updated!")
                    self.stdout.write("  " + "-" * 40)
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully updated {updated_count} appointments!"))
            self.stdout.write(self.style.SUCCESS(f"🎯 All appointments now assigned to {correct_artist.user.get_full_name()}"))
            
            # Verify the update
            self.stdout.write(f"\n🔍 VERIFICATION:")
            for appointment in Appointment.objects.filter(status='Waiting'):
                self.stdout.write(f"  - {appointment.service.name} by {appointment.client.username}")
                self.stdout.write(f"    Artist: {appointment.artist.user.get_full_name()}")
                self.stdout.write(f"    Status: {appointment.status}")
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Artist user not found."))
        except Artist.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Artist profile not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during update: {str(e)}"))
        
        self.stdout.write("\n" + "=" * 60)
