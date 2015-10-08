from django.contrib.auth.decorators import user_passes_test


"""Decorator for views that can only be access by a superuser."""
superuser_required = user_passes_test(lambda u: u.is_superuser)
