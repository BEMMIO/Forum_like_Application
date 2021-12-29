from django.dispatch import Signal

invite_is_sent = Signal(providing_args=["invite"])
invite_is_accepted = Signal(providing_args=["invite"])


