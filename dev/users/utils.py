import random

from django.conf import settings

# max 13 colors & provide user options to change and pick others.
DEFAULT_PREDEFINED_COLORS_FOR_USER_THEMES = (
    "#916e0c",
    "#83910c",
    "#0c7291",
    "#28a745",
    "#343a40",
    "#212529",
    "#46856a",
    "#854646",
    "#a54c4c",
    "#a58e4c",
    "#816c32",
    "#327681",
    "#6e287a",
)

PREDEFINED_COLORS = getattr(settings, "PREDEFINED_COLORS", DEFAULT_PREDEFINED_COLORS_FOR_USER_THEMES)

def generate_random_predefined_hex_color():
    return random.choice(PREDEFINED_COLORS)
