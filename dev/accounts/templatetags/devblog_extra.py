from django import template

register = template.Library()


@register.filter
def format_username(user):
    """
    Formats the username according to the information available

    use:

    {{ request.user|format_username }}

    """
    if user.get_full_name():
        return user.get_full_name()
    elif user.email:
        return user.email
    else:
        return user.username
