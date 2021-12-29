from django.dispatch import Signal
from django.dispatch import receiver

from .signals import *


@receiver(invite_is_accepted)
def invite_is_accepted_reciever_func(sender,**kwargs):

	invitation = kwargs["invite"]
	invitation.invite_accepted()


@receiver(invite_is_sent)
def invite_is_sent_reciever_func(sender,**kwargs):

	print("Invitation sent SIGNAL")