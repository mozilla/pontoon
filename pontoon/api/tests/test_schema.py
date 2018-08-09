import sys

from django.test import TestCase


class TestCyclicQueries(TestCase):
    def setUp(self):
        # graphql-core's ExecutionContext.report_error uses sys.excepthook to
        # print error stack traces. According to Python docs this hooks can be
        # safely customized:
        #
        #     The handling of such top-level exceptions can be customized by
        #     assigning another three-argument function to sys.excepthook.
        #
        # Cf. https://docs.python.org/2/library/sys.html#sys.excepthook
        self.excepthook_orig = sys.excepthook
        sys.excepthook = lambda *x: None

    def tearDown(self):
        sys.excepthook = self.excepthook_orig

    def test_projects(self):
        body = {
            'query': '''{
                projects {
                    name
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'data': {
                    'projects': [
                        {
                            'name': 'Pontoon Intro'
                        },
                        {
                            'name': 'Demo'
                        },
                    ]
                }
            }
        )

    def test_project_localizations(self):
        body = {
            'query': '''{
                project(slug: "pontoon-intro") {
                    localizations {
                        locale {
                            name
                        }
                    }
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'data': {
                    'project': {
                        'localizations': [
                            {
                                'locale': {
                                    'name': 'English'
                                }
                            }
                        ]
                    }
                }
            }
        )

    def test_projects_localizations_cyclic(self):
        body = {
            'query': '''{
                projects {
                    localizations {
                        locale {
                            localizations {
                                totalStrings
                            }
                        }
                    }
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cyclic queries are forbidden')

    def test_project_localizations_cyclic(self):
        body = {
            'query': '''{
                project(slug: "pontoon-intro") {
                    localizations {
                        locale {
                            localizations {
                                totalStrings
                            }
                        }
                    }
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cyclic queries are forbidden')

    def test_locales_localizations_cyclic(self):
        body = {
            'query': '''{
                locales {
                    localizations {
                        project {
                            localizations {
                                totalStrings
                            }
                        }
                    }
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cyclic queries are forbidden')

    def test_locale_localizations_cyclic(self):
        body = {
            'query': '''{
                locale(code: "en-US") {
                    localizations {
                        project {
                            localizations {
                                totalStrings
                            }
                        }
                    }
                }
            }'''
        }

        response = self.client.get('/graphql', body, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cyclic queries are forbidden')
