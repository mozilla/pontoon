# Pontoon &mdash; Mozilla's Localization Platform

### For localizers

Pontoon enables localizers to translate web apps and websites in place with
context and spatial limitations right in front of them. A full list of extracted
strings is also available, to help with strings that are hard to reach, e.g.
error messages and the `<title>` tag.

[Localizer Docs](https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/).

### For app owners

To enable localization of your site with Pontoon, include a script to overcome
cross-frame scripting, and Pontoon will autodetect strings. Or, to make the best
out of Pontoon, fully prepare your site with hooks that will mark strings for
localization and include all the necessary tags.

[Developer Docs](https://developer.mozilla.org/docs/Mozilla/Implementing_Pontoon_in_a_Mozilla_website).

## Installation

Our [installation documentation](https://mozilla-pontoon.readthedocs.io/) is available on readthedocs.

For local development, `docker` is the recommended way to go, as it is simpler and makes it easier for us to reproduce potential issues.

Do *not* use our `docker` environment for production deployment, instead use the regular setup instructions.

For quick and easy deployment using the Heroku platform, click this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Contributing

You want to help us make Pontoon better? We are very glad!

Start by [installing Pontoon locally using `docker`](https://mozilla-pontoon.readthedocs.io/en/latest/dev/install-docker.html). Once you have a working local environment, take a look at our [mentored bugs](https://wiki.mozilla.org/Webdev/GetInvolved/pontoon.mozilla.org). It is often better to start with those bugs, as they tend to be easier, and someone is committed to helping you get it done. To start working on a bug, verify that it isn't already assigned to someone else, and then ask on the bug for it to be assigned to you.

Before you start writing code, make sure to read our [contribution docs](https://mozilla-pontoon.readthedocs.io/en/latest/dev/contributing.html). It contains information on how to style code, how to run tests, how to name your commits, etc. All things you will need to know if you want your work to be merged into Pontoon!

Pontoon developers hang around in the `#pontoon` channel on [Mozilla's IRC server](https://wiki.mozilla.org/IRC). Please [join us there](https://cbe001.chat.mibbit.com/?url=irc:%2F%2Firc.mozilla.org%2Fpontoon) if you want to ask questions!

If you want to go further, you can…

* Check out development roadmap on the [wiki](http://wiki.mozilla.org/Pontoon)
* File a [bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon&rep_platform=all&op_sys=all)
* Check [existing bugs](https://bugzilla.mozilla.org/buglist.cgi?product=Webtools&component=Pontoon&resolution=---&list_id=13740920)

## Servers (used for Mozilla projects only)

* [Staging](https://mozilla-pontoon-staging.herokuapp.com/)
* [Production](https://pontoon.mozilla.org/)

## License

This software is licensed under the
[New BSD License](http://creativecommons.org/licenses/BSD/). For more
information, read [LICENSE](https://github.com/mozilla/pontoon/blob/master/LICENSE).
