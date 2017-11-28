
import pytest

from django.db.models import Max


def _factory(Model=None, instance_attrs=None,
             batch=None, batch_kwargs=None, **kwargs):
    # batch_kwargs is a list of dictionaries to pass as kwargs
    # when instantiating the objects
    batch_kwargs = batch_kwargs or {}

    # how many of the given Model to create
    batch = batch or len(batch_kwargs) or 1

    n = (Model.objects.aggregate(pk=Max('pk'))['pk'] or 0) + 1
    instances = []
    for i in range(0, batch):
        model_kwargs = kwargs.copy()
        if batch_kwargs:
            model_kwargs.update(batch_kwargs[i])
        instance = Model(**model_kwargs)
        if instance_attrs:
            instance_attrs(instance, n + i)
        instances.append(instance)
    Model.objects.bulk_create(instances)
    return instances


@pytest.fixture
def factory():
    """Generic Model factory
    provides a factory function that can be called with the following args:

    :arg django.db.models.Model `Model`: a Django model class
    :arg int `batch`: number of objects to instantiate
    :arg list `batch_kwargs`: a list of kwargs to instantiate the objects with
    :arg callable `instance_attrs`: a callback function to add additional attrs
       to each object after instantiation
    """
    return _factory


@pytest.fixture
def factories(project_factory, locale_factory, resource_factory,
              entity_factory, translated_resource_factory,
              project_locale_factory, tag_factory,
              translation_factory):
    return dict(
        project=project_factory,
        locale=locale_factory,
        resource=resource_factory,
        entity=entity_factory,
        project_locale=project_locale_factory,
        tag=tag_factory,
        translation=translation_factory,
        translated_resource=translated_resource_factory)
