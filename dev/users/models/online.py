from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError, models as m

from dev.core.conf import Dev


class Online(m.Model):
    """ Online model for Devio users online-status """
    user = m.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        related_name="online_tracker",
        on_delete=m.CASCADE,
    )
    last_click = m.DateTimeField(default=timezone.now)


    def __str__(self):
        return "{} online status".format(self.user.username)


    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            pass  


    @classmethod
    def update_or_create_online_status_for_user(cls,user):
        """
        use in middleware to update users timelapse
        """
        cls.objects.update_or_create(user=user,defaults={'last_click': timezone.now()})
            

    @property
    def is_online(self):
        # cache me!
        online_trackers = self.__class__.online_status().select_related("user")
        if self.user in [tracker.user for tracker in online_trackers]:
            return True
        return False


    @classmethod
    def online_status(cls,cut_off=timedelta(minutes=Dev.settings["online_timeout"])):

        timelapse = timezone.now() - cut_off
        return cls.objects.filter(last_click__gte=timelapse).order_by("-last_click")


    @classmethod
    def users_open_and_hidden_online_status_stats(cls):

        hidden = []
        public = []

        online_trackers = cls.online_status().select_related("user")
        users = [tracker.user for tracker in online_trackers]

        for user in users:
            if user.is_online_presence_hidden:
                hidden.append(user)
            else:
                public.append(user)

        return dict(hidden_=hidden,public_=public)


    @classmethod
    def stats(cls):
        # cache me!
        data = {
        "Online Users counts : ":cls.online_status().count(),
        "Users online : ":[user_online.user for user_online in cls.online_status().select_related("user")],
        "Private online status counts": len(cls.users_open_and_hidden_online_status_stats()["hidden_"]),
        "Public online status counts":len(cls.users_open_and_hidden_online_status_stats()["public_"]),
        }
        return data
