from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .recommendation import order_music_for_user
from .models  import UserPrefrence
@receiver(post_save,sender=UserPrefrence)
def clear_preference_after_listening(sender,instance,**kwargs):
    order_music_for_user(instance.user_id)
    
@receiver(post_delete,sender=UserPrefrence)
def clear_preference_after_listening(sender,instance,**kwargs):
    order_music_for_user(instance.user_id)

