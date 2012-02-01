Hook components
===============

The hook component(s) are the part of the web app that hook into the target project. As of yet, these components are only available in PHP:

* a `_w()` function that is a wrapper for gettext's `_()`. It marks strings for localization with Pontoon comments that can then be parsed by the client component. You want to use `_w()` everywhere where you used `_()` before. A simple search-and-replace can achieve that.
* `header_tags()` prints out meta tag to the target project's header telling the client that this is a Pontoon enhanced page and where is the metafile for it stored. You need to insert a call to `header_tags` to your project's header, just after <head>.
* `footer_tags()` inject javascript to the target app, to help with iframe cross-domain policy problem. You need to insert a call to `footer_tags` to your project's footer, just before </body>.