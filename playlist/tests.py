from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from playlist.models import Music
from Trackify.asgi import application


class MusicSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.match = Music.objects.create(
            title="Search Match",
            description="A test track",
            duration=180,
            file_size=1000,
            bitrate=320,
            samples=44100,
            channels=2,
            is_active=True,
            unique_hash="search-match",
        )
        Music.objects.create(
            title="Other Track",
            description="A different track",
            duration=180,
            file_size=1000,
            bitrate=320,
            samples=44100,
            channels=2,
            is_active=True,
            unique_hash="other-track",
        )

    def test_search_filters_music_by_title(self):
        response = self.client.get("/music/", {"search": "search match"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [music["id"] for music in response.data["results"]],
            [self.match.id],
        )


class RecommendationWebSocketTests(TestCase):
    def test_authenticated_user_can_connect_and_disconnect(self):
        user = get_user_model().objects.create_user(
            username="websocket-user",
            password="test-password",
            email="websocket@example.com",
        )
        token = AccessToken.for_user(user)

        async def connect_and_disconnect():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/recommendations/?token={token}",
            )
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.disconnect()

        async_to_sync(connect_and_disconnect)()
