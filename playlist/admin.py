from django.contrib import admin
from .models import Music,Artist,Genre,Language,PlayListTrack,Playlist
# Register your models here.
@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_filter=['artist','title']
    read_only_fields=['unique_hash',]

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_filter=['name','language']
    
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_filter=['type','artist']

admin.site.register(Language)
admin.site.register(PlayListTrack)
admin.site.register(Playlist)


