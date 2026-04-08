from django.core.management.base import BaseCommand
from booking.models import Artist, ArtistAvailability


class Command(BaseCommand):
    help = 'Create default availability for all artists who do not have one'

    def handle(self, *args, **options):
        artists_without_availability = Artist.objects.filter(
            is_active_employee=True
        ).filter(
            availability__isnull=True
        )
        
        created_count = 0
        updated_count = 0
        
        for artist in artists_without_availability:
            availability = ArtistAvailability.create_default_availability(artist)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created default availability for artist: {artist.get_full_name()}'
                )
            )
        
        # Also update existing artists to ensure they have proper availability
        existing_artists = Artist.objects.filter(
            is_active_employee=True
        ).filter(
            availability__isnull=False
        )
        
        for artist in existing_artists:
            availability = artist.availability
            # Only update if critical fields are missing
            if not availability.monday_start or not availability.monday_end:
                ArtistAvailability.create_default_availability(artist)
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Updated incomplete availability for artist: {artist.get_full_name()}'
                    )
                )
        
        total_processed = created_count + updated_count
        if total_processed > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {total_processed} artists '
                    f'({created_count} created, {updated_count} updated)'
                )
            )
        else:
            self.stdout.write(
                self.style.INFO('All artists already have availability set up.')
            )
