from __future__ import absolute_import

import pytest


@pytest.fixture
def settings_debug(settings):
    """Make the settings.DEBUG for this test"""
    settings.DEBUG = True


@pytest.yield_fixture
def request_update_translation():
    """
    Call /update/ view to push a translation/suggestion etc.
    """
    def func(client, **args):
        update_params = {
            'translation': 'approved translation',
            'plural_form': '-1',
            'ignore_check': 'true',
        }
        update_params.update(args)

        return client.post(
            '/update/',
            update_params,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
    return func
