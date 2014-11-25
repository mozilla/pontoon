==================================
Making a Translate Toolkit Release
==================================

Summary
=======
#. Git clone git@github.com:translate/translate.git translate-release
#. Create release notes
#. Up version number
#. make build
#. Test install and other tests
#. Tag the release
#. Publish on PyPI
#. Upload to Github
#. Upload to Sourceforge
#. Release documentation
#. Update translate website
#. Unstage sourceforge
#. Announce to the world
#. Cleanup
#. Other possible steps


Detailed instructions
=====================

Get a clean checkout
--------------------
We work from a clean checkout to ensure that everything you are adding to the
build is what is in VC and doesn't contain any of your uncommitted changes.  It
also ensure that someone else could replicate your process.

.. code-block:: bash

  $ git clone git@github.com:translate/translate.git translate-release
  $ cd translate-release
  $ git submodule update --init


Create release notes
--------------------
The release notes will be used in these places:

- Toolkit website - `download page
  <http://toolkit.translatehouse.org/download.html>`_ (used in gh-pages)
- Sourceforge download - README.rst (used to give user info)
- Email announcements - text version

We create our release notes in reStructured Text, since we use that elsewhere
and since it can be rendered well in some of our key sites.

First we need to create a log of changes in the Translate Toolkit, which is
done generically like this:

.. code-block:: bash

  $ git log $previous_version..HEAD > docs/release/$version.rst


Or a more specific example:

.. code-block:: bash

  $ git log 1.10.0..HEAD > docs/releases/1.11.0-rc1.rst


Edit this file.  You can use the commits as a guide to build up the release
notes.  You should remove all log messages before the release.

.. note:: Since the release notes will be used in places that allow linking we
   use links within the notes.  These should link back to products websites
   (`Virtaal <http://virtaal.org>`_, `Pootle
   <http://pootle.translatehouse.org>`_, etc), references to `Translate
   <http://translatehouse.org>`_ and possibly bug numbers, etc.

Read for grammar and spelling errors.

.. note:: When writing the notes please remember:

   #. The voice is active. 'Translate has released a new version of the
      toolkit', not 'A new version of the toolkit was release by Translate'.
   #. The connection to the users is human not distant.
   #. We speak in familiar terms e.g. "I know you've been waiting for this
      release" instead of formal.

We create a list of contributors using this command:

.. code-block:: bash

  $ git log 1.10.0..HEAD --format='%aN, ' | awk '{arr[$0]++} END{for (i in arr){print arr[i], i;}}' | sort -rn | cut -d\  -f2-


Add release notes for dev
-------------------------

After updating the release notes for the about to be released version, it is
necessary to add new release notes for the next release, tagged as ``dev``.


Up version numbers
------------------
Update the version number in:

- ``translate/__version__.py``
- ``docs/conf.py``

In ``__version__.py``, bump the build number if anybody used the toolkit with
the previous number, and there have been any changes to code touching stats or
quality checks.  An increased build number will force a toolkit user, like
Pootle, to regenerate the stats and checks.

For ``conf.py`` change ``version`` and ``release``

.. todo:: FIXME - We might want to consolidate the version and release info so
   that we can update it in one place.

The version string should follow the pattern::

    $MAJOR-$MINOR-$MICRO[-$EXTRA]

E.g. ::

    1.10.0
    0.9.1-rc1 

``$EXTRA`` is optional but all the three others are required.  The first
release of a ``$MINOR`` version will always have a ``$MICRO`` of ``.0``. So
``1.10.0`` and never just ``1.10``.


Build the package
-----------------
Building is the first step to testing that things work.  From your clean
checkout run:

.. code-block:: bash

  $ mkvirtualenv build-ttk-release
  (build-ttk-release)$ pip install -r requirements/dev.txt
  (build-ttk-release)$ make build
  (build-ttk-release)$ deactivate
  $ rmvirtualenv build-ttk-release


This will create a tarball in ``dist/`` which you can use for further testing.

.. note:: We use a clean checkout just to make sure that no inadvertant changes
   make it into the release.


Test install and other tests
----------------------------
The easiest way to test is in a virtualenv. You can test the installation of
the new toolkit using:

.. code-block:: bash

  $ mkvirtualenv test-ttk-release
  (releasing)$ pip install path/to/dist/translate-toolkit-$version.tar.bz2


You can then proceed with other tests such as checking:

#. Documentation is available in the package
#. Converters and scripts are installed and run correctly:

   .. code-block:: bash

     (test-ttk-release)$ moz2po --help
     (test-ttk-release)$ php2po --version
     (test-ttk-release)$ deactivate
     $ rmvirtualenv test-ttk-release

#. Meta information about the package is correct. This is stored in
   :file:`setup.py`, to see some options to display meta-data use:

   .. code-block:: bash

     $ ./setup.py --help

   Now you can try some options like:

   .. code-block:: bash

     $ ./setup.py --name
     $ ./setup.py --version
     $ ./setup.py --author
     $ ./setup.py --author-email
     $ ./setup.py --url
     $ ./setup.py --license
     $ ./setup.py --description
     $ ./setup.py --long-description
     $ ./setup.py --classifiers

   The actual descriptions are taken from :file:`translate/__init__.py`.


