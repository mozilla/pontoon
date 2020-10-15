The Guide to your First Contribution to Pontoon
===============================================

Welcome to Pontoon!

This document is going to guide you as you discover Pontoon and make
valuable contributions. It will walk you step by step until you are in a
position to write code that you can reliably run, test, and send for
review.

1. Make sure it's a good match
------------------------------

*Before contributing to an open source project, it is important to make
sure that the project uses technologies that you know and want to learn more about.*

Pontoon is a web application, with both back-end and front-end code. The
two languages we use are **Python** (back-end) and **JavaScript**
(front-end). On the back-end, we use the **Django** framework. On the
front-end, we use the **React** framework. To be able to contribute, you
will want to have knowledge of either Python and Django or JavaScript
and React. Having experience with both pairs is of course even better!

We use **git** to version our code, and we use **GitHub** to handle pull
requests and code reviews. Basic knowledge of git is required to be able
to send your contributions our way.

+--------------+-------------------+-------------------+
| Skill        | Expected Level    | Notes             |
+==============+===================+===================+
| git          | Basic knowledge   |                   |
+--------------+-------------------+-------------------+
| Python       | Some experience   | Python 3          |
+--------------+-------------------+-------------------+
| Django       | Basic knowledge   |                   |
+--------------+-------------------+-------------------+
| JavaScript   | Some experience   | ECMAScript 2018   |
+--------------+-------------------+-------------------+
| React        | Basic knowledge   |                   |
+--------------+-------------------+-------------------+

2. Install Pontoon
------------------

*In order to be able to contribute code to an open source project, you
first need to be able to run that project on your computer.*

The recommended method of installing Pontoon is using ``docker`` and our
scripts. It is straightforward if your computer is running with Linux or
macOS, and a tad more difficult for Windows. In all cases, follow the
instructions in our :doc:`setup` page.


3. Populate your database
-------------------------

*After installing a tool, it is likely that its database is empty. You
will need to create some data in order to have things show up in the
interface.*

Once Pontoon is installed and you have it running, you will want to
create some data so that you can play with it, and test it in action.
You can create any kind of data you want, of course, but to make it
easier we have a special git repository that we made for testing
Pontoon. Here are the steps to add that project to your Pontoon
instance:

1.  Log in to your local instance with the superuser account you created during the previous step.
2.  Click the avatar in the top-right corner, and in the menu click "Admin".
3.  You will see the Admin panel, with a table of projects that will likely be empty. Click the "Add New Project" button.
4.  Fill the project creation form as follows:

    1.  Name: Pontoon Test
    2.  Slug (auto-filled): pontoon-test
    3.  Locales: select Slovenian (sl), then add any locales you want
    4.  Repositories

        1. URL: https://github.com/mathjazz/pontoon-test
        2. Download prefix: https://raw.githubusercontent.com/mathjazz/pontoon-test/master/{locale\_code}
        3. Public Repository Website: https://github.com/mathjazz/pontoon-test

5.  Leave the rest as it is, then scroll to the bottom of the page, and click the "Save Project" button.
6. Once the project is saved, scroll to the bottom of the page again, and click the "Sync" button. This will pull the data from the repository, and create entries for each of the locales you have enabled.
7. And that's it! You should now have a project enabled for some locale.

4. Verify your setup
--------------------

*Setting up a project means more than installing it: it also means
making sure that the tool runs and that tests pass.*

Once you have successfully installed and populated Pontoon on your
computer, you will need to make a few verifications. First and foremost,
make sure the site works correctly, and the data you created previously
shows up. Make sure you can log in, that you can send some translations,
that projects appear on the dashboards, etc.

Second, you will want to run the tests and make sure they pass. We have
a few test suites for Pontoon, some for the front-end, others for the
back-end, as well as a few code-quality tests. To run all of the tests
(same as what will happen when you open a pull request in GitHub), use
the command ``make test``.

When you have successfully verified that your setup works correctly, you
can safely move to the next part.

5. Choose a bug to work on
--------------------------

*You are now ready to make a contribution! Open source projects usually
have a list of mentored bugs that are appropriate to work on first, and
on which mentors will be available to help you.*

Work that needs to be done on Pontoon is tracked in
`bugzilla <https://bugzilla.mozilla.org/>`_, Mozilla's bug tracking
software. You will need to create an account there in order to be
assigned to a bug.

