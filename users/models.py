from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES=[('Listener','Listener'),('artist','artist')]
    role=models.CharField(choices=ROLE_CHOICES,default='Listener')
    email=models.EmailField(unique=True,blank=False)