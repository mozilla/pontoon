
.. _qm:

Qt .qm
******

A .qm file is a compiled :doc:`Qt linguist <ts>` file.  In many ways it is
similar to Gettext, in that it uses a hashing table to lookup the translated
text.  In older version they store only the hash and the translation which
doesn't make the format useful for recovering translated text.

.. _qm#conformance:

Conformance
===========

The toolkit can read .qm files correctly.  There are some unimplemented aspects
of the message block, but these seem to be legacy features and require examples
to be able to implement the feature.

The .qm implementation cannot write a .qm file, thus you are only able to use
this format in a read-only context: counting messages
(:doc:`/commands/pocount`), reading in messages for a TM or using it as a
source format for a converter e.g. a possible qm2xliff converter.

.. _qm#todo:

TODO
====

* Writing

  * Hash algorithm
