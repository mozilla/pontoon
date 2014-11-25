
.. _installation:

Installation
************

This is a guide to installing the Translate Toolkit on your system.  If the
Translate Toolkit is already packaged for your system, this is probably the
easiest way to install it. For Windows users, we provide installers. For
several Linux distributions, the package might be available through your
package manager.

These packages might not be the absolute newest, or you might want to install
from our packaged releases for some other reason.

If your system already has the toolkit prepackaged, then please let us know
what steps are required to install it.

.. _installation#prerequisites:

Prerequisites
=============

* Remove old versions of toolkit on Debian

The dollowing advice only applies to manual installation from tar ball.

#. Find location of your python packages::

     python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"

#. Delete toolkit package from your Python site-packages directory e.g.::

     rm /usr/local/lib/python2.5/dist-packages/translate -R

.. _installation#building:

Building
========

For build instructions, see the :doc:`developers/building` page.

.. _installation#download:

Download
========

Download a stable `released version
<http://sourceforge.net/projects/translate/files/Translate%20Toolkit/>`_.  Or
if you have a python environment, run `easy_install translate-toolkit`.  For
those who need problems fixed, or who want to work on the bleeding edge, get
the latest source from :ref:`Git <installation#installing_from_git>`.

For most Windows users, the file named "translate-toolkit-...-setup.exe" is the
best choice and contains everything you need if you just want to run Toolkit
commands.  If you want to use it for development, you will need to install it
with easy_install or from the source package.

If you install the complete "setup" version in Windows, or if you install
through your distribution's package manager, you should automatically have all
the dependencies you need. If you are installing from the Version Control
System, or from a source release, you should check the README file for
information on the dependencies that are needed. Some of the dependencies are
optional. The README file documents this.

.. _installation#installing_packaged_versions:

Installing packaged versions
============================

Get the package for your system:

+------------+------------------------------------------------------------+
| -setup.exe | A complete Windows installer containing all dependencies,  |
|            | including Python                                           |
+------------+------------------------------------------------------------+
| .exe       | An installer for a Windows with Python and other           |
|            | dependencies already installed                             |
+------------+------------------------------------------------------------+
| RPM        | If you want to install easily on an RPM based system       |
+------------+------------------------------------------------------------+
| .tar.gz    | for source based installing on Linux                       |
+------------+------------------------------------------------------------+
| .deb       | for Debian GNU/Linux (etch version)                        |
+------------+------------------------------------------------------------+

The RPM package can be installed by using the following command::

  rpm -Uvh translate-toolkit-1.0.1.rpm

To install a tar.bz2::

  tar xvjf translate-toolkit-1.1.0.tar.bz2
  cd translate-toolkit-1.1.0
  su
  ./setup.py install

On Windows simply click on the .exe file and follow the instructions.

On Debian (if you are on etch), just type the following command::

  aptitude install translate-toolkit

If you are using an old Debian stable system, you might want to install the
.tar.bz2 version. Be sure to install python and python development first with::

  apt-get install python python-dev

Alternatively newer packages might be in testing.

.. _installation#installing_from_git:

Installing from Git
===================

If you want to try the bleeding edge, or just want to have the latest fixes
from a stabilising branch then you need to use Git to get your sources.::

  git clone https://github.com/translate/translate.git

This will retrieve the ``master`` branch of the Toolkit.  Further Git
`instructions <http://git.or.cz/course/svn.html>`_ are also available.

Once you have the sources you have two options, a full install::

  su
  ./setup.py install

or, running the tools from the source directory

::

    ./setuppath # Only needed the first time
    . setpath  # Do this once for a session

.. _installation#verify_installed_version:

Verify installed version
========================

To verify which version of the toolkit you have installed run::

  [l10n@server]# moz2po --version
  moz2po 1.1.0
