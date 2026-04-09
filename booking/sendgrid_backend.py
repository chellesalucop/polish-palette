"""
SendGrid Email Backend for Polish Palette
Bypasses SMTP port restrictions on cloud platforms
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

class SendGridEmailBackend(BaseEmailBackend):
    """
    SendGrid API email backend that bypasses SMTP port restrictions
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")
    
    def send_messages(self, email_messages):
        """
        Send email messages using SendGrid API
        """
        if not email_messages:
            return
        
        try:
            sg = SendGridAPIClient(self.api_key)
            
            for message in email_messages:
                # Create SendGrid email
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=message.body,
                )
                
                # Send email
                response = sg.send(mail)
                
                if response.status_code == 202:
                    logger.info(f"Email sent successfully to {message.to}")
                else:
                    logger.error(f"Failed to send email to {message.to}: {response.status_code} {response.body}")
                    
        except Exception as e:
            logger.error(f"SendGrid API error: {str(e)}")
            raise
    
    def send_message(self, message):
        """Send a single message"""
        return self.send_messages([message])
