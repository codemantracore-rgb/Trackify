from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Music,Genre,Language,Artist,Playlist,PlayListTrack,UserPrefrence
# Create your views here.
class MusicSerializer(ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='type',
        queryset=Genre.objects.all(),many=True
    )
    language=serializers.SlugRelatedField(slug_field='name',queryset=Language.objects.all(),many=True)
    artist=serializers.SlugRelatedField(slug_field='name',queryset=Artist.objects.all(),many=True)
    class Meta:
        model=Music
        fields="__all__"
from django.db.models import Q
class PlayListSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    music=MusicSerializer(many=True,read_only=True)
    def get_queryset(self):
        return Playlist.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        ).distinct()
    class Meta:
        model=Playlist
        fields="__all__"
        # read_only_fields = ['user']
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     request = self.context.get('request')

        # if request:
            # self.fields['user'].queryset = Playlist.objects.filter(
            #         user=request.user
            #     )
            # self.fields['playlist_name'].queryset = Playlist.objects.filter(
            #         user=request.user
            #     )
            # pass

class AddMusicSerializer(ModelSerializer):
    playlist_name = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Playlist.objects.all(),
        source='playlist'
    )
    music = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Music.objects.all()
    )
    class Meta:
        model = PlayListTrack
        fields = ['playlist_name', 'music']

class UserPrefrenceSerializer(ModelSerializer):
    music=serializers.SlugRelatedField(slug_field='title',queryset=Music.objects.all())
    class Meta:
        
        model = UserPrefrence
        fields="__all__"
        read_only_fields=['id','created_at','user']
    def validate_data(self,music):
        if not music.is_active:
            return serailizer.ValidationError("Validation failure")
        else:
            return music

# class UserPrefrence(models.Model):
#     user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     music=models.ForeignKey(Music,on_delete=models.CASCADE)
#     listened_duration=models.BooleanField()
#     completed=models.BooleanField()
#     skipped=models.BooleanField()
#     liked=models.BooleanField()
#     created_at=models.DateTimeField(auto_now_add=True)
#     class Meta:
#         ordering=['-created_at']