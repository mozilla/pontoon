.. _packages:

==========================
pip and friends: Packaging
==========================

*(largely borrowed from Zamboni)*

Your app will depend on lots of tasty open source Python libararies. The list
of all your dependencies should exist in two places:
# requirements/prod.txt
# As a submodule of vendor

Ultimately your app code will run against the libraries under vendor via mod_wsgi.

Why requirements? For developement, you can use virtualenvs and pip to have a 
tidy self-contained environment. If run from the Django runserver command, you
don't even need a web server.


The vendor library
------------------

The ``/vendor`` library is supposed to contain all packages and repositories.
It enables the project to be deployed as one package onto many machines,
without relying on PyPI-based installations on each target machine.

By default, the vendor lib is checked out as a *git submodule* under
``vendor/``. If you *do* need to check it out separately, do::

    git clone --recursive git://github.com/mozilla/playdoh-lib.git ./vendor

Once the playdoh-lib repo has been downloaded to ``/vendor``, you only need to
install the **compiled** packages (as defined in ``requirements/compiled.txt``).
These can come from your system package manager or from::

    pip install -r requirements/compiled.txt


Global vs. local library
------------------------

Playdoh provides its default library in the ``vendor/`` directory. You *may*
fork and change it, but that will make it hard to pull updates from the
upstream library later.

If you want to make only a few **local additions** or override some of the
libs in ``vendor/``, make those changes to the directory ``vendor-local/``
instead, which (in ``manage.py``) is given precedence over playdoh's vendor
dir.

compiled.txt vs prod.txt
------------------------
If a Python library requires compilation, it should be recorded in compiled.txt.
These aren't as portable and cannot be shipped in the vendor library.
For local development, it's nice to pip install these into a virtualenv. A 
common practise is to use virtual env **only** for compiled libraries and
vendor for the rest of your dependencies.

Adding new packages
-------------------

If we wanted to add a new dependency called ``cheeseballs`` to playdoh, you
would add it to ``requirements/prod.txt``. If your library isn't used in 
production, then put it in ``requirements/dev.txt``. This makes it available 
to users installing into virtualenvs.

We also need to add the new package to the vendor lib, since that is what runs
in production...

First, we need to add the source. There are two ways, depending on how
this project is hosted:

Non-git based repos (hg, CVS, tarball)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For such repos or for packages coming from PyPI, do::

    pip install -I --install-option="--home=`pwd`/vendor-local" cheeseballs
    cd vendor-local
    git add lib/python/cheeseballs
    git commit

Optionally, if the package installs executables add them too. For
example::

    cd vendor-local
    git add bin/cheeseballer
    git commit

For hg repos that are not on PyPI, they can be installed with pip too
but omit the ``--home`` option and use the ``--src`` instead. For
example::

    pip install -I --src='vendor-local/src' \    
    -e hg+http://bitbucket.org/jespern/django-piston@default#egg=django-piston
    cd vendor-local
    git add src/django-piston
    git commit

Note: Installed source packages need to be appended to
``vendor-local/vendor.pth``. See note below. For example::

    echo src/django-piston >> vendor-local/vendor.pth
    
git-based repositories
~~~~~~~~~~~~~~~~~~~~~~

For a git-based package, add it as a git submodule::

    cd vendor-local
    git submodule add git://github.com/mozilla/cheeseballs.git src/cheeseballs
    git commit vendor.pth .gitmodules src/cheeseballs

Further, you then need to update ``vendor-local/vendor.pth``. Python uses
``.pth`` files to dynamically add directories to ``sys.path`` (`docs
<http://docs.python.org/library/site.html>`_).

The file format is simple. Consult ``vendor/vendor.pth`` for reference.

Some packages (like ``html5lib`` and ``selenium``) are troublesome, because
their source lives inside an extra subdirectory ``src/`` inside their checkout.
So they need to be sourced with ``src/html5lib/src``, for example. Hopefully
you won't hit any snags like that.

Done. Try ``./manage.py shell`` and then ``import cheeseballs`` to make sure
it worked.

Testing Your Vendor Change
---------------
It's critical that you test your app running under mod_wsgi. Although you
may use runserver day to day, go ahead and run some code through WSGI to 
prove vendor is setup properly. (throw an import into your view, etc)

Advanced Topics
---------------
TODO [automate these instructions](<https://github.com/mozilla/playdoh/issues/30)

Initial creation of the vendor library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The vendor repo was seeded with ::

    pip install -I --install-option="--home=`pwd`/vendor" --src='vendor/src' -r requirements/dev.txt

    # ..delete some junk from vendor/lib/python...

    # Create the .pth file so Python can find our src libs.
    find src -type d -depth 1 >> vendor.pth

    # Add all the submodules.
    for f in src/*; do
        pushd $f >/dev/null && REPO=$(git config remote.origin.url) && popd > /dev/null && git submodule add $REPO $f
    done
    git add .


Adding lots of git submodules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As noted in *Adding new packages*, git-based packages are *git submodules*
inside the vendor library. To set up the first batch of submodules, something
like the following happened::

    for f in src/*
        pushd $f && REPO=$(git config remote.origin.url) && popd && git submodule add $REPO $f


For reference: pip
~~~~~~~~~~~~~~~~~~

The classical method of installing is using pip. We have our packages
separated into three files:

:src:`requirements/compiled.txt`
    All packages that require (or go faster with) compilation.  These can't be
    distributed cross-platform, so they need to be installed through your
    system's package manager or pip.

:src:`requirements/prod.txt`
    The minimal set of packages you need to run zamboni in production.  You
    also need to get ``requirements/compiled.txt``.

:src:`requirements/dev.txt`
    All the packages needed for running tests and development servers.  This
    automatically includes ``requirements/prod.txt``.


With pip, you can get a development environment with::

    pip install -r requirements/dev.txt -r requirements/compiled.txt

