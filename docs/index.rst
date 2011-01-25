===================================
Welcome to playdoh's documentation!
===================================

**Mozilla's Playdoh** is a web application template based on Django_.

Patches are welcome! Feel free to fork and contribute to this project on
Github_.

.. _Django: http://www.djangoproject.com/
.. _Github: https://github.com/mozilla/playdoh


Features
--------
Quick and dirty (and probably incomplete) feature list:

* Rich, but "cherry-pickable" features out of the box:

  * Django
  * jinja2 template engine
  * Celery support
  * Simple database migrations
  * Full localization support

* Secure by default:

  * SHA-512 default password hashing
  * X-Frame-Options: DENY by default
  * secure and httponly flags on cookies enabled by default


Contents
--------

.. toctree::
   :maxdepth: 1

   gettingstarted
   libs
   operations
   migrations
   l10n_setup
   l10n_update
   packages
   docs
   bestpractices


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
