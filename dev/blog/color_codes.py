import random

from django.conf import settings

# extend w/ 30 more colors
DEFAULT_PREDEFINED_COLORS = (
    "#fce94f",
    "#edd400",
    "#c4a000",
    "#8ae234",
    "#73d216",
    "#23863a",
    "#545b62",
    "#537faf",
    "#4e9a06",
    "#d3d7cf",
    "#fcaf3e",
    "#f57900",
    "#ce5c00",
    "#729fcf",
    "#3465a4",
    "#204a87",
    "#888a85",
    "#ad7fa8",
    "#75507b",
    "#333333",
    "#5c3566",
    "#ef2929",
    "#cc0000",
    "#a40000",
    "#00b6c4"
)

PREDEFINED_COLORS = getattr(settings, "PREDEFINED_COLORS", DEFAULT_PREDEFINED_COLORS)

def generate_random_predefined_hex_color():
    return random.choice(PREDEFINED_COLORS)
