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
files need to be in SVN. To play nice with our git-based application code,
we need to keep this SVN repository in sync with a git repository.

The following steps will get you started:

#.  Create an SVN repository with directories based on MDN_ locale directory.
    You need at least::

        ./en_US
        ./en_US/LC_MESSAGES
        ./templates
        ./templates/LC_MESSAGES

#.  Make a new git repository (a convention is to call it ``myproject-locale``),
    and clone the SVN repo into it. ::

        cd /my/playdoh/project/dir/
        git svn clone https://svn.mozilla.org/projects/something/trunk/locale locale
        cd locale
        git add remote origin git@github.com:mozilla/myproject-locale.git
        git push origin master
        cd ..

    Now extract strings from your project::

        ./manage.py extract
        ./manage.py verbatimize --rename
        ./manage.py merge

#.  Commit it all locally
#.  Build your .mo files and commit those as well::

        ./bin/compile-mo.sh locale/
        cd locale
        git add .
        git commit -m 'Built .mo files'

#.  Finally push this to SVN followed by a push to git. ::

        git svn dcommit && git push origin HEAD

    **A note on SVN vs. git:** When you ``git svn dcommit``, git will add
    SVN metadata to your git commit message. This causes the *commit ID to
    change*. So you always want to push to SVN first, then to git, not
    vice versa, or git will be a sad panda because your local and remote
    histories diverge.

#.  Add the ``locale/`` directory as a *git submodule* to your main code
    repository, so that they can be deployed together::

        git submodule add git://github.com/mozilla/myproject-locale.git locale
        # (commit, push)
    

Advanced Steps
--------------

#.  localize.mozilla.org does not automatically compile .mo files when a
    localizer commits to SVN. Neither does it automate the push over to
    git. There's a handy little script called ``autol10n`` that you can
    run as a cron job somewhere, which will:
    
    * pick up changed .po files from SVN,
    * compile the .mo files,
    * then push everything over to git...
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
