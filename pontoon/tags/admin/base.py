from collections import OrderedDict
from django.utils.functional import cached_property
from pontoon.base.models import (
    Locale,
    Project,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.tags.models import Tag


class Clonable:
    """Instantiated descendants of this class can be called to create a cloned
    version of the object.

    The clone will be called with attributes listed in `self.clone_kwargs` as
    kwargs. These can be overridden when creating the clone.

    """

    clone_kwargs = ()

    def __init__(self, **kwargs):
        for k in self.clone_kwargs:
            setattr(self, k, kwargs.get(k))

    def __call__(self, **kwargs):
        clone_kwargs = {k: getattr(self, k) for k in self.clone_kwargs}
        clone_kwargs.update(kwargs)
        return self.__class__(**clone_kwargs)


class FilteredDataTool(Clonable):
    """Base Tool for constructing and coalescing aggregating querysets

    Descendants of this class will filter a queryset by mapping
    self.filter_methods to methods on the class

    The data is aggregated and then cached/coalesced to the
    data property

    It can be cloned to override filtering params
    """

    default_groupby = ()
    _default_annotations = ()

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def data_manager(self):
        """Entry table through which the query is constructed"""
        raise NotImplementedError()

    @property
    def default_annotations(self):
        return OrderedDict(self._default_annotations)

    @property
    def filtered_data(self):
        """Queryset after applying filter methods"""
        data = self.data_manager.all()
        for tag_filter in self.filters:
            data = tag_filter(data)
        return data

    @property
    def filters(self):
        return [getattr(self, "filter_%s" % f) for f in self.filter_methods]

    @cached_property
    def data(self):
        """Cached and coalesed copy from get_data result"""
        return self.coalesce(self.get_data())

    def coalesce(self, data):
        """Coalesce the queryset to python data"""
        return data

    def get_annotations(self):
        """Fields to aggregate"""
        anno = self.default_annotations.copy()
        anno.update(self.annotations or {})
        return anno

    def get_data(self):
        """Get the aggregated queryset"""
        return self.filtered_data.values(*self.get_groupby()).annotate(
            **self.get_annotations()
        )

    def get_groupby(self):
        """Get groupby fields"""
        return self.groupby and [self.groupby] or self.default_groupby


class TagsDataTool(FilteredDataTool):
    """Base Data Tool for retrieving Tag data

    This class has the various Pontoon object managers as properties, which
    allows the managers to be overridden (theoretically) in a descendant class
    """

    _default_annotations = ()
    default_groupby = ("resource__tag",)
    filter_methods = ("tag", "locales", "projects")
    clone_kwargs = ("locales", "projects", "priority", "slug", "path")

    @property
    def locale_manager(self):
        return Locale.objects

    @property
    def project_manager(self):
        return Project.objects

    @property
    def resource_manager(self):
        return Resource.objects

    @property
    def tag_manager(self):
        return Tag.objects

    @property
    def translation_manager(self):
        return Translation.objects

    @property
    def tr_manager(self):
        return TranslatedResource.objects
