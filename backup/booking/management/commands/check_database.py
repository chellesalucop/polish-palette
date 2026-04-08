from django.core.management.base import BaseCommand
from booking.models import Appointment, Service, Artist, Client

class Command(BaseCommand):
    help = 'Check database contents and display summary'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("DATABASE CHECK - What's in your database?")
        self.stdout.write("=" * 60)
        
        # Check Clients
        self.stdout.write("\n👥 CLIENTS:")
        clients = Client.objects.all()
        for client in clients:
            self.stdout.write(f"  - {client.username} ({client.email})")
        
        # Check Services
        self.stdout.write("\n💅 SERVICES:")
        services = Service.objects.all()
        for service in services:
            self.stdout.write(f"  - {service.name}: ₱{service.price} ({service.duration} mins)")
        
        # Check Artists
        self.stdout.write("\n🎨 ARTISTS:")
        artists = Artist.objects.all()
        for artist in artists:
            self.stdout.write(f"  - {artist.user.get_full_name()} ({artist.user.email})")
        
        # Check Appointments
        self.stdout.write("\n📋 APPOINTMENTS:")
        appointments = Appointment.objects.all()
        for apt in appointments:
            self.stdout.write(f"  - {apt.client.username} -> {apt.artist.user.get_full_name()}")
            self.stdout.write(f"    Service: {apt.service.name} on {apt.date} at {apt.time}")
            self.stdout.write(f"    Status: {apt.status}")
        
        self.stdout.write("\n" + "=" * 60)
