import pytest


@pytest.fixture
def site_matrix(factories):
    projects = factories['project'](batch=3)
    locales = factories['locale'](batch=3)
    project_locale_kwargs = []
    resource_kwargs = []
    translated_resource_kwargs = []
    for project in projects:
        resources = []
        for i in range(0, 7):
            resources.append(
                dict(project=project,
                     total_strings=(i + 5) ** 3))
        for locale in locales:
            project_locale_kwargs.append(
                dict(project=project, locale=locale))
            for i, resource in enumerate(resources):
                translated_resource_kwargs.append(
                    dict(locale=locale,
                         approved_strings=(i + 2) ** 3,
                         translated_strings=(i + 1) ** 3,
                         fuzzy_strings=i ** 3))
        resource_kwargs += resources
    project_locales = factories['project_locale'](
        batch_kwargs=project_locale_kwargs)
    resources = factories['resource'](batch_kwargs=resource_kwargs)
    for i, translated_resource in enumerate(translated_resource_kwargs):
        translated_resource.update(
            dict(resource=resources[i % len(resources)]))
    translated_resources = factories['translated_resource'](
        batch_kwargs=translated_resource_kwargs)
    return dict(
        factories=factories,
        projects=projects,
        locales=locales,
        project_locales=project_locales,
        resources=resources,
        translated_resources=translated_resources)
