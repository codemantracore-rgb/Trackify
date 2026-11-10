from django.urls import path, include
from .views import MusicView, PlaylistView,AddMusicView,DeleteMusicView,UserPrefrenceView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'playlist', PlaylistView, basename='playlist')

urlpatterns = [
    path('', MusicView.as_view(), name='music'),
    path('', include(router.urls)),
    path('add-music',AddMusicView.as_view(),name='add-music'),
    path('delete-music',DeleteMusicView.as_view(),name='delete-music'),
    path('listening-history',UserPrefrenceView.as_view(),name='listening-history')
]
# URL

# Method

# Function

# /music/

# GET

# Get all music

# /music/

# POST

# Create music

# /music/5/

# GET

# Get one music

# /music/5/

# PUT

# Update entire record

# /music/5/

# PATCH

# Update some fields

# /music/5/

# DELETE

# Delete music