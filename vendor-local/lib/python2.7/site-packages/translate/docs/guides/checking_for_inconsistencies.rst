
.. _checking_for_inconsistencies:
.. _checking_for_inconsistencies_in_your_translations:

Checking for inconsistencies in your translations
*************************************************

Over time language changes, hopefully not very quickly.  However, if your
language is new to computers the change might be rapid.  So now your older
translations have different text to your new translations.  In this use case we
look at how you can bring alignment back to your translations.

Other cases in which you can expect inconsistencies:

* Multiple translators are involved
* Translations are very old
* You prepared this set of translations with translations from multiple sources
* You changed terminology at some stage in the translation
* You did not do a formal glossary development stage

.. _checking_for_inconsistencies#what_we_wont_be_able_to_achieve:

What we won't be able to achieve
================================

We cannot find grammatical errors and we won't be able to find all cases of
words, etc

.. _checking_for_inconsistencies#scenario:

Scenario
========

You are translating Mozilla Firefox into Afrikaans.  The files are stored in
*af*.  You have the following issues:

- Your current translator is good but took over from a team of three
- Terminology is well defined but not well used by the old translators

We'll look at the translations first from the English, or source text, point of
view.  Then we will look at it from the Afrikaans point of view.  The first
will pick up where we have translated the same English word differently in
Afrikaans i.e. an inconsistency.  While the second will determine if we use the
same English word for different English words, possibly this will confuse a
user.

.. _checking_for_inconsistencies#step_1:_extracting_conflicting_target_text_translations:

Step 1: Extracting conflicting target text translations
-------------------------------------------------------

::

  poconflicts -I --accelerator="&" af af-conflicts

From our existing translation in *af* we extract conflicts and place them in
*af-conflicts*.  We are ignoring case with :opt:`-I` so that ``Save as`` is
considered the same as ``Save As``.  The :opt:`--accelerator` options allows us
to ignore accelerators so that ``File`` is the sane as ``&File`` which is also
the same as ``Fi&le``

If we browse into *af-conflicts* we will see a flat structure of words with
conflicts. ::

  $ cd af-conflicts
  $ ls
  change.po         disc.po         functionality.po  letter.po          overwrite.po       restored.po
  changes.po        document.po     gb.po             library.po         page.po            restore.po
  character.po      dots.po         graphic.po        light.po           pager.po           retry.po 
  chart.po          double.po       grayscale.po      limit.po           percent.po         return.po
  check.po          down.po         grid.po           line.po            pies.po            right.po
  circle.po         drawing.po      group.po
  etc...

These are normal PO files which you can edit in any PO editor or text editor.
If we look at the first file ``change.po`` we can see that the source text
*Change* was translated as *Verander* and *Wysig*.  The translators job is noe
to correct these PO files, ignoring instances where the difference is in fact
correct.

Once all fixes have been made we can merge our changes back into the original
files.

.. _checking_for_inconsistencies#step_2:_merging_our_corrections_back_into_the_original_files:

Step 2: Merging our corrections back into the original files
------------------------------------------------------------

Our files in *af-conflicts* are in a flat structure.  We need to structure them
into the hierarchy of the existing PO files. ::

  porestructure af-conflicts af-restructured

The entries that where in the files in *af-conflicts* have been placed in
*af-restrucured*, they now appear in the correct place in the directory
structure and also appear in the correct file.  We are now ready to merge. ::

  pomerge -t af -i af-restructure -o af

Using the existing files in *af* we merge the corrected and restructured file
from *af-restructure* and place them back into *af*.  Note: use a different
output directory if you do not want to overwrite your existing files. All your
conflict corrections are now in the correct PO file in *af*.

You might want to run **Step 1** again to make sure you didn't miss anything or
introduce yet another problem.

Next we look at the inverted conflict problem.

.. _checking_for_inconsistencies#step_3:_extracting_conflicts_of_meaning:

Step 3: Extracting conflicts of meaning
---------------------------------------

If you have used the same Afrikaans word for two different English words then
you could have created a conflict of meaning.  For instance in our Xhosa
translations the word ``Cima`` was used for both ``Delete`` and ``Cancel``.
Clearly this is a serious issue.  This step will allow us to find those errors
and take action. ::

  poconflicts -v -I --accelerator="&" af af-conflicts-invert

We use the same command line as in **Step 1** but add :opt:`-v` to allow us to
invert the match.  We are also now outputting to *af-conflicts-invert* to make
things clear.

This time the PO files that are created have Afrikaans names ::

  $ cd af-conflicts-invert
  $ ls
  dataveld.po              grys.po             lisensieooreenkoms.po  paragraaf.po        sny.po
  datumgekoop.po           hallo.po            lysinhoud.po           pasmaak.po          soek.po
  datum.po                 hiperboliese.po     maateenheid.po         persentasie.po      sorteer.po
  deaktiveer.po            hoekbeheer.po       maatskappynaam.po      posadres.po         sorteervolgorde.po
  etc...

We edit these as usual.  You need to remember that you will see a normal PO
file but that you are looking at how the translation might be confusing to a
user.  If you see the same Afrikaans translation for two different English
terms but there is no conflict of meaning or no alternative then leave it as
is.  You will find a lot of these instances so the results are less dramatic
then the results from a normal conflict analysis.

Lastly follow **Step 2** to restructure and merge these conflicts back into
your translations

.. _checking_for_inconsistencies#conclusion:

Conclusion
==========

You've now gone a long way to improving the quality of your translations.
Congratulations!  You might want to take some of what you've learnt here to
start building a terminology list that can help prevent some of the issues you
have seen.
