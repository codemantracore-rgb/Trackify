from django.db import models
# from django.contrib.auth.models import User
import hashlib,json
from django.db.models.functions import Lower

class Language(models.Model):
    name=models.CharField()
    def __str__(self):
        return self.name
    class Meta:
        constraints=[
            models.UniqueConstraint(
                Lower('name'),name='case-insensitive-1'
            )
        ]

class Artist(models.Model):
    name=models.CharField()
    language=models.ManyToManyField(Language,related_name='artists')
    def __str__(self):
        return self.name
    class Meta:
        constraints=[
            models.UniqueConstraint(
                Lower('name'),name='case-insensitive-2'
            )
        ]
        permissions=[('upload_music','Can upload Music'),('approve_music','Can approve music')]

# Create your models here.
class Music(models.Model):
    title=models.CharField()
    description=models.TextField()
    language=models.ManyToManyField(Language,related_name='language')
    artist=models.ManyToManyField(Artist,related_name='artists')
    genre=models.ManyToManyField("Genre")
    audio_file=models.FileField(upload_to='music/audio/',null=True)
    cover_image=models.ImageField(upload_to='music/images/',null=True)
    duration=models.BigIntegerField()
    file_size=models.BigIntegerField()
    bitrate=models.BigIntegerField()
    samples=models.PositiveIntegerField()
    channels=models.SmallIntegerField()
    is_active=models.BooleanField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    unique_hash=models.CharField(blank=False,editable=False,unique=True)
    
    def generate_unique_hash(self):
        artist_id=sorted(self.artist.values_list('id',flat=True))
        language_id=sorted(self.language.values_list('id',flat=True))
        data={
            'title':self.title.strip(),
            'artist':artist_id,
            'language':language_id
        }
        serialized=json.dumps(data,sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    def __str__(self):
        return self.title
    # class Meta:
    #     constraints=[
    #         models.UniqueConstraint(fields=['title','artist','language'],name='unique-music')
    #     ]
    class Meta:
        constraints=[
            models.UniqueConstraint(
                Lower('title'),name='case-insensitive-3'
            )
        ]

class Genre(models.Model):
    type=models.CharField()
    artist=models.ManyToManyField(Artist,related_name='Genres')
    def __str__(self):
        return self.type
    class Meta:
        constraints=[
            models.UniqueConstraint(
                Lower('type'),name='case-insensitive-4'
            )
        ]
        
from django.conf import settings

class Playlist(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='playlists')
    title=models.TextField()
    # desription=models.TextField()
    music = models.ManyToManyField(Music,through='PlayListTrack', related_name="playlists", blank=True)
    is_public=models.BooleanField()
    def __str__(self):
        return self.title
    class Meta:
        ordering=['id']

class PlayListTrack(models.Model):
    playlist=models.ForeignKey(Playlist,on_delete=models.CASCADE)
    music=models.ForeignKey(Music,on_delete=models.CASCADE)
    position=models.PositiveIntegerField()
    class Meta:
        ordering=['position']
    # def __str__(self):
    #     return self.playlist
from django.conf import settings
class UserPrefrence(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    music=models.ForeignKey(Music,on_delete=models.CASCADE)
    listened_duration=models.PositiveIntegerField()
    completed=models.BooleanField()
    skipped=models.BooleanField()
    liked=models.BooleanField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']


