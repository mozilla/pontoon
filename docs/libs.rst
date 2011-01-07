=========
Libraries
=========

There are a number of libraries that either come bundled with playdoh or are
otherwise useful for it.

**Note:** Libraries marked with an \*asterisk\* are bundled with playdoh by default. 


Python
======

Database
--------

* `django-multidb-router <https://github.com/jbalogh/django-multidb-router>`_:
  Round-robin master/slave db router for Django 1.2.
* `schematic <https://github.com/jbalogh/schematic>`_\*:
  Simple database migration tool.

Deferred Execution (cron, message queues)
-----------------------------------------

* `django-celery <https://github.com/ask/django-celery>`_\*:
  Celery integration for Django.
* `django-cronjobs <https://github.com/jsocol/django-cronjobs>`_:
  A simple cron-running management command for Django.
* `django-gearman <https://github.com/fwenzel/django-gearman>`_:
  A convenience wrapper for Gearman clients and workers in Django/Python.

Internationalization (i18n) and Localization (L10n)
---------------------------------------------------

* `Babel <http://babel.edgewall.org/>`_:
  A collection of tools for internationalizing Python applications.
* `pytz <http://pytz.sourceforge.net/>`_:
  World Timezone Definitions for Python.
* `tower <https://github.com/clouserw/tower>`_\*:
  A library that builds on Babel and Jinja2 to make extracting strings easy and
  uniform.

Middleware
----------

* `commonware <http://github.com/jsocol/commonware>`_\*:
  Middlewares and other stuff we share.

Mozilla
-------

* `django-moz-header <https://github.com/mozilla/django-moz-header>`_:
  Common header/footer templates and CSS for Django-based Mozilla sites.
* `django-mozilla-product-details <http://github.com/fwenzel/django-mozilla-product-details>`_:
  Pulls Mozilla product details library data from SVN and makes it available
  as Python dictionaries.

Security and Data Sanitization
------------------------------

* `bleach <https://github.com/jsocol/bleach>`_:
  An easy, HTML5, whitelisting HTML sanitizer.
* `django-sha2 <http://github.com/fwenzel/django-sha2>`_\*:
  Monkey-patches SHA-256 and SHA-512 support into Django.
* `happyforms <https://github.com/jbalogh/happyforms>`_:
  Extension to Django Forms that strips spaces.

Templates and Caching
---------------------

* `django-cache-machine <https://github.com/jbalogh/django-cache-machine>`_:
  Automatic caching and invalidation for Django models through the ORM.
* `jingo <https://github.com/jbalogh/jingo>`_\*:
  An adapter for using Jinja2 templates with Django.
* `jingo-minify <https://github.com/jsocol/jingo-minify>`_\*:
  Concatenate and minify JS and CSS for Jinja2 + Jingo + Django.
* `hera <https://github.com/clouserw/hera>`_:
  Client for Zeus Traffic Manager SOAP API.

Testing
-------

* `django-fixture-magic <https://github.com/davedash/django-fixture-magic>`_:
  Utilities to extract and manipulate Django fixtures.
* `django-nose <https://github.com/jbalogh/django-nose>`_\*:
  Django test runner using *nose*.
* `nose <http://somethingaboutorange.com/mrl/projects/nose/>`_\*:
  *nose* extends unittest to make testing easier.
* `test-utils <https://github.com/jbalogh/test-utils>`_\*:
  A grab-bag of testing utilities that are pretty specific to our Django,
  Jinja2, and nose setup.

Various
-------

* `nuggets <https://github.com/mozilla/nuggets/>`_:
  Little utilities that don't deserve a package.


JavaScript
==========

* `jQuery <http://jquery.com/>`_\*:
  The jQuery JavaScript library.

