from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/artist/(?P<artist_id>\d+)/$', consumers.ArtistBookingConsumer.as_asgi()),
    re_path(r'ws/reschedule/artist/(?P<artist_id>\d+)/$', consumers.RescheduleConsumer.as_asgi()),
    re_path(r'ws/booking/client/(?P<client_id>\d+)/$', consumers.ClientBookingConsumer.as_asgi()),
]
