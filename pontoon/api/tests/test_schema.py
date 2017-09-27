from django.test import TestCase


class TestCyclicQueries(TestCase):

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
                        }
                    ]
                }
            }
        )

    def test_projects_localizations(self):
        body = {
            'query': '''{
                projects {
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
                    'projects': [
                        {
                            'localizations': [
                                {
                                    'locale': {
                                        'name': 'English'
                                    }
                                }
                            ]
                        }
                    ]
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
