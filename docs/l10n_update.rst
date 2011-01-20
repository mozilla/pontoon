.. _l10n-update:

L10n Update
===========

Follow these steps to **update** strings for L10n.

We are using English strings for gettext message ids.

Environment Setup
-----------------

Your top level directory named locale should be an SVN repository.
This is because we will generate files there and we'll
commit via SVN. Developers who never deal with L10n
do not need to worry about this kind of setup. It's often
easier to have a L10n dev setup, which a cron job updates
the sources, updates the strings, and compiles the po
files and lastly commiting to SVN.

Instructions:
-------------

::

    ./manage.py extract

    ./manage.py verbatimize --rename
    # This will copy the POT files created in step 1 to templates/LC_MESSAGES.

    ./manage.py merge


Optional:
---------

To compile all .mo files::

    ./bin/compile-mo.sh locale/


New Locales:
------------

Assuming you want to add 'fr':

#.  ``mkdir -p locale/fr/LC_MESSAGES``
#.  ``./manage.py merge``

or

#.  ``msginit --no-translator -l fr -i templates/LC_MESSAGES/messages.pot -o fr/LC_MESSAGES/messages.po``
#.  repeat for other POT files
