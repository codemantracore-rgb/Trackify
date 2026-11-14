
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        scope = dict(scope)

        query_string = scope.get(
            "query_string", b""
        ).decode("utf-8")

        token_values = parse_qs(
            query_string
        ).get("token", [])

        scope["user"] = AnonymousUser()

        if token_values:
            scope["user"] = await _get_token_from_user(
                token_values[0]
            )

        return await self.inner(scope, receive, send)


@database_sync_to_async
def _get_token_from_user(raw_token):

    try:
        authentication = JWTAuthentication()

        validated_token = authentication.get_validated_token(
            raw_token
        )

        return authentication.get_user(validated_token)

    except Exception as e:
        print("JWT Authentication Error:", e)
        return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
