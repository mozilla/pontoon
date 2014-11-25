
.. _running_the_tools_on_microsoft_windows:

Running the tools on Microsoft Windows
**************************************

Since the toolkit is written in Python, it should work perfectly on Windows.

.. _running_the_tools_on_microsoft_windows#add_the_toolkit_to_your_path:

Add the toolkit to your path
=============================

.. _running_the_tools_on_microsoft_windows#windows_95/98:

Windows 95/98
-------------

You might need to add the installation directory of the translate toolkit to
your path ::

  path "C:\Program Files\translate-toolkit\"

This will work for one session, but will be lost when you reboot again.
Therefore you might want to add it to the autoexec.bat file.

.. _running_the_tools_on_microsoft_windows#windows_2000/xp:

Windows 2000/XP
---------------

You can add to the path permanently.  Check `this
<http://www.computerhope.com/issues/ch000549.htm>`_ useful guide.  You should
add the following to your path::

  C:\Programs Files\translate-toolkit\

If you have the `Gettext tools
<http://gnuwin32.sourceforge.net/packages/gettext.htm>`_ installed, add it to
your path as well::

  C:\Program Files\GnuWin32\bin\

.. _running_the_tools_on_microsoft_windows#change_windows_file_to_unix_file:

Change Windows file to Unix file
=================================

Some programs in Windows will add CRLFs to the file which is considered rather
poor practice for l10ns that require Unix files.  To fix a text file, drag and
drop it to the dos2unix.exe utility from http://www.bastet.com/
