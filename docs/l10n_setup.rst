L10n Setup
==========

So you'd like to localize your webapp. **Congratulations!**

Playdoh comes with all of the libraries and tools you need in the dev and
production requirements.

Requirements
------------

The one set of low level tools not provided is gettext.

::

    aptitude install gettext
    # or
    brew install gettext

Steps
-----

To allow localizers to translate your app on localize.mozilla.org, your .po
files need to be in SVN. You want a checkout of your locale directory to live
inside the git checkout under ``locale``.

The following steps will get you started:

#.  Create an SVN repository with directories based on MDN_ locale directory.
    You need at least::

        ./en_US
        ./en_US/LC_MESSAGES
        ./templates
        ./templates/LC_MESSAGES

#.  Check out this SVN repository inside your project path::

        cd /my/playdoh/project/dir/
        svn checkout https://svn.mozilla.org/projects/something/trunk/locale locale

        ## If you don't like svn, you may use git-svn too:
        # git svn clone https://svn.mozilla.org/projects/something/trunk/locale locale

#.  Now extract strings from your project::

        ./manage.py extract
        ./manage.py verbatimize --rename
        ./manage.py merge

#.  Commit it all.

#.  Build your .mo files and commit those as well::

        ./bin/compile-mo.sh locale/
        cd locale
        git add .
        git commit -m 'Built .mo files'


Advanced Steps
--------------

#.  Some projects keep a copy of the SVN checkout in git. When doing that,
    keep in mind that ``git svn dcommit`` will change the commit message,
    thus changing the git commit ID. Therefore, always commit to SVN first,
    then push to git, never vice-versa::

        cd locale/
        # do something
        git commit -am 'did something'
        git svn dcommit && git push origin HEAD

#.  localize.mozilla.org does not automatically compile .mo files when a
    localizer commits to SVN. Neither does it automate the push over to
    git. There's a handy little script called ``autol10n`` that you can
    run as a cron job somewhere, which will:
    
    * pick up changed .po files from SVN,
    * compile the .mo files,
    * then (if necessary) push everything over to git...
    * ... and retag the git submodule to the latest revision.

    The script is available in playdoh under ``bin/autol10n.sh``.

#.  Read the next section (:ref:`l10n-update`) for a better understanding of
    what Django management commands are used to extract and merge strings into
    your po files. It has instructions for adding more locales.

.. _MDN: http://svn.mozilla.org/projects/mdn/trunk/locale/

Q&A
---

* *Why SVN?* Our localizers like to use either SVN or Verbatim.
* *Why a git repo to mirror an SVN repo?* This allows us to have an external
  reference ("git submodule") and deploy the app including its translations
  easily.
* *How do I use gettext?* In templates we use jinja_ 

.. _jinja: http://jinja.pocoo.org/docs/templates/#i18n
