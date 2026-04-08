from django.core.management.base import BaseCommand
from booking.models import Artist, Appointment
from datetime import date

class Command(BaseCommand):
    help = 'Check upcoming schedule for artist'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("CHECKING UPCOMING SCHEDULE FOR ARTIST")
        self.stdout.write("=" * 60)
        
        # Get the artist
        try:
            artist = Artist.objects.first()
            if not artist:
                self.stdout.write(self.style.ERROR("❌ No artist found in database"))
                return
                
            self.stdout.write(f"🎨 Artist: {artist.user.get_full_name()} ({artist.user.email})")
            
            # Check upcoming bookings
            today = date.today()
            self.stdout.write(f"📅 Today's date: {today}")
            
            upcoming = Appointment.objects.filter(
                artist=artist, 
                date__gte=today, 
                status__in=['Waiting', 'On-going']
            ).order_by('date', 'time')
            
            self.stdout.write(f"📋 Upcoming bookings count: {upcoming.count()}")
            
            if upcoming.exists():
                self.stdout.write("\n📅 Upcoming Schedule:")
                for apt in upcoming[:10]:
                    self.stdout.write(f"  - {apt.date} at {apt.time}: {apt.service.name}")
                    self.stdout.write(f"    Client: {apt.client.get_full_name()}")
                    self.stdout.write(f"    Status: {apt.status}")
                    self.stdout.write("")
            else:
                self.stdout.write(self.style.WARNING("❌ No upcoming bookings found"))
                
            # Check all appointments for this artist
            all_appointments = Appointment.objects.filter(artist=artist)
            self.stdout.write(f"📊 Total appointments for artist: {all_appointments.count()}")
            
            # Show recent appointments
            recent = all_appointments.order_by('-date', '-time')[:5]
            if recent.exists():
                self.stdout.write("\n📅 Recent Appointments:")
                for apt in recent:
                    self.stdout.write(f"  - {apt.date} at {apt.time}: {apt.service.name} ({apt.status})")
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
        
        self.stdout.write("\n" + "=" * 60)
