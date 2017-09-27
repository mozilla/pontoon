import sys
import unittest

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import clear_url_caches


def reload_urls():
    clear_url_caches()
    reload(sys.modules[settings.ROOT_URLCONF])


class TestGraphQL(TestCase):

    body = {
        'query': '{projects{name}}'
    }

    def test_graphql_dev_get(self):
        with self.settings(DEV=True):
            response = self.client.get('/graphql', self.body,
                                       HTTP_ACCEPT="application/json")
            self.assertEqual(response.status_code, 200)

    def test_graphql_dev_post(self):
        with self.settings(DEV=True):
            response = self.client.post('/graphql', self.body,
                                        HTTP_ACCEPT="application/json")
            self.assertEqual(response.status_code, 200)

    @unittest.skip('Overriding DEV does not work.')
    def test_graphql_prod_get(self):
        with self.settings(DEV=False):
            response = self.client.get('/graphql', self.body,
                                       HTTP_ACCEPT="application/json")
            self.assertEqual(response.status_code, 200)

    @unittest.skip('Overriding DEV does not work.')
    def test_graphql_prod_post(self):
        with self.settings(DEV=False):
            response = self.client.post('/graphql', self.body,
                                        HTTP_ACCEPT="application/json")
            self.assertEqual(response.status_code, 200)


class TestGraphiQL(TestCase):

    body = {
        'query': '{projects{name}}'
    }

    def test_graphiql_dev_get(self):
        with self.settings(DEV=True):
            response = self.client.get('/graphql', self.body,
                                       HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, 200)

    def test_graphiql_dev_post(self):
        with self.settings(DEV=True):
            response = self.client.post('/graphql', self.body,
                                        HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, 200)

    @unittest.skip('Overriding DEV does not work.')
    def test_graphiql_prod_get(self):
        with self.settings(DEV=False):
            reload_urls()
            response = self.client.get('/graphql', self.body,
                                       HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, 400)

    @unittest.skip('Overriding DEV does not work.')
    def test_graphiql_prod_post(self):
        with self.settings(DEV=False):
            reload_urls()
            response = self.client.post('/graphql', self.body,
                                        HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, 400)
