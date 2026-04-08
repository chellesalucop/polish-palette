from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from booking.models import Artist

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an artist account with specified email (DEPRECATED - Use Django Admin instead)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('This command is deprecated. Please use Django Admin to create artist accounts.'))
        self.stdout.write(self.style.WARNING('Go to /admin in your browser to manage artist accounts.'))
        
        # For backward compatibility, update existing artists if they exist
        email = 'lincolnloud419@gmail.com'
        password = 'artist123'
        
        try:
            # Find existing user
            user = User.objects.get(email=email)
            
            # Create or update Artist record linked to the user
            artist, artist_created = Artist.objects.update_or_create(
                user=user,
                defaults={
                    'email': email,
                    'password': password,  # Will be auto-hashed by model save method
                    'status': 'Available',
                    'is_active_employee': True,
                }
            )

            if artist_created:
                self.stdout.write(self.style.SUCCESS(f'Artist profile created for: {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'Artist profile already existed for: {email}'))

            self.stdout.write(self.style.SUCCESS(f'\n🎨 Artist Login Details:'))
            self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
            self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
            self.stdout.write(self.style.SUCCESS(f'   Status: {artist.status}'))
            self.stdout.write(self.style.WARNING(f'\n⚠️  Please use Django Admin for future artist account management.'))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {email} not found.'))
            self.stdout.write(self.style.ERROR(f'Create the user account first, then use Django Admin to create the artist profile.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Please use Django Admin to create artist accounts.'))
