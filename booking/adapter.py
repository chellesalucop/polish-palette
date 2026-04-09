from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

def safe_send_mail(subject, message, from_email, recipient_list, fail_silently=False):
    """Send email with graceful fallback for network errors"""
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Don't raise the exception - let the login continue
        return False
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
        subject = "Two-Factor Authentication Code - Polish Palette"
        if is_new_user:
            message = f"""Hello {first_name},

Welcome to Polish Palette! 

To complete your Google OAuth registration and secure your account, please enter the following verification code:

Your 2FA code is: {otp}

This code expires in 10 minutes.

If you did not create this account, please ignore this email.

Polish Palette Team
"""
        else:
            message = f"""Hello {first_name},

You are logging into your Polish Palette account via Google.

Your 2FA code is: {otp}

This code expires in 10 minutes.

If you did not attempt to login, please secure your account immediately.

Polish Palette Team
"""
        
        email_sent = safe_send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        
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
