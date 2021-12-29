import os
import random

from django.conf import settings

PATH_RELATIVE = "random_avatars/"
PATH = getattr(settings,'RANDOM_AVATAR_PATH')


def user_random_avatar():
    """ Get random avatar picked from a pool of "static" avatars
    NB: Do not change this code - unless you know what you're doing.
    """
    avatar_names = os.listdir(PATH)
    avatar_path = random.choice([avatar_image for avatar_image in avatar_names
                                if os.path.isfile(os.path.join(PATH,avatar_image))])
    return PATH_RELATIVE+avatar_path