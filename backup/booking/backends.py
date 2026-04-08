from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from booking.models import Client, Artist

class CustomAuthBackend(BaseBackend):
    """
    Custom authentication backend that supports both Client and Artist models.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate user against the Client model.
        Supports both 'email' and 'username' keyword arguments as the fallback.
        """
        if email is None:
            email = kwargs.get('username')
            
        if not email:
            return None
            
        try:
            client = Client.objects.get(email=email)
            if client.check_password(password):
                return client
        except Client.DoesNotExist:
            pass
        
        return None
    
    def get_user(self, user_id):
        """
        Retrieve user by ID from the Client model.
        """
        try:
            return Client.objects.get(pk=user_id)
        except Client.DoesNotExist:
            return None
