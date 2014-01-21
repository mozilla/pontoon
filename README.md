Pontoon
=======
Pontoon enables localizers to translate websites in-place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag. [Localizer Docs](https://developer.mozilla.org/en-US/docs/Localizing_with_Pontoon).

To enable localization of your site with Pontoon, include a script to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags. [Developer Docs](https://developer.mozilla.org/en-US/docs/Implementing_Pontoon_Mozilla).

Installation
------------
Pontoon is basedon on [Playdoh](https://github.com/mozilla/playdoh). To set up Ponton, you can either use their official [documentation](http://playdoh.readthedocs.org/en/latest/) or follow the steps below.

1. Create the database:
 * `mysql -u root -e 'CREATE DATABASE pontoon CHARACTER SET utf8;'`
2. Clone this repository or your [fork](http://help.github.com/fork-a-repo/):
 * `git clone --recursive https://github.com/mathjazz/pontoon.git`
 * `cd pontoon`
3. Create and set up the [virtual environment](http://www.virtualenv.org/en/latest/index.html):
 * `virtualenv --no-site-packages env`
 * `source env/bin/activate`
 * `pip install -r requirements/compiled.txt -r requirements/prod.txt`
4. Configure the [settings](#local-settings):
 * `cp settings/local.py-dist settings/local.py`
5. Sync the database, run [migrations](http://south.readthedocs.org/) and create a super user:
 * `./manage.py syncdb --noinput`
 * `./manage.py migrate`
 * `./manage.py createsuperuser`
6. Run the development server:
 * `./manage.py runserver`
7. Finally, point your web browser to [http://localhost:8000](http://localhost:8000).

To try Pontoon with the included testpilot project, [pysvn](http://pysvn.tigris.org/project_downloads.html) is required and `/pontoon/hooks/` folder has to be linked to or placed in your web server's document root.

Local settings
--------------
 * `MICROSOFT_TRANSLATOR_API_KEY`: set to a valid [Microsoft Translator API key](http://msdn.microsoft.com/en-us/library/hh454950) to use machine translation.
 * `GOOGLE_ANALYTICS_KEY`: set to a valid [Google Analytics key](https://www.google.com/analytics/) to use Google Analytics.
 * `MOZILLIANS_API_KEY`: set to a valid [Mozillians API key](https://wiki.mozilla.org/Mozillians/API-Specification) to grant permission to Mozilla localizers.

Updates
-------
To sync your repository with upstream changes, just update the code using git:

* `git pull && git submodule sync --quiet && git submodule update --init --recursive`

To update submodules with upstream changes:

* `git submodule foreach git pull origin master`
* `git commit -am "Updating submodules with upstream changes"`

Get involved
------------
* File a [bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon&rep_platform=all&op_sys=all)
* Read more on the [Wiki](https://github.com/mathjazz/pontoon/wiki)
* Join #pontoon on [IRC](https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon)
* Follow us on [Twitter](https://twitter.com/#!/mozillapontoon)

License
-------
This software is licensed under the [New BSD License](http://creativecommons.org/licenses/BSD/). For more information, read the file `LICENSE`.
