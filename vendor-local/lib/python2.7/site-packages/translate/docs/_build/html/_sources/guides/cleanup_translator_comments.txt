
.. _cleanup_translator_comments:

Cleanup translator comments
***************************

Translate Toolkit 1.1 saw source comments being converted to developer comments
instead of translator comments.

This use case shows you how to get rid of the old translator comments.

.. _cleanup_translator_comments#the_change:

The Change
==========

We used to put all source comments into translator comments.

::

  # Some Comment

But now place them in developer comments.

::

  #. Some Comment

This ensures that these source comments are updated to the newest versions from
the source files, which is a good thing.  Translator comments survive these
updates, just like you want, while developer comments are discarded.

If you don't clean up your PO files you will now end up with::

  # Some Comment
  #. Some Comment

Thus a duplicated comment.  Fortunately you only need to clean your PO files
once.

.. _cleanup_translator_comments#removing_old_translator_comments:

Removing old translator comments
================================

.. note:: This will remove all your translator comments.  So if you have some
   that you actually want to keep then you will need to manual editing

Removal is simple using :doc:`/commands/pocommentclean`::

  pocommentclean my-po-dir

Which will clean all your PO files in ``my-po-dir``

``pocommentclean`` is simply a nice wrapper for this sed command::

  sed -i "/^#$/d;/^#[^\:\~,\.]/d" $(find po -name "*.po")

This will delete all lines starting with # that are not used by PO for
locations (#:), automatic/developer comments (#.), state (#,) and obsolete
(#~).

You can now safely commit your changes and begin your migrations using
:doc:`/commands/pot2po` of :doc:`/commands/pomigrate2`

