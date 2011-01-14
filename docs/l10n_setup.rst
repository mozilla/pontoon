L10n Setup
==========

So you'd like to localize your webapp. **Congratulations!**

Playdoh comes with all of the libraries and tools you need
in the dev and production requirements.

Steps
-----

The following steps will get you started:

#. Create a SVN reposity based on MDN_ locale directory.
   This will give you a README.txt, compile-mo.sh, and 
   show you the proper directory layout.
#. Compile the po files and mirror the SVN repository in a 
   git repository via a cron job that runs every 15 minutes. 
   Example: (TBD)
   /home/fwenzel/bin/autol10n/autol10n.sh
#. Add your git repo as an external to this project
   It should create a locale directory at the top level 
#. Read locale/README.txt for a better understanding of
   what Django management commands are used to extract and
   merge strings into your po files. It has instructions
   for adding more locales.

Q&A
---
Why SVN? Our localizers like to use either SVN or Verbatim.

Why a git repo to mirror an SVN repo? This allows us to have an external reference and update easily.

.. _MDN: http://svn.mozilla.org/projects/mdn/trunk/locale/
