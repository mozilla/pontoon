
.. _odf:
.. _opendocument_format:

OpenDocument Format
*******************
This page summarises the support for the :wp:`OpenDocument` format (ODF) in the
Translate Toolkit.  This currently involves only the :doc:`odf2xliff
</commands/odf2xliff>` and xliff2odf converters.

The Translate Toolkit aims to support version 1.1 of the ODF standard, although
it should work reasonably well with older or newer files to the extent that
they are similar.

Our support is implemented to classify tags as not containing translatable
text, or as being inline tags inside translatable tags. This approach means
that new fields added in future versions will automatically be seen as
translatable and should still be extracted successfully, even if the currently
released versions of the Translate Toolkit are not aware of their existence.

* `Currently used and classified tags
  <https://github.com/translate/translate/blob/master/translate/storage/odf_shared.py#L23>`_

More complex tag uses are still needed to extract 100% correctly in some
complex cases. For more information, see the list of :wiki:`issues from testing
<odf/testing>`.
