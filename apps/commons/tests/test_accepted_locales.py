import os
import shutil

from django.conf import settings
import test_utils

import manage


class AcceptedLocalesTest(test_utils.TestCase):
    """Test lazy evaluation of locale related settings.

    Verify that some localization-related settings are lazily evaluated based 
    on the current value of the DEV variable.  Depending on the value, 
    DEV_LANGUAGES or PROD_LANGUAGES should be used.

    """
    locale = manage.path('locale')
    locale_bkp = manage.path('locale_bkp')

    @classmethod
    def setup_class(cls):
        """Create a directory structure for locale/.

        Back up the existing locale/ directory and create the following 
        hierarchy in its place:

            - locale/en-US/LC_MESSAGES
            - locale/fr/LC_MESSAGES
            - locale/templates/LC_MESSAGES
            - locale/empty_file

        Also, set PROD_LANGUAGES to ('en-US',).

        """
        if os.path.exists(cls.locale_bkp):
            raise Exception('A backup of locale/ exists at %s which might '
                            'mean that previous tests didn\'t end cleanly. '
                            'Skipping the test suite.' % cls.locale_bkp)
        cls.DEV = settings.DEV
        cls.PROD_LANGUAGES = settings.PROD_LANGUAGES
        cls.DEV_LANGUAGES = settings.DEV_LANGUAGES
        settings.PROD_LANGUAGES = ('en-US',)
        os.rename(cls.locale, cls.locale_bkp)
        for loc in ('en-US', 'fr', 'templates'):
            os.makedirs(os.path.join(cls.locale, loc, 'LC_MESSAGES'))
        open(os.path.join(cls.locale, 'empty_file'), 'w').close()

    @classmethod
    def teardown_class(cls):
        """Remove the testing locale/ dir and bring back the backup."""

        settings.DEV = cls.DEV
        settings.PROD_LANGUAGES = cls.PROD_LANGUAGES
        settings.DEV_LANGUAGES = cls.DEV_LANGUAGES
        shutil.rmtree(cls.locale)
        os.rename(cls.locale_bkp, cls.locale)

    def test_build_dev_languages(self):
        """Test that the list of dev locales is built properly.

        On dev instances, the list of accepted locales should correspond to 
        the per-locale directories in locale/.

        """
        settings.DEV = True
        assert (settings.DEV_LANGUAGES == ['en-US', 'fr'] or
                settings.DEV_LANGUAGES == ['fr', 'en-US']), \
                'DEV_LANGUAGES do not correspond to the contents of locale/.'

    def test_dev_languages(self):
        """Test the accepted locales on dev instances.

        On dev instances, allow locales defined in DEV_LANGUAGES.

        """
        settings.DEV = True
        # simulate the successful result of the DEV_LANGUAGES list 
        # comprehension defined in settings.
        settings.DEV_LANGUAGES = ['en-US', 'fr']
        assert settings.LANGUAGE_URL_MAP == {'en-us': 'en-US', 'fr': 'fr'}, \
               ('DEV is True, but DEV_LANGUAGES are not used to define the '
                'allowed locales.')

    def test_prod_languages(self):
        """Test the accepted locales on prod instances.

        On stage/prod instances, allow locales defined in PROD_LANGUAGES.

        """
        settings.DEV = False
        assert settings.LANGUAGE_URL_MAP == {'en-us': 'en-US'}, \
               ('DEV is False, but PROD_LANGUAGES are not used to define the '
                'allowed locales.')
