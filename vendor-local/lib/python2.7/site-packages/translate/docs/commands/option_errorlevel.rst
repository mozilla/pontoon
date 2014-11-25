
.. _option_errorlevel:

--errorlevel=ERRORLEVEL
***********************

This is a parameter that can be passed to most of the programs in the translate
toolkit in order to choose the level of feedback that you need when errors
occur.  It is mostly useful for debugging. Please report your errors to the
developers with :opt:`--errorlevel=traceback`.

.. _option_errorlevel#none:

none
====

Display no error messages

.. _option_errorlevel#message:

message
=======

Display on the error message

::

    An error occurred processing PO file

.. _option_errorlevel#exception:

exception
=========

Give the error message and name and Python exception

::

    ValueError: An error occurred processing PO file

.. _option_errorlevel#traceback:

traceback
=========

Provide a full traceback for debugging purposes

::

    csv2po: warning: Error processing: nso/readlicense_oo/docs/readme.csv: Traceback (most recent call last):

      File "/usr/lib/python2.4/site-packages/translate/misc/optrecurse.py", line 415, in recursiveprocess
        success = self.processfile(fileprocessor, options, fullinputpath, fulloutputpath, fulltemplatepath)

      File "/usr/lib/python2.4/site-packages/translate/misc/optrecurse.py", line 468, in processfile
        if fileprocessor(inputfile, outputfile, templatefile, **passthroughoptions):

      File "/usr/lib/python2.4/site-packages/translate/convert/csv2po.py", line 183, in convertcsv
        outputpo = convertor.convertfile(inputcsv)

      File "/usr/lib/python2.4/site-packages/translate/convert/csv2po.py", line 159, in convertfile
        raise ValueError("An error occured processing PO file")

    ValueError: An error occurred processing PO file

