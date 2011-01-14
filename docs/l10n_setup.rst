L10n Setup
==========

So you'd like to localize your webapp. **Congratulations!**

Playdoh comes with all of the libraries and tools you need
in the dev and production requirements.

Requirements
------------

The one set of low level tools not provided is gettext.

::

    aptitutde install gettext

Steps
-----

The following steps will get you started:

#. Create a SVN reposity with directories based on MDN_ 
   locale directory. Playdoh comes with bin/complie-mo.sh   
#. Compile the po files and mirror the SVN repository in a 
   git repository via a cron job that runs every 15 minutes. 
   Example: (TBD)
   /home/fwenzel/bin/autol10n/autol10n.sh
#. Add your git repo as an external to this project
   It should create a locale directory at the top level 
#. Read the next section L10n udpate for a better understanding of
   what Django management commands are used to extract and
   merge strings into your po files. It has instructions
   for adding more locales.

Q&A
---
Why SVN? Our localizers like to use either SVN or Verbatim.
Why a git repo to mirror an SVN repo? This allows us to have an external reference and update easily.

.. _MDN: http://svn.mozilla.org/projects/mdn/trunk/locale/
