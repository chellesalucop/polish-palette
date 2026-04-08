"""
Management command: release_reschedule_locks

Finds any Appointment in 'Rescheduling' status whose soft-lock has expired,
reverts them to 'Waiting', and clears proposed slot fields.

Run this periodically (e.g. every 5 minutes via a cron / scheduled task):
    python manage.py release_reschedule_locks
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from booking.models import Appointment


class Command(BaseCommand):
    help = 'Release expired reschedule soft-locks and revert appointments to Waiting status.'

    def handle(self, *args, **options):
        expired = Appointment.objects.filter(
            status='Rescheduling',
            reschedule_lock_expires_at__lt=timezone.now(),
        )
        count = expired.count()
        if count:
            expired.update(
                status='Waiting',
                proposed_date=None,
                proposed_time=None,
                reschedule_lock_expires_at=None,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Released {count} expired reschedule lock(s).'
            ))
        else:
            self.stdout.write('No expired reschedule locks found.')
