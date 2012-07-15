from mock import patch
from os import path
from django.utils.importlib import import_module


class MockTrans(object):
    """
    This is a mock implementation of Trans class indjango.utils.translation.
    It is mocked so that call to gettext functions returns wrapped strings
    needed for Pontoon.
    """

    def __getattr__(self, real_name):
        from django.conf import settings
        if settings.USE_I18N:
            from django.utils.translation import trans_real as trans
            # Make sure the project's locale dir isn't in LOCALE_PATHS
            if settings.SETTINGS_MODULE is not None:
                parts = settings.SETTINGS_MODULE.split('.')
                project = import_module(parts[0])
                project_locale_path = path.normpath(
                    path.join(path.dirname(project.__file__), 'locale'))
                normalized_locale_paths = [path.normpath(locale_path)
                    for locale_path in settings.LOCALE_PATHS]
                if (path.isdir(project_locale_path) and
                        not project_locale_path in normalized_locale_paths):
                    warnings.warn("Translations in the project directory "
                                  "aren't supported anymore. Use the "
                                  "LOCALE_PATHS setting instead.",
                                  PendingDeprecationWarning)
        else:
            from django.utils.translation import trans_null as trans
        if real_name in ['gettext_noop', 'gettext', 'ngettext',
                'ugettext', 'ungettext', 'pgettext', 'npgettext']:
            setattr(self, '_' + real_name, getattr(trans, real_name))
            setattr(self, real_name, globals().get('mock_' + real_name))
        else:
            setattr(self, real_name, getattr(trans, real_name))
        return getattr(trans, real_name)

_mock_trans = MockTrans()

del MockTrans

PONTOON_WRAPPER_TAG = '<!--l10n-->'
PONTOON_PSEUDO_WRAPPER_TAG = 'LT--pontoonl10n--GT'


def _wrap_message(message):
    return  PONTOON_PSEUDO_WRAPPER_TAG + message or ''


def mock_gettext_noop(message):
    return _mock_trans._gettext(_wrap_message(message))


def mock_gettext(message):
    return _mock_trans._gettext(_wrap_message(message))


def mock_ngettext(singular, plural, number):
    return _mock_trans._ngettext(_wrap_message(singular), plural, number)


def mock_ugettext(message):
    return _mock_trans._ugettext(_wrap_message(message))


def mock_ungettext(singular, plural, number):
    return _mock_trans._ungettext(_wrap_message(singular), plural, number)


def mock_pgettext(context, message):
    return _mock_trans._pgettext(context, _wrap_message(message))


def mock_npgettext(context, singular, plural, number):
    return _mock_trans._npgettext(
            context, _wrap_message(singular), plural, number)


class PontoonMiddleware(object):
    """
    Middleware to make a Django project ready to use Pontoon.

    Preferrably, this middleware should be the last item
    in the list of middlewares for a Django project.
    """

    @patch('django.utils.translation._trans', _mock_trans)
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Monkey patch `django.utils.translation._trans` in view_func
        so that marked up strings can be wrapped by Pontoon.
        """
        return view_func(request, *view_args, **view_kwargs)

    def process_response(self, request, response):
        """
        Replace PONTOON_PSEUDO_WRAPPER_TAG with PONTOON_WRAPPER_TAG
        in rendered response.
        """
        response.content = response.content.replace(PONTOON_PSEUDO_WRAPPER_TAG,
                PONTOON_WRAPPER_TAG)
        return response
