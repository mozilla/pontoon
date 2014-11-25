
.. _building:

Building
********

.. _building#unix:

UNIX
====

.. _building#windows:

Windows
=======

.. _building#requirements:

Requirements
------------

* `Innosetup <http://www.jrsoftware.org/isinfo.php>`_
* `py2exe <http://www.py2exe.org/>`_

Consult the README in the source distribution for the build dependencies. 

.. _building#building_python_packages_with_c_extensions_under_windows:

Building Python packages with C extensions under Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to build modules which have C extensions, you will need either the
Visual Studio C++ compiler or `MinGW
<http://sourceforge.net/projects/mingw/files/MSYS/Extension/>`_.

Make sure that your Visual Studio C++ or MinGW program path is part of your
system's program path, since the Python build system requires this.

To build and install a package with MinGW, you need to execute::

  python setup.py build -c mingw32 install

from the command line.

To build a Windows installer when using MinGW, execute::
  
  python setup.py build -c mingw32 bdist_wininst

.. _building#building:

Building
--------

Simply execute::

  python setup.py innosetup

The generated file can be found under ``translate-toolkit-<version>\Output``
(where ``<version>`` is the software version).

