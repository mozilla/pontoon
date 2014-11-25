
.. _subtitles:

Subtitles
*********

.. versionadded:: 1.4

The translation of subtitles are supported in the toolkit with the commands
:doc:`sub2po </commands/sub2po>` and po2sub.

The following formats are supported for subtitles:

* MicroDVD
* MPL2
* MPsub
* :wp:`SubRip` (.srt)
* :wp:`SubViewer` 2.0 (.sub)
* TMPlayer
* Sub Station Alpha
* Advanced Sub Station Alpha

YouTube supports `a number of formats
<https://support.google.com/youtube/answer/2734698?hl=en&ref_topic=2734694>`_

.. _subtitles#implementation_details:

Implementation details
======================

Format support is provided by `Gaupol <http://home.gna.org/gaupol/>`_ a
subtitling tool.  Further enhancement of format support in Gaupol will directly
benefit our conversion ability.

.. _subtitles#usage:

Usage
=====

It must be noted that our tools provide the ability to localise the subtitles.
This in itself is useful and allows a translator to use their existing
localisation tools.  But this is pure localisation and users should be aware
that they might still need to post edit their work to account for timing,
limited text space, limits in the ability of viewers to keep up with the text.

For most cases simply localising will be good enough.  But in some cases the
translated work might need to be reviewed to fix any such issues.  You can use
Gaupol to perform those reviews.