We maintain a list of what we deem "good first bugs". They are marked as
mentored on bugzilla, and can be found quickly on our `Pontoon wiki
page <https://wiki.mozilla.org/L10n:Pontoon#Get_involved>`_ or through
`this bugzilla
search <https://bugzilla.mozilla.org/buglist.cgi?f1=bug_mentor&list_id=15050149&o1=isnotempty&resolution=---&classification=Server%20Software&query_format=advanced&emailbug_mentor1=1&component=Pontoon&product=Webtools>`_.
Look through that list for unassigned bugs (marked as ``NEW``), choose
one that is appealing to you and seems adapted to your skill set, then
comment on that bug asking to be assigned to it. Feel free to start
working on it right away — even if you end up not being assigned for
some reason, it will still be good experience for you.

6. Read the contributing rules
------------------------------

*Most projects have strict contributing rules, and your contributions
risk not being accepted if you don't respect them.*

To make developer's lives easier, we enforce a few contribution rules
around Pontoon. They range from how to style your code to how to write
commit messages. All these rules are written in our :doc:`contributing`
page. Please read it before opening a pull request!

There is more documentation around Pontoon, and it is often worth
reading it, if only to understand better how the tool works and how and
where to make your contributions. Here are a few links to important
documentation resources:

-  If you want to work on the front-end, it is important that you read
   the `Front-End
   Documentation <https://github.com/mozilla/pontoon/tree/master/frontend>`_.
-  Most of the documentation around installing and developing can be
   found in `Pontoon's
   Documentation <https://mozilla-pontoon.readthedocs.io/en/latest/>`_.
-  For documentation about using Pontoon to localize, see `How to use
   Pontoon <https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/>`_.
-  For documentation about exposing a project on Pontoon, see `How to
   localize your
   projects <https://mozilla-pontoon.readthedocs.io/en/latest/user/localizing-your-projects.html>`_.
-  For documentation about managing communities in Pontoon, see `Working
   with
   Pontoon <https://mozilla-l10n.github.io/documentation/tools/pontoon/>`_.

7. Communicate with us
----------------------

*Open source projects are usually built around a community of people.
Communicating with that community is an important part of contributing
to such projects.*

There are two main places where we communicate about Pontoon's
development. The first one is `chat.mozilla.org <https://chat.mozilla.org/>`_,
used for real-time chat, quick questions, side-track conversations, etc.
Find us in the `#pontoon channel <https://chat.mozilla.org/#/room/#pontoon:mozilla.org>`_.

The second is discourse, a forum platform that we use for more long-term
conversations. We use `Mozilla's community
discourse <https://discourse.mozilla.org/>`_ instance, posting in the
`pontoon category <https://discourse.mozilla.org/c/pontoon>`_.

These are both places that we strongly encourage you to join, and they
are where you should introduce yourself, ask questions, show your work,
etc.

Pontoon's core developer team is currently composed of Matjaž and
Adrian, with occasional help from other members of Mozilla's L10n team,
Axel and Staś. We also receive invaluable help from community members.

+------------+----------+--------------------------+------------------+-----------------------------------------------+
|            | Name     | ROLE                     | chat.mozilla.org | github                                        |
+============+==========+==========================+==================+===============================================+
| |image4|   | Matjaž   | Pontoon Core Developer   | mathjazz         | `mathjazz <https://github.com/mathjazz/>`_    |
+------------+----------+--------------------------+------------------+-----------------------------------------------+
| |image5|   | Adrian   | Pontoon Core Developer   | adrian           | `adngdb <https://github.com/adngdb/>`_        |
+------------+----------+--------------------------+------------------+-----------------------------------------------+
| |image6|   | Axel     | L10n Tech Lead           | Pike             | `Pike <https://github.com/Pike/>`_            |
+------------+----------+--------------------------+------------------+-----------------------------------------------+
| |image7|   | Staś     | Fluent Core Developer    | stas             | `stasm <https://github.com/stasm/>`_          |
+------------+----------+--------------------------+------------------+-----------------------------------------------+

.. |image0| image:: https://avatars2.githubusercontent.com/u/626716?s=32&v=4
.. |image1| image:: https://avatars1.githubusercontent.com/u/328790?s=32&v=4
.. |image2| image:: https://avatars3.githubusercontent.com/u/43494?s=32&v=4
.. |image3| image:: https://avatars2.githubusercontent.com/u/265818?s=32&v=4
.. |image4| image:: https://avatars2.githubusercontent.com/u/626716?s=32&v=4
.. |image5| image:: https://avatars1.githubusercontent.com/u/328790?s=32&v=4
.. |image6| image:: https://avatars3.githubusercontent.com/u/43494?s=32&v=4
.. |image7| image:: https://avatars2.githubusercontent.com/u/265818?s=32&v=4
