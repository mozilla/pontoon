Pontoon
=======
Pontoon enables localizers to translate web apps and web sites in place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag. [Localizer Docs](https://developer.mozilla.org/en-US/docs/Localizing_with_Pontoon).

To enable localization of your site with Pontoon, include a script to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags. [Developer Docs](https://developer.mozilla.org/en-US/docs/Implementing_Pontoon_Mozilla).


Installation
------------
1. [Install Docker and Compose](https://docs.docker.com/compose/install/).

2. Clone this repository or your [fork](http://help.github.com/fork-a-repo/):
   * `git clone --recursive https://github.com/mathjazz/pontoon.git`
   * `cd pontoon`

3. Build the development instance using the build script:

   ```sh
   $ ./bin/build-docker.sh
   ```

Once you've finished these steps, you should be able to start the site by
running:

```sh
$ docker-compose up
```

If you're running Docker directly (via Linux), the site should be available at
http://localhost:8000. If you're running [boot2docker](http://boot2docker.io/),
the site should be available on port 8000 at the IP output by running:

```
$ boot2docker ip
```

For [admin](http://localhost:8000/admin/) access, create admin account with:

```
`./manage.py createsuperuser`.
```


Local settings
--------------
The following settings can be set by creating a `.env` file in root directory of
your pontoon repo and adding their values:

```
MICROSOFT_TRANSLATOR_API_KEY=my-api-key
GOOGLE_ANALYTICS_KEY=google-key
```

* `MICROSOFT_TRANSLATOR_API_KEY`: set [Microsoft Translator API key](http://msdn.microsoft.com/en-us/library/hh454950) to use machine translation.

* `GOOGLE_ANALYTICS_KEY`: set [Google Analytics key](https://www.google.com/analytics/) to use Google Analytics.

* `MOZILLIANS_API_KEY`: set [Mozillians API key](https://wiki.mozilla.org/Mozillians/API-Specification) to grant permission to Mozilla localizers.


Updates
-------
To sync your repository with upstream changes, just update the code using git:

* `git pull && git submodule sync --quiet && git submodule update --init --recursive`


Get involved
------------
* File a [bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon&rep_platform=all&op_sys=all)

* Read more on the [Wiki](https://github.com/mathjazz/pontoon/wiki)

* Join #pontoon on [IRC](https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon)


Servers
-------
* [Development](https://pontoon-dev.allizom.org/)
* [Production](https://pontoon.mozilla.org/)


License
-------
This software is licensed under the [New BSD License](http://creativecommons.org/licenses/BSD/). For more information, read the file `LICENSE`.
