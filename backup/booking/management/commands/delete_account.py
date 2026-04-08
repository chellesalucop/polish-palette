from django.core.management.base import BaseCommand
from django.db import transaction
from booking.models import Client, Artist

class Command(BaseCommand):
    help = 'Delete a user account by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the account to delete')

    def handle(self, *args, **options):
        email = options['email']
        
        with transaction.atomic():
            # Try to find and delete Client account
            try:
                client = Client.objects.get(email=email)
                client_name = f"{client.first_name} {client.last_name}"
                client.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted Client account: {client_name} ({email})')
                )
                return
            except Client.DoesNotExist:
                pass
            
            # Try to find and delete Artist account
            try:
                artist = Artist.objects.select_related('user').get(user__email=email)
                artist_name = artist.user.get_full_name()
                artist.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted Artist account: {artist_name} ({email})')
                )
                return
            except Artist.DoesNotExist:
                pass
            
            # No account found
            self.stdout.write(
                self.style.ERROR(f'No account found with email: {email}')
            )
