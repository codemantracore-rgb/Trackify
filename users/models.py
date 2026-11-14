from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES=[('Listener','Listener'),('artist','artist')]
    role=models.CharField(choices=ROLE_CHOICES,default='Listener')
    email=models.EmailField(unique=True,blank=False)

class Artist(models.Model):
    name=models.TextField()
    bio=models.TextField()
    photo=models.ImageField(upload_to='artists/')
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['name'],name='artist-name')
        ]


# class Listener(model.model):
#     name=models.TextField()

class Follow(models.Model):
    artist=models.ForeignKey(Artist,on_delete=models.CASCADE)
    listener=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['artist','listener'],name='followers')
        ]
# class UserArtist(models.Model):


