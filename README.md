Pontoon
=======
Pontoon enables localizers to translate websites in-place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag. [Localizer Docs](https://developer.mozilla.org/en-US/docs/Localizing_with_Pontoon).

To enable localization of your site with Pontoon, include a script to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags. [Developer Docs](https://developer.mozilla.org/en-US/docs/Implementing_Pontoon_Mozilla).

Installation
------------
Pontoon is basedon on [Playdoh](https://github.com/mozilla/playdoh). To set it up, you can either use Playdoh's official [documentation](http://playdoh.readthedocs.org/en/latest/) or follow the steps below.

1. Clone this repository or your [fork](http://help.github.com/fork-a-repo/):
 * `git clone --recursive https://github.com/mathjazz/pontoon.git`
 * `cd pontoon`
2. Create and set up the [virtual environment](http://www.virtualenv.org/en/latest/index.html):
 * `virtualenv --no-site-packages env`
 * `source env/bin/activate`
 * [Mac users](https://bugzilla.mozilla.org/show_bug.cgi?id=1005443): `export ARCHFLAGS="-Wno-error=unused-command-line-argument-hard-error-in-future"`
 * `pip install -r requirements/compiled.txt -r requirements/prod.txt`
3. Configure the [settings](#local-settings):
 * `cp settings/local.py-dist settings/local.py`
4. Set up the database:
 * `mysql.server start`
 * `mysql -u root -e 'CREATE DATABASE pontoon CHARACTER SET utf8;'`
 * `./manage.py syncdb --noinput && ./manage.py migrate`

__Mac users__ : _In case of a_ `ValueError: expected only letters, got 'utf-8'`

_Run :_ `export LC_CTYPE=en_US` _before running_ `./manage.py syncdb --noinput && ./manage.py migrate`

 * `mysql -u root pontoon -e 'ALTER TABLE base_entity MODIFY string LONGTEXT COLLATE utf8_bin;'`
5. Run the development server:
 * `./manage.py runserver`

And that's it, just point your web browser to [http://localhost:8000](http://localhost:8000) and Pontoon's homepage should apear.

Test project
------------
It gets much more exciting if you add at least one project, so you can try how the localization with Pontoon actually works. We created a simple website in PHP that uses SVN repository for storing localization files. Here's how you set it up:

1. Move or link main Pontoon project folder (`pontoon/`) to your web server's document root, which should be capable of running PHP.
2. Install [pysvn](http://pysvn.tigris.org/project_downloads.html) to work with the SVN repository. Binaries are available for most popular platforms, but you can also install it from source:
 * Download and untar the latest [source kit](http://pysvn.tigris.org/project_downloads.html) under pysvn Extension.
 * `cd Source`
 * `python setup.py configure`
 * `make`
 * `cp -R pysvn pontoon/env/lib/python2.X/site-packages/`
3. Run project from localization files stored in SVN repository:
 * `./manage.py update_projects`

You can also add your own project at [http://localhost:8000/admin/](http://localhost:8000/admin/), but you need an admin account for that:
 * `./manage.py createsuperuser`

Local settings
--------------
 * `MICROSOFT_TRANSLATOR_API_KEY`: set to a valid [Microsoft Translator API key](http://msdn.microsoft.com/en-us/library/hh454950) to use machine translation.
 * `GOOGLE_ANALYTICS_KEY`: set to a valid [Google Analytics key](https://www.google.com/analytics/) to use Google Analytics.
 * `MOZILLIANS_API_KEY`: set to a valid [Mozillians API key](https://wiki.mozilla.org/Mozillians/API-Specification) to grant permission to Mozilla localizers.

Updates
-------
To sync your repository with upstream changes, just update the code using git:

* `git pull && git submodule sync --quiet && git submodule update --init --recursive`

Get involved
------------
* File a [bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon&rep_platform=all&op_sys=all)
* Read more on the [Wiki](https://github.com/mathjazz/pontoon/wiki)
* Join #pontoon on [IRC](https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon)
* Follow us on [Twitter](https://twitter.com/#!/mozillapontoon)

License
-------
This software is licensed under the [New BSD License](http://creativecommons.org/licenses/BSD/). For more information, read the file `LICENSE`.
