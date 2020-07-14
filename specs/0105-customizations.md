- Feature Name: Customizations
- Created: 2020-07-01
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1649688

# Summary

Support for instance-specific customizations.

# Motivation

Some needs Mozilla has are not applicable to other deployments, and vice
versa. Examples could be

* Integration to Mozilla-specific services
* Integration of instance-specific data collection
* Theming and branding changes

# Feature Explanation

This feature introduces several entry points to Pontoon, which
can then be used by external code to customize an instance.
A `setup.cfg` for such code could like like

```ini
[options.entry_points]
pontoon.settings =
    my_customization=my_package.module:settings_hook
pontoon.apps =
    my_customization=my_package.module:apps_hook
```

These hooks are read via
[`pkg_resources.iter_entry_points`](https://setuptools.readthedocs.io/en/latest/pkg_resources.html#convenience-api).

## Setttings Hook

This is the `pontoon.settings` hook. It's executed as part
of the `pontoon.settings` setup afer the base phase, and allows to
modify the settings to manipulate in particular

* `INSTALLED_APPS`
* `MIDDLEWARE`

## Apps Hook

This hook is executed as part of `pontoon.base.apps`, and allows
to run code as part of app startup. We're not calling it monkeypatch
because monkeys are nice.

# Security

This is a footgun. Don't shoot yourself in the foot. Do not put
security sensitive settings in customizations.

# Deployment

To actually deploy customizations, you need to hook up them up to
the deployment pipelines.

## Heroku

On Heroku, this should be done by
[adding](https://devcenter.heroku.com/articles/using-multiple-buildpacks-for-an-app)
a [custom buildpack](https://devcenter.heroku.com/articles/buildpack-api)
after the python and nodejs buildpacks.

## Docker

Pontoon shouldn't be deployed from the
[development container](https://bugzilla.mozilla.org/show_bug.cgi?id=1513104).
Yet, if that changes, the customizations would be part of costum docker
images for the modified instances.
