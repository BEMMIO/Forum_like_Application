import django.dispatch
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save

from dev.users.models import User as model_cls
from .utils import user_random_avatar

"""
This signal assigns a randomly generated avatar to a new user.
"""
@receiver(pre_save,sender=model_cls)
def user_default_avatar_set_reciever(sender,instance,*args,**kwargs):
    if not (instance.avatar_tmp or instance.avatar_src):
        instance.avatar_tmp = user_random_avatar()
