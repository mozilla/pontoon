from django import template


# We must redefine user_theme and theme_class with a new decorator in order
# to use them in a Django template, such as in django/base.html

register = template.Library()


@register.filter
def user_theme(user):
    """Get user's theme or return 'system' if user is not authenticated."""
    if user.is_authenticated:
        return user.profile.theme
    return "system"


@register.filter
def theme_class(request):
    """Get theme class name based on user preferences and system settings."""
    theme = "system"
    user = request.user

    if user.is_authenticated:
        theme = user.profile.theme

    if theme == "system":
        theme = request.COOKIES.get("system_theme", "system")

    return f"{theme}-theme"
