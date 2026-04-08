from django.shortcuts import redirect
from functools import wraps

def artist_login_required(view_func):
    """
    Custom decorator that handles both Django auth and session-based auth for artists.
    This allows standalone artists (without Client users) to access artist views.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check for Django auth with linked Client user
        if hasattr(request.user, 'artist'):
            request.artist = request.user.artist
            return view_func(request, *args, **kwargs)

        # Check for session-based auth for standalone artists
        if request.session.get('artist_authenticated') and request.session.get('artist_id'):
            try:
                from .models import Artist
                artist = Artist.objects.get(id=request.session['artist_id'])
                request.artist = artist
                return view_func(request, *args, **kwargs)
            except Artist.DoesNotExist:
                # Clear invalid session
                request.session.pop('artist_authenticated', None)
                request.session.pop('artist_id', None)

        # Not authenticated as artist - redirect to login
        return redirect('artist_login')

    return wrapper
