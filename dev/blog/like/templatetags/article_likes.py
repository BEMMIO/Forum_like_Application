from django import template
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

register = template.Library()

@register.simple_tag
def likes_label(article):
    """
        template :  {% load article_likes %}
        
        use : {% likes_label article %}

        output :
            - edward likes this.
            - react, admin, edward and 1 other user like this.
            - react, edward, django and 2 other users like this.

        NOTE : resolve indexError

        {% if article.users_like %}

            {% likes_label article %}

        {% endif %}

    """
    last_likes = article.users_like or []

    usernames = []
    for user in last_likes[:3]:
        usernames.append(user.username)

    if len(usernames) == 1:
        return _("%(user)s likes this.") % {"user": usernames[0]}

    hidden_likes = len(article.users_like) - len(usernames)
    if len(last_likes) < 4:
        usernames_string = humanize_usernames_list(usernames)
    else:
        usernames_string = ", ".join(usernames)

    if not hidden_likes:
        return _("%(users)s like this.") % {"users": usernames_string}

    label = ngettext(
        "%(users)s and %(likes)s other user like this.",
        "%(users)s and %(likes)s other users like this.",
        hidden_likes,
    )
    formats = {"users": usernames_string, "likes": hidden_likes}

    return label % formats


def humanize_usernames_list(usernames):
    formats = {"users": ", ".join(usernames[:-1]), "last_user": usernames[-1]}

    return _("%(users)s and %(last_user)s") % formats
