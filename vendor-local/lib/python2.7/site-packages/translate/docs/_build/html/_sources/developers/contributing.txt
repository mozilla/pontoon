
.. _contributing:

Contributing
************

We could use your help.  If you are interesting in contributing then please
join us on IRC on `#pootle-dev <irc://irc.freenode.net/#pootle-dev>`_ and on
the `translate-devel <mailto:translate-devel@lists.sourceforge.net>`_ mailing
list.

Here are some idea of how you can contribute

- :ref:`Test <contributing#testing>` -- help us test new candidate releases
  before they are released
- :ref:`Debug <contributing#debugging>` -- check bug reports, create tests to
  highlight problems
- :ref:`Develop <contributing#developing>` -- add your Python developer skills
  to the mix
- :ref:`Document <contributing#documenting>` -- help make our docs readable,
  useful and complete

Below we give you more detail on these:

.. _contributing#testing:

Testing
=======

Before we release new versions of the Toolkit we need people to check that they
still work correctly.  If you are a frequent user you might want to start using
the release candidate on your current work and report any errors before we
release them.

Compile and install the software to see if we have any platform issues::

  ./setup.py install

Check for any files that are missing, tools that were not installed, etc.

:wiki:`Run unit tests <developers/testing_guidelines#running_tests>` to see if
there are any issues.  Please report any failures.

Finally, simply work with the software.  Checking all your current usage
patterns and report problems.

.. _contributing#debugging:

Debugging
=========

- Make sure your familiar with the :wiki:`bug reporting guidelines
  <developers/reporting_bugs>`.
- Create a login for yourself at https://github.com
- Then choose an `issue <https://github.com/translate/translate/issues>`_

Now you need to try and validate the bug.  Your aim is to confirm that the bug
is either fixed, is invalid or still exists.

If its fixed please close the bug and give details of how when it was fixed or
what version you used to validate it as corrected.

If you find that the bug reporter has made the incorrect assumptions or their
suggestion cannot work.  Then mark the bug as invalid and give reasons why.

The last case, an existing bug is the most interesting.  Check through the bug
and do the following:

- Fix up the summary to make it clear what the bug is
- Create new bugs for separate issues
- Set severity level and classifications correctly
- Add examples to reproduce the bug, or make the supplied files simpler
- If you can identify the bug but not fix it then explain what needs fixing
- Move on to the next bug

.. _contributing#developing:

Developing
==========

Don't ignore this area if you feel like you are not a hotshot coder!

You will need some Python skills, this is a great way to learn.

Here are some ideas to get you going:

* Write a test to expose some bug
* Try to fix the actual code to fix your bug
* Add a small piece of functionality that helps you
* Document the methods in especially the base class and derived classes
* Add a :doc:`format </formats/index>` type and converters
* Add more features to help our formats :doc:`conform to the standards
  </formats/conformance>`

You will definitely need to be on the `Development
<https://lists.sourceforge.net/lists/listinfo/translate-devel>`_ and probably
on the `Subversion checkin
<https://lists.sourceforge.net/lists/listinfo/translate-cvs>`_ lists.

Now is the time to familiarise yourself with the :doc:`developers guide
<developers>`.

.. _contributing#documenting:

Documenting
===========

This is the easy one.  Login to the wiki and start!

The key areas that need to be looked at are:

- Do the guides to each tool cover all command line options
- Are the examples clear for the general cases
- Is the tools use clear
- In the Use cases, can we add more, do they need updating. Has upstream
  changed its approach

After that and always:

* Grammar
* Spelling
* Layout
