from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from booking.models import Appointment

class Command(BaseCommand):
    help = 'Send reminder emails to clients and artists 1 day before their appointments'

    def handle(self, *args, **options):
        # Calculate tomorrow's date
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Get all approved appointments for tomorrow
        appointments = Appointment.objects.filter(
            date=tomorrow,
            status='Approved'
        ).select_related('client', 'artist')
        
        self.stdout.write(f"Checking for {appointments.count()} appointments for tomorrow ({tomorrow})")
        
        for appt in appointments:
            try:
                # Prepare recipient list
                emails = []
                if appt.client and appt.client.email:
                    emails.append(appt.client.email)
                if appt.artist and appt.artist.email:
                    emails.append(appt.artist.email)
                
                if not emails:
                    continue
                
                # Format time for display
                time_str = appt.time.strftime('%I:%M %p')
                
                # Email content
                subject = f"Appointment Reminder: Tomorrow at {time_str} - Polish Palette"
                message = f"""Hello,

This is a friendly reminder that you have a nail appointment scheduled for tomorrow:

Date: {appt.date}
Time: {time_str}
Service: {appt.service.name}
Artist: {appt.artist.first_name if appt.artist else 'TBD'}

We look forward to seeing you then!

Polish Palette Team
"""
                
                # Send the email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    emails,
                    fail_silently=False
                )
                
                self.stdout.write(self.style.SUCCESS(f"Reminder sent for appointment {appt.id} to {', '.join(emails)}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error sending reminder for appt {appt.id}: {str(e)}"))
