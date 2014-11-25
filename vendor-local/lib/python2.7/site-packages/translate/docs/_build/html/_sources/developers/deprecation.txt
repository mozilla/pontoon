Deprecation of Features
=======================

From time to time we need to deprecate functionality, this is a guide as to how
we implement deprecation.


Types of deprecation
--------------------

1. Misspelled function
2. Renamed function
3. Deprecated feature


Period of maintenance
---------------------
Toolkit retains deprecated features for a period of two releases.  Thus
features deprecated in 1.7.0 are removed in 1.9.0.


Documentation
-------------
Use the ``@deprecated`` decorator with a comment and change the docstring to
use the Sphinx `deprecation syntax
<http://sphinx-doc.org/markup/para.html#directive-deprecated>`_.

.. code-block:: python

   @deprecated("Use util.run_fast() instead.")
   def run_slow():
       """Run slowly

       .. deprecated:: 1.9.0
          Use :func:`run_fast` instead.
       """
       run_fast()  # Call new function if possible


Implementation
--------------
Deprecated features should call the new functionality if possible.  This may
not always be possible, such as the cases of drastic changes.  But it is the
preferred approach to reduce maintenance of the old code.


Announcements
-------------
.. note:: This applies only to feature deprecation and renamed functions.
   Announcements for corrections are at the coders discretion.

1. On **first release with deprecation** highlight that the feature is
   deprecated in this release and explain reasons and alternate approaches.
2. On **second relase** warn that the feature will be removed in the next
   release.
3. On **third release** remove the feature and announce removal in the release
   announcements.

Thus by examples:

Translate Toolkit 1.9.0:
  The ``run_slow`` function has been deprecated and replaced by the faster and
  more correct ``run_fast``.  Users of ``run_slow`` are advised to migrate
  their code.

Translate Toolkit 1.10.0:
  The ``run_slow`` function has been deprecated and replaced by ``run_fast``
  and will be removed in the next version.  Users of ``run_slow`` are advised
  to migrate their code.

Translate Toolkit 1.11.0:
  The ``run_slow`` function has been removed, use ``run_fast`` instead.
