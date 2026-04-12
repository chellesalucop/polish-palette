from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

def safe_send_mail(subject, message, from_email, recipient_list, fail_silently=False, max_retries=3):
    """Send email with retry logic for Gmail connectivity issues"""
    import time
    import socket
    import threading
    import queue
    
    # Use a queue to get the result back from the thread
    result_queue = queue.Queue()
    
    def send_email_thread():
        for attempt in range(max_retries):
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
                result_queue.put(True)
                return
            except (socket.error, ConnectionError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Email attempt {attempt + 1} failed: {e}. Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Failed to send email after {max_retries} attempts: {e}")
                    result_queue.put(False)
                    return
            except Exception as e:
                logger.error(f"Unexpected error sending email: {e}")
                result_queue.put(False)
                return
    
    # Start the email sending in a separate thread
    thread = threading.Thread(target=send_email_thread)
    thread.daemon = True  # Daemon thread won't prevent process exit
    thread.start()
    
    # Return True immediately (we'll log the actual result asynchronously)
    logger.info("Email sending started in background thread")
    return True

def safe_send_html_mail(subject, template_name, context, from_email, recipient_list, fail_silently=False, max_retries=3):
    """Send HTML email with retry logic for Gmail connectivity issues"""
    import time
    import socket
    import threading
    import queue
    from django.core.mail import EmailMultiAlternatives
    
    # Use a queue to get the result back from the thread
    result_queue = queue.Queue()
    
    def send_email_thread():
        try:
            # Render HTML template
            html_content = render_to_string(template_name, context)
            
            # Create email with HTML content
            email = EmailMultiAlternatives(
                subject=subject,
                body="",  # Plain text will be generated from HTML
                from_email=from_email,
                to=recipient_list
            )
            email.attach_alternative(html_content, "text/html")
            
            for attempt in range(max_retries):
                try:
                    email.send()
                    result_queue.put(True)
                    return
                except (socket.error, ConnectionError, OSError) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"HTML Email attempt {attempt + 1} failed: {e}. Retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error(f"Failed to send HTML email after {max_retries} attempts: {e}")
                        result_queue.put(False)
                        return
                except Exception as e:
                    logger.error(f"Unexpected error sending HTML email: {e}")
                    result_queue.put(False)
                    return
        except Exception as e:
            logger.error(f"Error rendering HTML email template: {e}")
            result_queue.put(False)
            return
    
    # Start the email sending in a separate thread
    thread = threading.Thread(target=send_email_thread)
    thread.daemon = True  # Daemon thread won't prevent process exit
    thread.start()
    
    # Return True immediately (we'll log the actual result asynchronously)
    logger.info("HTML Email sending started in background thread")
    return True
from django.conf import settings
from django.shortcuts import redirect
from .models import TwoFactorOTP

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This method is called when a user is about to login via social account.
        We can customize the user creation process here and implement 2FA.
        """
        # Debug: Print to see if this method is called
        print("\n" + "="*50)
        print(f"DEBUG: CustomSocialAccountAdapter.pre_social_login EXECUTING")
        print(f"DEBUG: Provider: {sociallogin.account.provider}")
        print("="*50 + "\n")
        
        # Check if 2FA is disabled
        if getattr(settings, 'DISABLE_TWO_FACTOR_AUTH', False):
            print("DEBUG: 2FA is disabled, proceeding with normal login")
            # Let the default adapter handle the login
            return
        
        # Get user data from Google
        user_data = sociallogin.account.extra_data
        email = user_data.get('email')
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')
        
        # Track whether this is a new user for messaging
        User = get_user_model()
        is_new_user = not User.objects.filter(email=email).exists()
        
        # Generate 2FA OTP for OAuth login
        otp_obj = TwoFactorOTP.generate_otp(email, 'google')
        otp = otp_obj.otp
        
        print(f"DEBUG: Generated OTP {otp} for {email}")

        # Send appropriate email message
        subject = "Two-Factor Authentication Code"
        context = {
            'user_name': first_name,
            'otp_code': otp,
            'subject': subject
        }
        email_sent = safe_send_html_mail(
            subject, 
            'emails/two_factor_otp.html', 
            context, 
            settings.DEFAULT_FROM_EMAIL, 
            [email], 
            fail_silently=False
        )
        
        if not email_sent:
            print(f"DEBUG: Email failed, but OTP code is: {otp}")
        else:
            print("DEBUG: Email sent, interrupting with 2FA verification")
        
        # Set session data for 2FA
        request.session['2fa_pending'] = True
        request.session['2fa_user_email'] = email
        request.session['2fa_login_method'] = 'google'
        request.session['is_signup'] = is_new_user
        
        # Serialize the sociallogin object to session
        request.session['pending_sociallogin_data'] = sociallogin.serialize()
        
        # CRITICAL: Use ImmediateHttpResponse to halt the allauth flow
        raise ImmediateHttpResponse(redirect('two_factor_verify'))

    def save_user(self, request, sociallogin, form=None):
        """
        Override save_user to prevent duplicate user creation
        """
        user = sociallogin.user
        user_data = sociallogin.account.extra_data
        email = user_data.get('email')
        
        # Check if user already exists before creating
        User = get_user_model()
        try:
            existing_user = User.objects.get(email=email)
            return existing_user
        except User.DoesNotExist:
            return super().save_user(request, sociallogin, form)