Tag and branch the release
--------------------------
You should only tag once you are happy with your release as there are some
things that we can't undo. You can safely branch for a ``stable/`` branch
before you tag.

.. code-block:: bash

  $ git checkout -b stable/1.10.0
  $ git push origin stable/1.10.0
  $ git tag -a 1.10.0 -m "Tag version 1.10.0"
  $ git push --tags


Publish on PyPI
---------------

.. - `Submitting Packages to the Package Index
  <http://wiki.python.org/moin/CheeseShopTutorial#Submitting_Packages_to_the_Package_Index>`_


.. note:: You need a username and password on `Python Package Index (PyPI)
   <https://pypi.python.org>`_ and have rights to the project before you can
   proceed with this step.

   These can be stored in :file:`$HOME/.pypirc` and will contain your username
   and password. A first run of:

   .. code-block:: bash

     $ ./setup.py register

   will create such file. It will also actually publish the meta-data so only
   do it when you are actually ready.

To test before publishing run:

.. code-block:: bash

  $ make test-publish-pypi


Then to actually publish:

.. code-block:: bash

  $ make publish-pypi


Create a release on Github
--------------------------

- https://github.com/translate/translate/releases/new

You will need:

- Tarball of the release
- Release notes in Markdown

#. Draft a new release with the corresponding tag version
#. Convert the release notes to Markdown with `Pandoc
   <http://johnmacfarlane.net/pandoc/>`_ and add those to the release
#. Attach the tarball to the release
#. Mark it as pre-release if it's a release candidate.


Copy files to sourceforge
-------------------------

.. note:: You need to have release permissions on sourceforge to perform this
   step.

- http://sourceforge.net/projects/translate/files/Translate%20Toolkit/

You will need:

- Tarball of the release
- Release notes in reStructured Text


These are the steps to perform:

#. Create a new folder in the `Translate Toolkit
   <https://sourceforge.net/projects/translate/files/Translate%20Toolkit/>`_
   release folder using the 'Add Folder' button.  The folder must have the same
   name as the release version e.g.  ``1.10.0-rc1``.  Mark this as being for
   staging for the moment.
#. ``make publish-sourceforge`` will give you the command to upload your
   tarball and ``README.rst``.

   #. Upload tarball for release.
   #. Upload release notes as ``README.rst``.
   #. Click on the info icon for ``README.rst`` and tick "Exclude Stats" to
      exclude the README from stats counting.

#. Check that the README.rst for the parent ``Translate Toolkit`` folder is
   still appropriate, this is the text from ``translate/__info__.py``.
#. Check all links for ``README.rst`` files, new release and parent.


Release documentation
---------------------
We need a tagged release before we can do this.  The docs are published on Read
The Docs.

- https://readthedocs.org/dashboard/translate-toolkit/versions/

Use the admin pages to flag a version that should be published

.. todo:: FIXME we might need to do this before publishing so that we can
   update doc references to point to the tagged version as apposed to the
   latest version.


Update translate website
------------------------
We use github pages for the website. First we need to checkout the pages:

.. code-block:: bash

  $ git checkout gh-pages


#. In ``_posts/`` add a new release posting.  This is in Markdown format (for
   now), so we need to change the release notes .rst to .md, which mostly means
   changing URL links from ```xxx <link>`_`` to ``[xxx](link)``.
#. Change $version as needed. See ``download.html``, ``_config.yml`` and
   ``egrep -r $old_release *``
#. :command:`git commit` and :command:`git push` -- changes are quite quick, so
   easy to review.


Unstage on sourceforge
----------------------
If you have created a staged release folder, then unstage it now.


Announce to the world
---------------------
Let people know that there is a new version:

#. Announce on mailing lists:
   Send the announcement to the translate-announce mailing lists on
   translate-announce@lists.sourceforge.net
#. Adjust the #pootle channel notice. Use ``/topic`` to change the topic.
#. Email important users
#. Tweet about it
#. Update `Toolkit's Wikipedia page
   <http://en.wikipedia.org/wiki/Translate_Toolkit>`_


Cleanup
=======
These are tasks not directly related to the releasing, but that are
nevertheless completely necessary.

Bump version to N+1-alpha1
--------------------------

Now that we've release lets make sure that master reflect the current state
which would be ``{N+1}-alpha1``. This prevents anyone using master being
confused with a stable release and we can easily check if they are using master
or stable.


Other possible steps
====================
Some possible cleanup tasks:

- Remove any RC builds from the sourceforge download pages (maybe?).
- Commit any release notes and such (or maybe do that before tagging).
- Remove your translate-release checkout.
- Update and fix these release notes.


We also need to check and document these if needed:

- Change URLs to point to the correct docs: do we want to change URLs to point
  to the $version docs rather then 'latest'
- Building on Windows, building for other Linux distros. We have produced
  Windows builds in the past.
- Communicating to upstream packagers
