from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .recommendation import _delete_cache
from .models  import UserPrefrence
@receiver(post_save,sender=UserPrefrence)
def clear_preference_after_listening(sender,instance,**kwargs):
    _delete_cache(instance.user_id)
    
@receiver(post_delete,sender=UserPrefrence)
def clear_preference_after_listening(sender,instance,**kwargs):
    _delete_cache(instance.user_id)

