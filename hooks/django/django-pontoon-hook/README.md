django-pontoon-hook
===================

django-pontoon-hook makes a Django project ready to use [Pontoon][1]'s services
for interactive localization.

[1]: https://github.com/mathjazz/pontoon

installation
============

 1. Add 'pontoon_hook' to your settings.INSTALLED_APPS.
 2. Add 'pontoon_hook.middleware.PontoonMiddleware' to your settings.MIDDLEWARE_CLASSES
    preferably as the last item or as later as possible.
