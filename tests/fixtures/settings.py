
import pytest


@pytest.fixture
def settings_debug(settings):
    """Make the settings.DEBUG for this test"""
    settings.DEBUG = True

'''
@pytest.fixture(scope='session')
def django_db_modify_db_settings(django_db_modify_db_settings_xdist_suffix):
	from django.conf import settings
	settings.DATABASES['default']['TEST_CHARSET'] = 'utf8'
	settings.DATABASES['default']['TEST_COLLATION'] = 'tr_TR.utf8'
'''
