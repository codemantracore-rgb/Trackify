from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView,GenericAPIView,CreateAPIView,DestroyAPIView
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .permissions import IsPlayListOwner

from .permissions import MusicPermission
from .serializers import MusicSerializer,PlayListSerializer,AddMusicSerializer,UserPrefrenceSerializer
from .models import Music,Playlist,PlayListTrack
from django.contrib.auth.models import User
from.recommendation import order_music_for_user

class MusicView(GenericAPIView):
    queryset=Music.objects.all().order_by('id')
    serializer_class=MusicSerializer
    permission_classes=[MusicPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(artist__name__icontains=search)
                | Q(genre__type__icontains=search)
                | Q(language__name__icontains=search)
            ).distinct()
        return queryset

    def get(self,request,*args,**kwargs):
        # music=self.paginate_queryset(self.queryset)
        # serializer=self.get_serializer(music,many=True)
        # return self.get_paginated_response(serializer.data)
        ordered_music = order_music_for_user(request.user, self.get_queryset())
        page = self.paginate_queryset(ordered_music)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,*args,**kwargs):
        music=self.get_object()
        music.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self,request,*args,**kwargs):
        music=self.get_object()
        serializer=self.get_serializer(music,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)
    

class PlaylistView(ModelViewSet):
    # queryset=Playlist.objects.all()
    serializer_class=PlayListSerializer
    # pagination_class=PlayListPagination
    permission_classes=[IsAuthenticated, IsPlayListOwner]
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
    def get_queryset(self):
        return Playlist.objects.filter(is_public=True)

from django.core.exceptions import PermissionDenied
class AddMusicView(CreateAPIView, DestroyAPIView):
    serializer_class = AddMusicSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return PlayListTrack.objects.filter(
            playlist__user=self.request.user
        )
    def perform_create(self, serializer):
        playlist = serializer.validated_data['playlist']
        if playlist.user != self.request.user:
            raise PermissionDenied("You don't own this playlist.")
        serializer.save(
            position=playlist.playlisttrack_set.count() + 1
        )
        
class DeleteMusicView(DestroyAPIView):
    serializer_class = MusicSerializer
    permission_classes = [IsAuthenticated]
    queryset = PlayListTrack.objects.all()

    def get_queryset(self):
        return PlayListTrack.objects.filter(
            playlist__user=self.request.user
        )

    def perform_destroy(self, instance):
        instance.delete()

class UserPrefrenceView(CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=UserPrefrenceSerializer
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
    
# from rest_framework.generics import GenericAPIView
# from rest_framework.mixins import (
#     ListModelMixin,
#     CreateModelMixin,
#     RetrieveModelMixin,
#     UpdateModelMixin,
#     DestroyModelMixin
# )

# class MovieView(
#     ListModelMixin,
#     CreateModelMixin,
#     RetrieveModelMixin,
#     UpdateModelMixin,
#     DestroyModelMixin,
#     GenericAPIView
# ):

#     queryset = Music.objects.all()
#     serializer_class = MusicSerializer

#     def get(self, request, *args, **kwargs):
#         if 'pk' in kwargs:
#             return self.retrieve(request, *args, **kwargs)
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)





            


