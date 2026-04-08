import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ArtistBookingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time booking updates for artists.
    The artist connects to ws/artist/<artist_id>/
    """

    async def connect(self):
        self.artist_id = self.scope['url_route']['kwargs']['artist_id']
        self.group_name = f'artist_booking_{self.artist_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # Security: only the artist whose id matches may connect
        artist = await self._get_artist_for_user(user)
        if not artist or str(artist.id) != str(self.artist_id):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def booking_update(self, event):
        """Forward booking update event payload to the connected WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def _get_artist_for_user(self, user):
        try:
            # Check if user has linked artist (Django auth)
            if hasattr(user, 'artist'):
                return user.artist
            # For standalone artists, check session-based auth
            return None
        except Exception:
            return None


class RescheduleConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time reschedule notifications.
    The artist connects to ws/reschedule/artist/<artist_id>/
    The server pushes reschedule lifecycle events to that group.
    """

    async def connect(self):
        self.artist_id = self.scope['url_route']['kwargs']['artist_id']
        self.group_name = f'reschedule_artist_{self.artist_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # Security: only the artist whose id matches may connect
        artist = await self._get_artist_for_user(user)
        if not artist or str(artist.id) != str(self.artist_id):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Artists only receive; they do not send through this socket.
    async def receive(self, text_data):
        pass

    # -- group message handler --
    async def reschedule_event(self, event):
        """Forward any reschedule event payload to the connected WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def _get_artist_for_user(self, user):
        try:
            return user.artist
        except Exception:
            return None


class ClientBookingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time booking status updates for clients.
    The client connects to ws/booking/client/<client_id>/
    """

    async def connect(self):
        self.client_id = self.scope['url_route']['kwargs']['client_id']
        self.group_name = f'booking_client_{self.client_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # Security: only the client whose id matches may connect
        if str(user.id) != str(self.client_id):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def booking_update(self, event):
        """Forward booking update event payload to the connected WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))
