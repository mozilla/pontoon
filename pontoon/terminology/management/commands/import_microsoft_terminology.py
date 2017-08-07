import logging
import re
import sys

import requests


from bs4 import BeautifulSoup
from defusedxml.minidom import parseString

from django.core.management.base import BaseCommand
from concurrent.futures import ProcessPoolExecutor

from retrying import retry

from pontoon.base.models import Locale
from pontoon.terminology.formats import tbx
from pontoon.terminology.models import Term
from pontoon.terminology.term_indexes import CachedDBTermIndex

log = logging.getLogger(__name__)


TERMINOLOGY_URL = 'https://www.microsoft.com/Language/en-US/Terminology.aspx'

# List of regular expressions that should exclude term from the search.
STOPWORDS = (
    r'(Windows|Xbox|Microsoft|Skype|Bing|ActiveX|BitLocker|OneDrive|OneNote)',
    r'^\s*[A-Z]+\s*[A-Z]*\s*$',
    r'^[^a-zA-z]',
    r'.*@.*'
)
STOPWORDS = map(re.compile, STOPWORDS)


def retrieve_microsoft_terms((locale_code, ms_locale_code)):
    """
    Retrieves a terminology file from Microsoft Terminology Portal and parse them.
    """
    @retry(stop_max_attempt_number=10)
    def get_tbx_contents():
        # Because it's an ASP.NET page, we have to first extract viewstate and eventvalidation
        # from the page.
        page = BeautifulSoup(requests.get(TERMINOLOGY_URL).content, 'html.parser')

        def page_find(*args, **kwargs):
            """
            Retrieve elements from a page and raise an error if something is wrong.
            """
            elements = page.find(*args, **kwargs)
            if not elements:
                raise ValueError()

            return elements

        ms_portal_form_values = {
            option['value'].split('|')[1]: option['value']
            for option in page_find('select', class_='terminology').findChildren('option')
        }
        log.info('Downloading terminology for {}'.format(locale_code))
        viewstate = page_find(id="__VIEWSTATE")['value']
        eventvalidation = page_find(id="__EVENTVALIDATION")['value']
        file_data = requests.post(
            TERMINOLOGY_URL,
            {
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$lnk_modalDownload',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATORR': '',
                '__EVENTVALIDATION': eventvalidation,
                'ctl00$mslSearchControl$txt_SearchControl': '',
                'ctl00$cbo_LocSites': '0',
                'ctl00$ContentPlaceHolder1$lb_Lang': ms_portal_form_values[ms_locale_code]
            }
        )
        file_data.raise_for_status()
        tbx_contents = file_data.content

        # If server didn't return a valid tbx contents, validation exception will cause a retry.
        parseString(tbx_contents)
        return tbx_contents


    # Replace MS locale code with Pontoon code to make it easier to import.
    tbx_contents = get_tbx_contents().replace(
        'xml:lang="{}"'.format(ms_locale_code),
        'xml:lang="{}"'.format(locale_code)
    )

    log.info('Parsing terms for {}'.format(locale_code))

    return tbx.parse_terms(tbx_contents)




class Command(BaseCommand):
    """
    Import terminology files for a set of locales or all of them in the concurrent fashion.
    """
    help = 'Import all or selected terminology files from the Microsoft Language Portal.'


    def add_arguments(self, parser):
        # A number of processes that will be spawned to download and parse terms from tbx files.
        parser.add_argument('--workers', type=int, default=10, help='A number of download workers.')

        # A list of locales to import. Fetches all files if no parameter is passed.
        parser.add_argument('locales', nargs='*', help='A list of locales to download.')


    def handle(self, *args, **options):
        locale_codes = options.get('locales')
        workers_num = options.get('workers')
        Term.objects.term_index = CachedDBTermIndex

        # A list of Pontoon locales that share terminology with Microsoft Portal.
        terminology_locales = (
            Locale
                .objects
                .filter(ms_terminology_code__isnull=False)
                .exclude(ms_terminology_code='')
                .order_by('code')
        )

        if locale_codes:
            locales_to_download = terminology_locales.filter(code__in=locale_codes)
            available_locale_codes = set(terminology_locales.values_list('code', flat=True))
            unmatched_locales = set(locale_codes) - available_locale_codes

            if unmatched_locales:
                log.error("Can't find following locales: {}".format(
                    ','.join(unmatched_locales)
                ))
                log.info('Available locales:')
                log.info(', '.join(sorted(available_locale_codes)))
                sys.exit()

        else:
            # Download all locales if no specific locale is requested.
            locales_to_download = terminology_locales

        pool = ProcessPoolExecutor(workers_num)
        terms = {}
        try:
            terms_per_locale = pool.map(
                retrieve_microsoft_terms,
                [
                    (locale.code, locale.ms_terminology_code)
                    for locale in locales_to_download
                ]
            )
        except ValueError:
            # During testing I noticed that MS Terminology Portal returns 50x errors
            # or just ''.
            log.error("Couldn't load data from server. Please, try again later.")
            sys.exit(-1)

        # Merge all terms imported from different locale files
        for locale_terms in terms_per_locale:
            for term in locale_terms:
                if term.term_id in terms:
                    terms[term.term_id].translations.update(term.translations)
                else:
                    terms[term.term_id] = term


        log.info('Loaded %s terms.', (len(terms)))
        log.info('Importing terms to Pontoon')

        # Filter terms with MS specific phrases
        cleaned_terms = {k: v for k, v in terms.items() if not self.ms_term(v.source_text, v.description)}

        log.info('Removed %s MS Terms.', len(terms) - len(cleaned_terms))
        Term.objects.import_tbx_terms(cleaned_terms)

    def ms_term(self, source_text, description):
        """
        Determines if term's text/description contains any MS specific contents.
        """
        for rule in STOPWORDS:
            if rule.search(source_text) or rule.search(description):
                return True
        return False
