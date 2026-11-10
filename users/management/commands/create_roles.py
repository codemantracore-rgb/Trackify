from django.contrib.auth.models import Permission,User,Group
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from playlist.models import Music,Playlist
class Command(BaseCommand):
    help=" Works Perfectly as Expected "
    def handle(self,*args,**kwargs):
        admin,_=Group.objects.get_or_create(name='Admin')
        artist,_=Group.objects.get_or_create(name='Artist')
        listener,_=Group.objects.get_or_create(name='Listener')

        music_ct=ContentType.objects.get_for_model(Music)
        playlist_ct=ContentType.objects.get_for_model(Playlist)


        music_permission=Permission.objects.filter(
            content_type=music_ct
        )
        playlist_permission=Permission.objects.filter(
            content_type=playlist_ct
        )
        admin.permissions.set(
          
           list(music_permission)+
           list(playlist_permission)
         
        )
        

        artist.permissions.set(
            Permission.objects.filter(
            content_type=music_ct,
            codename__in=[
                'view_music'
                'update_music',
            ])

        )
        listener.permissions.set(
            Permission.objects.filter(
            content_type=playlist_ct,
            codename__in=[
                'view_music'
            ]
            )

        )

        self.stdout.write(
            self.style.SUCCESS("Done Permisions")
        )